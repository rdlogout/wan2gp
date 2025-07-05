# WanGP

-----
<p align="center">
<b>WanGP by DeepBeepMeep : The best Open Source Video Generative Models Accessible to the GPU Poor</b>
</p>

WanGP supports the Wan (and derived models), Hunyuan Video and LTV Video models with:
- Low VRAM requirements (as low as 6 GB of VRAM is sufficient for certain models)
- Support for old GPUs (RTX 10XX, 20xx, ...)
- Very Fast on the latest GPUs
- Easy to use Full Web based interface
- Auto download of the required model adapted to your specific architecture
- Tools integrated to facilitate Video Generation : Mask Editor, Prompt Enhancer, Temporal and Spatial Generation, MMAudio, Vew
- Loras Support to customize each model
- Queuing system : make your shopping list of videos to generate and come back later 

**Discord Server to get Help from Other Users and show your Best Videos:** https://discord.gg/g7efUW9jGV

**Follow DeepBeepMeep on Twitter/X to get the Latest News**: https://x.com/deepbeepmeep

## 🔥 Latest Updates
### July 2 2025: WanGP v6.5.1, WanGP takes care of you: lots of quality of life features:
- View directly inside WanGP the properties (seed, resolutions, length, most settings...) of the past generations
- In one click use the newly generated video as a Control Video or Source Video to be continued 
- Manage multiple settings for the same model and switch between them using a dropdown box 
- WanGP will keep the last generated videos in the Gallery and will remember the last model you used if you restart the app but kept the Web page open
- Custom resolutions : add a file in the WanGP folder with the list of resolutions you want to see in WanGP (look at the instruction readme in this folder)

Taking care of your life is not enough, you want new stuff to play with ?
- MMAudio directly inside WanGP : add an audio soundtrack that matches the content of your video. By the way it is a low VRAM MMAudio and 6 GB of VRAM should be sufficient. You will need to go in the *Extensions* tab of the WanGP *Configuration* to enable MMAudio
- Forgot to upsample your video during the generation ? want to try another MMAudio variation ? Fear not you can also apply upsampling or add an MMAudio track once the video generation is done. Even better you can ask WangGP for multiple variations of MMAudio to pick the one you like best
- MagCache support: a new step skipping approach, supposed to be better than TeaCache. Makes a difference if you usually generate with a high number of steps
- SageAttention2++ support : not just the compatibility but also a slightly reduced VRAM usage
- Video2Video in Wan Text2Video : this is the paradox, a text2video can become a video2video if you start the denoising process later on an existing video
- FusioniX upsampler: this is an illustration of Video2Video in Text2Video. Use the FusioniX text2video model with an output resolution of 1080p and a denoising strength of 0.25 and you will get one of the best upsamplers (in only 2/3 steps, you will need lots of VRAM though). Increase the denoising strength and you will get one of the best Video Restorer
- Choice of Wan Samplers / Schedulers
- More Lora formats support

**If you had upgraded to v6.5 please upgrade again to 6.5.1 as this will fix a bug that ignored Loras beyond the first one**

### June 23 2025: WanGP v6.3, Vace Unleashed. Thought we couldnt squeeze Vace even more ?
- Multithreaded preprocessing when possible for faster generations
- Multithreaded frames Lanczos Upsampling as a bonus
- A new Vace preprocessor : *Flow* to extract fluid motion
- Multi Vace Controlnets: you can now transfer several properties at the same time. This opens new possibilities to explore, for instance if you transfer *Human Movement* and *Shapes* at the same time for some reasons the lighting of your character will take into account much more the environment of your character.
- Injected Frames Outpainting, in case you missed it in WanGP 6.21

Don't know how to use all of the Vace features ? Check the Vace Guide embedded in WanGP as it has also been updated.


