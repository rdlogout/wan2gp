# Copyright 2024-2025 The Alibaba Wan Team Authors. All rights reserved.
import gc
import logging
import math
import os
import random
import sys
import types
from contextlib import contextmanager
from functools import partial
from mmgp import offload
import torch
import torch.nn as nn
import torch.cuda.amp as amp
import torch.distributed as dist
from tqdm import tqdm
from PIL import Image
import torchvision.transforms.functional as TF
import torch.nn.functional as F
from .distributed.fsdp import shard_model
from .modules.model import WanModel
from .modules.t5 import T5EncoderModel
from .modules.vae import WanVAE
from .utils.fm_solvers import (FlowDPMSolverMultistepScheduler,
                               get_sampling_sigmas, retrieve_timesteps)
from .utils.fm_solvers_unipc import FlowUniPCMultistepScheduler
from wan.modules.posemb_layers import get_rotary_pos_embed
from .utils.vace_preprocessor import VaceVideoProcessor
from wan.utils.basic_flowmatch import FlowMatchScheduler
from wan.utils.utils import get_outpainting_frame_location
from wgp import update_loras_slists

def optimized_scale(positive_flat, negative_flat):

    # Calculate dot production
    dot_product = torch.sum(positive_flat * negative_flat, dim=1, keepdim=True)

    # Squared norm of uncondition
    squared_norm = torch.sum(negative_flat ** 2, dim=1, keepdim=True) + 1e-8

    # st_star = v_cond^T * v_uncond / ||v_uncond||^2
    st_star = dot_product / squared_norm
    
    return st_star


class WanT2V:

    def __init__(
        self,
        config,
        checkpoint_dir,
        rank=0,
        model_filename = None,
        model_type = None, 
        base_model_type = None,
        text_encoder_filename = None,
        quantizeTransformer = False,
        save_quantized = False,
        dtype = torch.bfloat16,
        VAE_dtype = torch.float32,
        mixed_precision_transformer = False
    ):
        self.device = torch.device(f"cuda")
        self.config = config
        self.rank = rank
        self.dtype = dtype
        self.num_train_timesteps = config.num_train_timesteps
        self.param_dtype = config.param_dtype

        self.text_encoder = T5EncoderModel(
            text_len=config.text_len,
            dtype=config.t5_dtype,
            device=torch.device('cpu'),
            checkpoint_path=text_encoder_filename,
            tokenizer_path=os.path.join(checkpoint_dir, config.t5_tokenizer),
            shard_fn= None)

        self.vae_stride = config.vae_stride
        self.patch_size = config.patch_size 
        
        self.vae = WanVAE(
            vae_pth=os.path.join(checkpoint_dir, config.vae_checkpoint), dtype= VAE_dtype,
            device=self.device)
        
        logging.info(f"Creating WanModel from {model_filename[-1]}")
        from mmgp import offload
        # model_filename = "c:/temp/vace1.3/diffusion_pytorch_model.safetensors"
        # model_filename = "Vacefusionix_quanto_fp16_int8.safetensors"
        # model_filename = "c:/temp/t2v/diffusion_pytorch_model-00001-of-00006.safetensors"
        # config_filename= "c:/temp/t2v/t2v.json"
        base_config_file = f"configs/{base_model_type}.json"
        forcedConfigPath = base_config_file if len(model_filename) > 1 else None
        self.model = offload.fast_load_transformers_model(model_filename, modelClass=WanModel,do_quantize= quantizeTransformer and not save_quantized, writable_tensors= False, defaultConfigPath=base_config_file , forcedConfigPath= forcedConfigPath)
        # offload.load_model_data(self.model, "c:/temp/Phantom-Wan-1.3B.pth")
        # self.model.to(torch.bfloat16)
        # self.model.cpu()
        self.model.lock_layers_dtypes(torch.float32 if mixed_precision_transformer else dtype)
        # dtype = torch.bfloat16
        # offload.load_model_data(self.model, "ckpts/Wan14BT2VFusioniX_fp16.safetensors")
        offload.change_dtype(self.model, dtype, True)
        # offload.save_model(self.model, "wan2.1_selforcing_fp16.safetensors", config_file_path=base_config_file)
        # offload.save_model(self.model, "wan2.1_text2video_14B_mbf16.safetensors", config_file_path=base_config_file)
        # offload.save_model(self.model, "wan2.1_text2video_14B_quanto_mfp16_int8.safetensors", do_quantize=True, config_file_path=base_config_file)
        self.model.eval().requires_grad_(False)
        if save_quantized:
            from wgp import save_quantized_model
            save_quantized_model(self.model, model_type, model_filename[1 if base_model_type=="fantasy" else 0], dtype, base_config_file)

        self.sample_neg_prompt = config.sample_neg_prompt

        if base_model_type in ["vace_14B", "vace_1.3B"]:
            self.vid_proc = VaceVideoProcessor(downsample=tuple([x * y for x, y in zip(config.vae_stride, self.patch_size)]),
                                            min_area=480*832,
                                            max_area=480*832,
                                            min_fps=config.sample_fps,
                                            max_fps=config.sample_fps,
                                            zero_start=True,
                                            seq_len=32760,
                                            keep_last=True)

            self.adapt_vace_model()

    def vace_encode_frames(self, frames, ref_images, masks=None, tile_size = 0, overlapped_latents = None):
        if ref_images is None:
            ref_images = [None] * len(frames)
        else:
            assert len(frames) == len(ref_images)

        if masks is None:
            latents = self.vae.encode(frames, tile_size = tile_size)
        else:
            inactive = [i * (1 - m) + 0 * m for i, m in zip(frames, masks)]
            reactive = [i * m + 0 * (1 - m) for i, m in zip(frames, masks)]
            inactive = self.vae.encode(inactive, tile_size = tile_size)

            if overlapped_latents  != None and False : 
                # inactive[0][:, 0:1] = self.vae.encode([frames[0][:, 0:1]], tile_size = tile_size)[0] # redundant
                for t in inactive:
                    t[:, 1:overlapped_latents.shape[1] + 1] = overlapped_latents

            reactive = self.vae.encode(reactive, tile_size = tile_size)
            latents = [torch.cat((u, c), dim=0) for u, c in zip(inactive, reactive)]

        cat_latents = []
        for latent, refs in zip(latents, ref_images):
            if refs is not None:
                if masks is None:
                    ref_latent = self.vae.encode(refs, tile_size = tile_size)
                else:
                    ref_latent = self.vae.encode(refs, tile_size = tile_size)
                    ref_latent = [torch.cat((u, torch.zeros_like(u)), dim=0) for u in ref_latent]
                assert all([x.shape[1] == 1 for x in ref_latent])
                latent = torch.cat([*ref_latent, latent], dim=1)
            cat_latents.append(latent)
        return cat_latents

    def vace_encode_masks(self, masks, ref_images=None):
        if ref_images is None:
            ref_images = [None] * len(masks)
        else:
            assert len(masks) == len(ref_images)

        result_masks = []
        for mask, refs in zip(masks, ref_images):
            c, depth, height, width = mask.shape
            new_depth = int((depth + 3) // self.vae_stride[0]) # nb latents token without (ref tokens not included)
            height = 2 * (int(height) // (self.vae_stride[1] * 2))
            width = 2 * (int(width) // (self.vae_stride[2] * 2))

            # reshape
            mask = mask[0, :, :, :]
            mask = mask.view(
                depth, height, self.vae_stride[1], width, self.vae_stride[1]
            )  # depth, height, 8, width, 8
            mask = mask.permute(2, 4, 0, 1, 3)  # 8, 8, depth, height, width
            mask = mask.reshape(
                self.vae_stride[1] * self.vae_stride[2], depth, height, width
            )  # 8*8, depth, height, width

            # interpolation
            mask = F.interpolate(mask.unsqueeze(0), size=(new_depth, height, width), mode='nearest-exact').squeeze(0)

            if refs is not None:
                length = len(refs)
                mask_pad = torch.zeros_like(mask[:, :length, :, :])
                mask = torch.cat((mask_pad, mask), dim=1)
            result_masks.append(mask)
        return result_masks

    def vace_latent(self, z, m):
        return [torch.cat([zz, mm], dim=0) for zz, mm in zip(z, m)]

    def fit_image_into_canvas(self, ref_img, image_size, canvas_tf_bg, device, fill_max = False, outpainting_dims = None, return_mask = False):
        from wan.utils.utils import save_image
        ref_width, ref_height = ref_img.size
        if (ref_height, ref_width) == image_size and outpainting_dims  == None:
            ref_img = TF.to_tensor(ref_img).sub_(0.5).div_(0.5).unsqueeze(1)
            canvas = torch.zeros_like(ref_img) if return_mask else None
        else:
            if outpainting_dims != None:
                final_height, final_width = image_size
                canvas_height, canvas_width, margin_top, margin_left =   get_outpainting_frame_location(final_height, final_width,  outpainting_dims, 8)        
            else:
                canvas_height, canvas_width = image_size
            scale = min(canvas_height / ref_height, canvas_width / ref_width)
            new_height = int(ref_height * scale)
            new_width = int(ref_width * scale)
            if fill_max  and (canvas_height - new_height) < 16:
                new_height = canvas_height
            if fill_max  and (canvas_width - new_width) < 16:
                new_width = canvas_width
            top = (canvas_height - new_height) // 2
            left = (canvas_width - new_width) // 2
            ref_img = ref_img.resize((new_width, new_height), resample=Image.Resampling.LANCZOS) 
            ref_img = TF.to_tensor(ref_img).sub_(0.5).div_(0.5).unsqueeze(1)
            if outpainting_dims != None:
                canvas = torch.full((3, 1, final_height, final_width), canvas_tf_bg, dtype= torch.float, device=device) # [-1, 1]
                canvas[:, :, margin_top + top:margin_top + top + new_height, margin_left + left:margin_left + left + new_width] = ref_img 
            else:
                canvas = torch.full((3, 1, canvas_height, canvas_width), canvas_tf_bg, dtype= torch.float, device=device) # [-1, 1]
                canvas[:, :, top:top + new_height, left:left + new_width] = ref_img 
            ref_img = canvas
            canvas = None
            if return_mask:
                if outpainting_dims != None:
                    canvas = torch.ones((3, 1, final_height, final_width), dtype= torch.float, device=device) # [-1, 1]
                    canvas[:, :, margin_top + top:margin_top + top + new_height, margin_left + left:margin_left + left + new_width] = 0
                else:
                    canvas = torch.ones((3, 1, canvas_height, canvas_width), dtype= torch.float, device=device) # [-1, 1]
                    canvas[:, :, top:top + new_height, left:left + new_width] = 0
                canvas = canvas.to(device)
        return ref_img.to(device), canvas

    def prepare_source(self, src_video, src_mask, src_ref_images, total_frames, image_size,  device, keep_video_guide_frames= [], start_frame = 0,  fit_into_canvas = None, pre_src_video = None, inject_frames = [], outpainting_dims = None, any_background_ref = False):
        image_sizes = []
        trim_video_guide = len(keep_video_guide_frames)
        def conv_tensor(t, device):
            return t.float().div_(127.5).add_(-1).permute(3, 0, 1, 2).to(device)

        for i, (sub_src_video, sub_src_mask, sub_pre_src_video) in enumerate(zip(src_video, src_mask,pre_src_video)):
            prepend_count = 0 if sub_pre_src_video == None else sub_pre_src_video.shape[1]
            num_frames = total_frames - prepend_count            
            num_frames = min(num_frames, trim_video_guide) if trim_video_guide > 0 and sub_src_video != None else num_frames
            if sub_src_mask is not None and sub_src_video is not None:
                src_video[i] = conv_tensor(sub_src_video[:num_frames], device)
                src_mask[i] = conv_tensor(sub_src_mask[:num_frames], device)
                # src_video is [-1, 1] (at this function output), 0 = inpainting area (in fact 127  in [0, 255])
                # src_mask is [-1, 1] (at this function output), 0 = preserve original video (in fact 127  in [0, 255]) and 1 = Inpainting (in fact 255  in [0, 255])
                if prepend_count > 0:
                    src_video[i] =  torch.cat( [sub_pre_src_video, src_video[i]], dim=1)
                    src_mask[i] =  torch.cat( [torch.full_like(sub_pre_src_video, -1.0), src_mask[i]] ,1)
                src_video_shape = src_video[i].shape
                if src_video_shape[1] != total_frames:
                    src_video[i] =  torch.cat( [src_video[i], src_video[i].new_zeros(src_video_shape[0], total_frames -src_video_shape[1], *src_video_shape[-2:])], dim=1)
                    src_mask[i] =  torch.cat( [src_mask[i], src_mask[i].new_ones(src_video_shape[0], total_frames -src_video_shape[1], *src_video_shape[-2:])], dim=1)
                src_mask[i] = torch.clamp((src_mask[i][:, :, :, :] + 1) / 2, min=0, max=1)
                image_sizes.append(src_video[i].shape[2:])
            elif sub_src_video is None:
                if prepend_count > 0:
                    src_video[i] =  torch.cat( [sub_pre_src_video, torch.zeros((3, num_frames, image_size[0], image_size[1]), device=device)], dim=1)
                    src_mask[i] =  torch.cat( [torch.zeros_like(sub_pre_src_video), torch.ones((3, num_frames, image_size[0], image_size[1]), device=device)] ,1)
                else:
                    src_video[i] = torch.zeros((3, total_frames, image_size[0], image_size[1]), device=device)
                    src_mask[i] = torch.ones_like(src_video[i], device=device)
                image_sizes.append(image_size)
            else:
                src_video[i] = conv_tensor(sub_src_video[:num_frames], device)
                src_mask[i] = torch.ones_like(src_video[i], device=device)
                if prepend_count > 0:
                    src_video[i] =  torch.cat( [sub_pre_src_video, src_video[i]], dim=1)
                    src_mask[i] =  torch.cat( [torch.zeros_like(sub_pre_src_video), src_mask[i]] ,1)
                src_video_shape = src_video[i].shape
                if src_video_shape[1] != total_frames:
                    src_video[i] =  torch.cat( [src_video[i], src_video[i].new_zeros(src_video_shape[0], total_frames -src_video_shape[1], *src_video_shape[-2:])], dim=1)
                    src_mask[i] =  torch.cat( [src_mask[i], src_mask[i].new_ones(src_video_shape[0], total_frames -src_video_shape[1], *src_video_shape[-2:])], dim=1)
                image_sizes.append(src_video[i].shape[2:])
            for k, keep in enumerate(keep_video_guide_frames):
                if not keep:
                    src_video[i][:, k:k+1] = 0
                    src_mask[i][:, k:k+1] = 1

            for k, frame in enumerate(inject_frames):
                if frame != None:
                    src_video[i][:, k:k+1], src_mask[i][:, k:k+1] = self.fit_image_into_canvas(frame, image_size, 0, device, True, outpainting_dims, return_mask= True)
        

        self.background_mask = None
        for i, ref_images in enumerate(src_ref_images):
            if ref_images is not None:
                image_size = image_sizes[i]
                for j, ref_img in enumerate(ref_images):
                    if ref_img is not None and not torch.is_tensor(ref_img):
                        if j==0 and any_background_ref:
                            if self.background_mask == None: self.background_mask = [None] * len(src_ref_images) 
                            src_ref_images[i][j], self.background_mask[i] = self.fit_image_into_canvas(ref_img, image_size, 0, device, True, outpainting_dims, return_mask= True)
                        else:
                            src_ref_images[i][j], _ = self.fit_image_into_canvas(ref_img, image_size, 1, device)
        if self.background_mask != None:
            self.background_mask = [ item if item != None else self.background_mask[0] for item in self.background_mask ] # deplicate background mask with double control net since first controlnet image ref modifed by ref
        return src_video, src_mask, src_ref_images

    def decode_latent(self, zs, ref_images=None, tile_size= 0 ):
        if ref_images is None:
            ref_images = [None] * len(zs)
        # else:
        #     assert len(zs) == len(ref_images)

        trimed_zs = []
        for z, refs in zip(zs, ref_images):
            if refs is not None:
                z = z[:, len(refs):, :, :]
            trimed_zs.append(z)

        return self.vae.decode(trimed_zs, tile_size= tile_size)

    def get_vae_latents(self, ref_images, device, tile_size= 0):
        ref_vae_latents = []
        for ref_image in ref_images:
            ref_image = TF.to_tensor(ref_image).sub_(0.5).div_(0.5).to(self.device)
            img_vae_latent = self.vae.encode([ref_image.unsqueeze(1)], tile_size= tile_size)
            ref_vae_latents.append(img_vae_latent[0])
                    
        return torch.cat(ref_vae_latents, dim=1)
        
    def generate(self,
                input_prompt,
                input_frames= None,
                input_masks = None,
                input_ref_images = None,      
                input_video=None,
                denoising_strength = 1.0,
                target_camera=None,                  
                context_scale=None,
                width = 1280,
                height = 720,
                fit_into_canvas = True,
                frame_num=81,
                shift=5.0,
                sample_solver='unipc',
                sampling_steps=50,
                guide_scale=5.0,
                n_prompt="",
                seed=-1,
                offload_model=True,
                callback = None,
                enable_RIFLEx = None,
                VAE_tile_size = 0,
                joint_pass = False,
                slg_layers = None,
                slg_start = 0.0,
                slg_end = 1.0,
                cfg_star_switch = True,
                cfg_zero_step = 5,
                overlapped_latents  = None,
                return_latent_slice = None,
                overlap_noise = 0,
                conditioning_latents_size = 0,
                keep_frames_parsed = [],
                model_filename = None,
                model_type = None,
                loras_slists = None,
                **bbargs
                ):
        r"""
        Generates video frames from text prompt using diffusion process.

        Args:
            input_prompt (`str`):
                Text prompt for content generation
            size (tupele[`int`], *optional*, defaults to (1280,720)):
                Controls video resolution, (width,height).
            frame_num (`int`, *optional*, defaults to 81):
                How many frames to sample from a video. The number should be 4n+1
            shift (`float`, *optional*, defaults to 5.0):
                Noise schedule shift parameter. Affects temporal dynamics
            sample_solver (`str`, *optional*, defaults to 'unipc'):
                Solver used to sample the video.
            sampling_steps (`int`, *optional*, defaults to 40):
                Number of diffusion sampling steps. Higher values improve quality but slow generation
            guide_scale (`float`, *optional*, defaults 5.0):
                Classifier-free guidance scale. Controls prompt adherence vs. creativity
            n_prompt (`str`, *optional*, defaults to ""):
                Negative prompt for content exclusion. If not given, use `config.sample_neg_prompt`
            seed (`int`, *optional*, defaults to -1):
                Random seed for noise generation. If -1, use random seed.
            offload_model (`bool`, *optional*, defaults to True):
                If True, offloads models to CPU during generation to save VRAM

        Returns:
            torch.Tensor:
                Generated video frames tensor. Dimensions: (C, N H, W) where:
                - C: Color channels (3 for RGB)
                - N: Number of frames (81)
                - H: Frame height (from size)
                - W: Frame width from size)
        """
        # preprocess
        vace = "Vace" in model_filename

        if n_prompt == "":
            n_prompt = self.sample_neg_prompt
        seed = seed if seed >= 0 else random.randint(0, sys.maxsize)
        seed_g = torch.Generator(device=self.device)
        seed_g.manual_seed(seed)

        if self._interrupt:
            return None
        context = self.text_encoder([input_prompt], self.device)[0]
        context_null = self.text_encoder([n_prompt], self.device)[0]
        context = context.to(self.dtype)
        context_null = context_null.to(self.dtype)
        input_ref_images_neg = None
        phantom = False

        if target_camera != None:
            width = input_video.shape[2]
            height = input_video.shape[1]
            input_video = input_video.to(dtype=self.dtype , device=self.device)
            input_video = input_video.permute(3, 0, 1, 2).div_(127.5).sub_(1.)            
            source_latents = self.vae.encode([input_video])[0] #.to(dtype=self.dtype, device=self.device)
            del input_video
            # Process target camera (recammaster)
            from wan.utils.cammmaster_tools import get_camera_embedding
            cam_emb = get_camera_embedding(target_camera)       
            cam_emb = cam_emb.to(dtype=self.dtype, device=self.device)

        if denoising_strength < 1. and input_frames != None:
            height, width = input_frames.shape[-2:]
            source_latents = self.vae.encode([input_frames])[0]

        if vace :
            # vace context encode
            input_frames = [u.to(self.device) for u in input_frames]
            input_ref_images = [ None if u == None else [v.to(self.device) for v in u]  for u in input_ref_images]
            input_masks = [u.to(self.device) for u in input_masks]
            if self.background_mask != None: self.background_mask = [m.to(self.device) for m in self.background_mask]
            previous_latents = None
            # if overlapped_latents != None:
                # input_ref_images = [u[-1:] for u in input_ref_images]
            z0 = self.vace_encode_frames(input_frames, input_ref_images, masks=input_masks, tile_size = VAE_tile_size, overlapped_latents = overlapped_latents )
            m0 = self.vace_encode_masks(input_masks, input_ref_images)
            if self.background_mask != None:
                zbg = self.vace_encode_frames([ref_img[0] for ref_img in input_ref_images], None, masks=self.background_mask, tile_size = VAE_tile_size )
                mbg = self.vace_encode_masks(self.background_mask, None)
                for zz0, mm0, zzbg, mmbg in zip(z0, m0, zbg, mbg):
                    zz0[:, 0:1] = zzbg
                    mm0[:, 0:1] = mmbg

                self.background_mask = zz0 = mm0 = zzbg = mmbg = None
            z = self.vace_latent(z0, m0)

            target_shape = list(z0[0].shape)
            target_shape[0] = int(target_shape[0] / 2)
        else:
            if input_ref_images != None: # Phantom Ref images
                phantom = True
                input_ref_images = self.get_vae_latents(input_ref_images, self.device)
                input_ref_images_neg = torch.zeros_like(input_ref_images)
            F = frame_num
            target_shape = (self.vae.model.z_dim, (F - 1) // self.vae_stride[0] + 1 + (input_ref_images.shape[1] if input_ref_images != None else 0),
                            height // self.vae_stride[1],
                            width // self.vae_stride[2])

        seq_len = math.ceil((target_shape[2] * target_shape[3]) /
                            (self.patch_size[1] * self.patch_size[2]) *
                            target_shape[1]) 

        if self._interrupt:
            return None

        noise = [ torch.randn( *target_shape, dtype=torch.float32, device=self.device, generator=seed_g) ]

        # evaluation mode

        if sample_solver == 'causvid':
            sample_scheduler = FlowMatchScheduler(num_inference_steps=sampling_steps, shift=shift, sigma_min=0, extra_one_step=True)
            timesteps = torch.tensor([1000, 934, 862, 756, 603, 410, 250, 140, 74])[:sampling_steps].to(self.device)
            sample_scheduler.timesteps =timesteps
            sample_scheduler.sigmas = torch.cat([sample_scheduler.timesteps / 1000, torch.tensor([0.], device=self.device)])
        elif sample_solver == 'unipc' or sample_solver == "":
            sample_scheduler = FlowUniPCMultistepScheduler( num_train_timesteps=self.num_train_timesteps, shift=1, use_dynamic_shifting=False)
            sample_scheduler.set_timesteps( sampling_steps, device=self.device, shift=shift)
            
            timesteps = sample_scheduler.timesteps
        elif sample_solver == 'dpm++':
            sample_scheduler = FlowDPMSolverMultistepScheduler(
                num_train_timesteps=self.num_train_timesteps,
                shift=1,
                use_dynamic_shifting=False)
            sampling_sigmas = get_sampling_sigmas(sampling_steps, shift)
            timesteps, _ = retrieve_timesteps(
                sample_scheduler,
                device=self.device,
                sigmas=sampling_sigmas)
        else:
            raise NotImplementedError(f"Unsupported Scheduler {sample_solver}")


        # sample videos
        latents = noise[0]
        del noise

        injection_denoising_step = 0
        inject_from_start = False
        if denoising_strength < 1 and input_frames != None:
            if len(keep_frames_parsed) == 0  or all(keep_frames_parsed): keep_frames_parsed = [] 
            injection_denoising_step = int(sampling_steps * (1. - denoising_strength) )
            latent_keep_frames = []
            if source_latents.shape[1] < latents.shape[1] or len(keep_frames_parsed) > 0:
                inject_from_start = True
                if len(keep_frames_parsed) >0 :
                    latent_keep_frames =[keep_frames_parsed[0]]
                    for i in range(1, len(keep_frames_parsed), 4):
                        latent_keep_frames.append(all(keep_frames_parsed[i:i+4]))
            else:
                timesteps = timesteps[injection_denoising_step:]
                if hasattr(sample_scheduler, "timesteps"): sample_scheduler.timesteps = timesteps
                if hasattr(sample_scheduler, "sigmas"): sample_scheduler.sigmas= sample_scheduler.sigmas[injection_denoising_step:]
                injection_denoising_step = 0


        batch_size = 1
        if target_camera != None:
            shape = list(latents.shape[1:])
            shape[0] *= 2
            freqs = get_rotary_pos_embed(shape, enable_RIFLEx= False) 
        else:
            freqs = get_rotary_pos_embed(latents.shape[1:], enable_RIFLEx= enable_RIFLEx) 

        kwargs = {'freqs': freqs, 'pipeline': self, 'callback': callback}

        if target_camera != None:
            kwargs.update({'cam_emb': cam_emb})

        if vace:
            ref_images_count = len(input_ref_images[0]) if input_ref_images != None and input_ref_images[0] != None else 0
            context_scale = context_scale if context_scale != None else [1.0] * len(z)
            kwargs.update({'vace_context' : z, 'vace_context_scale' : context_scale})
            if overlapped_latents != None :
                overlapped_latents_size = overlapped_latents.shape[1] + 1
                # overlapped_latents_size = 3
                z_reactive = [  zz[0:16, 0:overlapped_latents_size + ref_images_count].clone() for zz in z]

        cache_type = self.model.enable_cache 
        if cache_type != None:
            x_count = 3 if phantom else 2
            self.model.previous_residual = [None] * x_count
            if cache_type == "tea":
                self.model.compute_teacache_threshold(self.model.cache_start_step, timesteps, self.model.cache_multiplier)
            else: 
                self.model.compute_magcache_threshold(self.model.cache_start_step, timesteps, self.model.cache_multiplier)
                self.model.accumulated_err, self.model.accumulated_steps, self.model.accumulated_ratio  = [0.0] * x_count, [0] * x_count, [1.0] * x_count
                self.model.one_for_all = x_count > 2
        if callback != None:
            callback(-1, None, True)

        offload.shared_state["_chipmunk"] =  False
        chipmunk = offload.shared_state.get("_chipmunk", False)        
        if chipmunk:
            self.model.setup_chipmunk()

        updated_num_steps=  len(timesteps)
        if callback != None:
            update_loras_slists(self.model, loras_slists, updated_num_steps)
            callback(-1, None, True, override_num_inference_steps = updated_num_steps)

        scheduler_kwargs = {} if isinstance(sample_scheduler, FlowMatchScheduler) else {"generator": seed_g}

        for i, t in enumerate(tqdm(timesteps)):
            timestep = [t]

            if denoising_strength < 1 and input_frames != None and i <= injection_denoising_step:
                sigma = t / 1000
                noise = torch.randn( *target_shape, dtype=torch.float32, device=self.device, generator=seed_g)
                if inject_from_start:
                    new_latents = latents.clone()
                    new_latents[:, :source_latents.shape[1] ] = noise[:, :source_latents.shape[1] ] * sigma + (1 - sigma) * source_latents
                    for latent_no, keep_latent in enumerate(latent_keep_frames):
                        if not keep_latent:
                            new_latents[:, latent_no:latent_no+1 ] = latents[:, latent_no:latent_no+1]
                    latents = new_latents
                    new_latents = None
                else:
                    latents = noise * sigma + (1 - sigma) * source_latents
                noise = None

            if overlapped_latents != None :
                overlap_noise_factor = overlap_noise / 1000 
                latent_noise_factor = t / 1000
                for zz, zz_r, ll in zip(z, z_reactive, [latents, None]): # extra None for second control net
                    zz[0:16, ref_images_count:overlapped_latents_size + ref_images_count]   = zz_r[:, ref_images_count:]  * (1.0 - overlap_noise_factor) + torch.randn_like(zz_r[:, ref_images_count:] ) * overlap_noise_factor 
                    if ll != None:
                        ll[:, 0:overlapped_latents_size + ref_images_count]   = zz_r  * (1.0 - latent_noise_factor) + torch.randn_like(zz_r ) * latent_noise_factor 

            if target_camera != None:
                latent_model_input = torch.cat([latents, source_latents], dim=1)
            else:
                latent_model_input = latents
            kwargs["slg_layers"] = slg_layers if int(slg_start * sampling_steps) <= i < int(slg_end * sampling_steps) else None

            offload.set_step_no_for_lora(self.model, i)
            timestep = torch.stack(timestep)
            kwargs["current_step"] = i 
            kwargs["t"] = timestep 
            if guide_scale == 1:
                noise_pred = self.model( [latent_model_input], x_id = 0, context = [context], **kwargs)[0]
                if self._interrupt:
                    return None
            elif joint_pass:
                if phantom:
                    pos_it, pos_i, neg = self.model(
                         [ torch.cat([latent_model_input[:,:-input_ref_images.shape[1]], input_ref_images], dim=1) ] * 2 +
                         [ torch.cat([latent_model_input[:,:-input_ref_images_neg.shape[1]], input_ref_images_neg], dim=1)],
                        context = [context, context_null, context_null], **kwargs)
                else:
                    noise_pred_cond, noise_pred_uncond = self.model(
                        [latent_model_input, latent_model_input], context = [context, context_null], **kwargs)
                if self._interrupt:
                    return None
            else:
                if phantom:
                    pos_it = self.model(
                        [ torch.cat([latent_model_input[:,:-input_ref_images.shape[1]], input_ref_images], dim=1) ], x_id = 0, context = [context], **kwargs
                        )[0]
                    if self._interrupt:
                        return None               
                    pos_i = self.model(
                        [ torch.cat([latent_model_input[:,:-input_ref_images.shape[1]], input_ref_images], dim=1) ], x_id = 1, context = [context_null],**kwargs
                        )[0]
                    if self._interrupt:
                        return None               
                    neg = self.model(
                           [ torch.cat([latent_model_input[:,:-input_ref_images_neg.shape[1]], input_ref_images_neg], dim=1) ], x_id = 2, context = [context_null], **kwargs
                        )[0]
                    if self._interrupt:
                        return None               
                else:
                    noise_pred_cond = self.model(
                        [latent_model_input], x_id = 0, context = [context], **kwargs)[0]
                    if self._interrupt:
                        return None               
                    noise_pred_uncond = self.model(
                        [latent_model_input], x_id = 1, context = [context_null], **kwargs)[0]
                    if self._interrupt:
                        return None

            # del latent_model_input

            # CFG Zero *. Thanks to https://github.com/WeichenFan/CFG-Zero-star/
            if guide_scale == 1:
                pass
            elif phantom:
                guide_scale_img= 5.0
                guide_scale_text= guide_scale #7.5                
                noise_pred = neg + guide_scale_img * (pos_i - neg) + guide_scale_text * (pos_it - pos_i)
            else:
                noise_pred_text = noise_pred_cond
                if cfg_star_switch:
                    positive_flat = noise_pred_text.view(batch_size, -1)  
                    negative_flat = noise_pred_uncond.view(batch_size, -1)  

                    alpha = optimized_scale(positive_flat,negative_flat)
                    alpha = alpha.view(batch_size, 1, 1, 1)

                    if (i <= cfg_zero_step):
                        noise_pred = noise_pred_text*0. # it would be faster not to compute noise_pred...
                    else:
                        noise_pred_uncond *= alpha
                noise_pred = noise_pred_uncond + guide_scale * (noise_pred_text - noise_pred_uncond)            
            noise_pred_uncond, noise_pred_cond, noise_pred_text, pos_it, pos_i, neg  = None, None, None, None, None, None
            temp_x0 = sample_scheduler.step(
                noise_pred[:, :target_shape[1]].unsqueeze(0),
                t,
                latents.unsqueeze(0),
                # return_dict=False,
                **scheduler_kwargs)[0]
            latents = temp_x0.squeeze(0)
            del temp_x0

            if callback is not None:
                callback(i, latents, False)         

        x0 = [latents]

        if chipmunk:
            self.model.release_chipmunk() # need to add it at every exit when in prof

        if return_latent_slice != None:
            if overlapped_latents != None:
                # latents [:, 1:] = self.toto
                for zz, zz_r, ll  in zip(z, z_reactive, [latents]):
                    ll[:, 0:overlapped_latents_size + ref_images_count]   = zz_r 

            latent_slice = latents[:, return_latent_slice].clone()
        if input_frames == None:
            if phantom:
                # phantom post processing
                x0 = [x0_[:,:-input_ref_images.shape[1]] for x0_ in x0]
            videos = self.vae.decode(x0, VAE_tile_size)
        else:
            # vace post processing
            videos = self.decode_latent(x0, input_ref_images, VAE_tile_size)
        if return_latent_slice != None:
            return { "x" : videos[0], "latent_slice" : latent_slice }
        return videos[0]

    def adapt_vace_model(self):
        model = self.model
        modules_dict= { k: m for k, m in model.named_modules()}
        for model_layer, vace_layer in model.vace_layers_mapping.items():
            module = modules_dict[f"vace_blocks.{vace_layer}"]
            target = modules_dict[f"blocks.{model_layer}"]
            setattr(target, "vace", module )
        delattr(model, "vace_blocks")