### June 19 2025: WanGP v6.2, Vace even more Powercharged
👋 Have I told you that I am a big fan of Vace ? Here are more goodies to unleash its power: 
- If you ever wanted to watch Star Wars in 4:3, just use the new *Outpainting* feature and it will add the missing bits of image at the top and the bottom of the screen. The best thing is *Outpainting* can be combined with all the other Vace modifications, for instance you can change the main character of your favorite movie at the same time  
- More processing can combined at the same time  (for instance the depth process can be applied outside the mask)
- Upgraded the depth extractor to Depth Anything 2 which is much more detailed

As a bonus, I have added two finetunes based on the Safe-Forcing technology (which requires only 4 steps to generate a video): Wan 2.1 text2video Self-Forcing and Vace Self-Forcing. I know there is Lora around but the quality of the Lora is worse (at least with Vace) compared to the full model. Don't hesitate to share your opinion about this on the discord server. 
### June 17 2025: WanGP v6.1, Vace Powercharged
👋 Lots of improvements for Vace the Mother of all Models:
- masks can now be combined with on the fly processing of a control video, for instance you can extract the motion of a specific person defined by a mask
- on the fly modification of masks : reversed masks (with the same mask you can modify the background instead of the people covered by the masks), enlarged masks (you can cover more area if for instance the person you are trying to inject is larger than the one in the mask), ...
- view these modified masks directly inside WanGP during the video generation to check they are really as expected
- multiple frames injections: multiples frames can be injected at any location of the video
- expand past videos in on click: just select one generated video to expand it

Of course all these new stuff work on all Vace finetunes (including Vace Fusionix).

Thanks also to Reevoy24 for adding a Notfication sound at the end of a generation and for fixing the background color of the current generation summary.

### June 12 2025: WanGP v6.0
👋 *Finetune models*: You find the 20 models supported by WanGP not sufficient ? Too impatient to wait for the next release to get the support for a newly released model ? Your prayers have been answered: if a new model is compatible with a model architecture supported by WanGP, you can add by yourself the support for this model in WanGP by just creating a finetune model definition. You can then store this model in the cloud (for instance in Huggingface) and the very light finetune definition file can be easily shared with other users. WanGP will download automatically the finetuned model for them.

To celebrate the new finetunes support, here are a few finetune gifts (directly accessible from the model selection menu):
- *Fast Hunyuan Video* : generate model t2v in only 6 steps
- *Hunyuan Vido AccVideo* : generate model t2v in only 5 steps
- *Wan FusioniX*: it is a combo of AccVideo / CausVid ans other models and can generate high quality Wan videos in only 8 steps

One more thing...

The new finetune system can be used to combine complementaty models : what happens when you combine  Fusionix Text2Video and Vace Control Net ?

You get **Vace FusioniX**: the Ultimate Vace Model, Fast (10 steps, no need for guidance) and with a much better quality Video than the original slower model (despite being the best Control Net out there). Here goes one more finetune...

Check the *Finetune Guide* to create finetune models definitions and share them on the WanGP discord server.

### June 11 2025: WanGP v5.5
👋 *Hunyuan Video Custom Audio*: it is similar to Hunyuan Video Avatar except there isn't any lower limit on the number of frames and you can use your reference images in a different context than the image itself\
*Hunyuan Video Custom Edit*: Hunyuan Video Controlnet, use it to do inpainting and replace a person in a video while still keeping his poses. Similar to Vace but less restricted than the Wan models in terms of content...


### June 6 2025: WanGP v5.41
👋 Bonus release: Support for **AccVideo** Lora to speed up x2 Video generations in Wan models. Check the Loras documentation to get the usage instructions of AccVideo.\
You will need to do a *pip install -r requirements.txt*

### June 6 2025: WanGP v5.4
👋 World Exclusive : **Hunyuan Video Avatar** Support ! You won't need 80 GB of VRAM nor 32 GB oF VRAM, just 10 GB of VRAM will be sufficient to generate up to 15s of high quality speech / song driven Video at a high speed with no quality degradation. Support for TeaCache included.\
Here is a link to the original repo where you will find some very interesting documentation and examples. https://github.com/Tencent-Hunyuan/HunyuanVideo-Avatar. Kudos to the Hunyuan Video Avatar team for the best model of its kind.\
Also many thanks to Reevoy24 for his repackaging / completing the documentation

### May 28 2025: WanGP v5.31
👋 Added **Phantom 14B**, a model that you can use to transfer objects / people in the video. My preference goes to Vace that remains the king of controlnets.
VACE improvements: Better sliding window transitions, image mask support in Matanyone, new Extend Video feature, and enhanced background removal options.

### May 26, 2025: WanGP v5.3
👋 Settings management revolution! Now you can:
- Select any generated video and click *Use Selected Video Settings* to instantly reuse its configuration
- Drag & drop videos to automatically extract their settings metadata
- Export/import settings as JSON files for easy sharing and backup

### May 20, 2025: WanGP v5.2
👋 **CausVid support** - Generate videos in just 4-12 steps with the new distilled Wan model! Also added experimental MoviiGen for 1080p generation (20GB+ VRAM required). Check the Loras documentation to get the usage instructions of CausVid.

### May 18, 2025: WanGP v5.1
👋 **LTX Video 13B Distilled** - Generate high-quality videos in less than one minute!

### May 17, 2025: WanGP v5.0
👋 **One App to Rule Them All!** Added Hunyuan Video and LTX Video support, plus Vace 14B and integrated prompt enhancer.

See full changelog: **[Changelog](docs/CHANGELOG.md)**

## 📋 Table of Contents

- [🚀 Quick Start](#-quick-start)
- [📦 Installation](#-installation)
- [🎯 Usage](#-usage)
- [📚 Documentation](#-documentation)
- [🔗 Related Projects](#-related-projects)

## 🚀 Quick Start

**One-click installation:** Get started instantly with [Pinokio App](https://pinokio.computer/)

**Manual installation:**
```bash
git clone https://github.com/deepbeepmeep/Wan2GP.git
cd Wan2GP
conda create -n wan2gp python=3.10.9
conda activate wan2gp
pip install torch==2.7.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/test/cu124
pip install -r requirements.txt
```

**Run the application:**
```bash
python wgp.py  # Text-to-video (default)
python wgp.py --i2v  # Image-to-video
```

**Update the application:**
If using Pinokio use Pinokio to update otherwise:
Get in the directory where WanGP is installed and:
```bash
git pull
pip install -r requirements.txt
```

## 📦 Installation

For detailed installation instructions for different GPU generations:
- **[Installation Guide](docs/INSTALLATION.md)** - Complete setup instructions for RTX 10XX to RTX 50XX

## 🎯 Usage

### Basic Usage
- **[Getting Started Guide](docs/GETTING_STARTED.md)** - First steps and basic usage
- **[Models Overview](docs/MODELS.md)** - Available models and their capabilities

### Advanced Features
- **[Loras Guide](docs/LORAS.md)** - Using and managing Loras for customization
- **[Finetunes](docs/FINETUNES.md)** - Add manually new models to WanGP
- **[VACE ControlNet](docs/VACE.md)** - Advanced video control and manipulation
- **[Command Line Reference](docs/CLI.md)** - All available command line options

## 📚 Documentation

- **[Changelog](docs/CHANGELOG.md)** - Latest updates and version history
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## 🔗 Related Projects

### Other Models for the GPU Poor
- **[HuanyuanVideoGP](https://github.com/deepbeepmeep/HunyuanVideoGP)** - One of the best open source Text to Video generators
- **[Hunyuan3D-2GP](https://github.com/deepbeepmeep/Hunyuan3D-2GP)** - Image to 3D and text to 3D tool
- **[FluxFillGP](https://github.com/deepbeepmeep/FluxFillGP)** - Inpainting/outpainting tools based on Flux
- **[Cosmos1GP](https://github.com/deepbeepmeep/Cosmos1GP)** - Text to world generator and image/video to world
- **[OminiControlGP](https://github.com/deepbeepmeep/OminiControlGP)** - Flux-derived application for object transfer
- **[YuE GP](https://github.com/deepbeepmeep/YuEGP)** - Song generator with instruments and singer's voice

---

<p align="center">
Made with ❤️ by DeepBeepMeep
</p> 
