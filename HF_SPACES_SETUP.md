# Wan2GP Hugging Face Spaces Setup Guide

This document explains the modifications made to make Wan2GP compatible with Hugging Face Spaces and provides deployment instructions.

## Changes Made

### 1. Dependencies (`requirements.txt`)

- **Removed**: `onnxruntime-gpu` → replaced with `onnxruntime` for better compatibility
- **Removed**: `pygame` and `sounddevice` → not needed in web environments
- **Added**: `huggingface_hub` for HF Hub integration
- **Note**: The `spaces` module is provided by HF Spaces environment, not installed via pip

### 2. Application Modifications (`app.py`)

- **HF Spaces Detection**: Added `RUNNING_ON_HF_SPACES` environment variable detection
- **Audio Dependencies**: Made pygame/sounddevice imports optional with graceful fallbacks
- **GPU Detection**: Added error handling for CUDA capabilities in cloud environments
- **Server Configuration**: Automatic server settings for HF Spaces environment
- **Model Defaults**: Set `t2v_1.3B` as default model for HF Spaces (lighter than 14B models)

### 3. README.md Updates

- Updated with proper HF Spaces metadata
- Set `hardware: a10g-small` for GPU acceleration
- Added comprehensive description and usage instructions
- Set appropriate Python version and storage requirements

### 4. HF Spaces Wrapper (`spaces.py`)

- Created a dedicated startup script for HF Spaces
- Automatic directory creation for required folders
- Dependency checking and helpful error messages
- Environment variable configuration for optimal performance

## Deployment Instructions

### Step 1: Create a New Space

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Choose "Gradio" as the SDK
4. Set appropriate hardware (recommended: A10G Small or better)

### Step 2: Upload Files

Upload all the modified files to your new Space:

- `app.py` (main application)
- `requirements.txt` (dependencies)
- `README.md` (Space configuration)
- `spaces.py` (startup wrapper)
- `.gitattributes` (for LFS support)
- All other project files and directories

### Step 3: Configure the Space

In your Space settings:

- Set `app_file: app.py` in README.md header
- Enable persistent storage if needed for model caching
- Set timeout to a reasonable value (models take time to download initially)

## Key Features Optimized for HF Spaces

### Model Selection

- **Default Model**: `t2v_1.3B` for faster loading and reasonable VRAM usage
- **Available Models**: All original models are still available via the dropdown
- **Auto-downloading**: Models download automatically on first use

### Performance Optimizations

- **Quantization**: Uses INT8 quantization by default for memory efficiency
- **Attention Mode**: Auto-detection for optimal attention mechanism
- **GPU Handling**: Graceful fallback to CPU if GPU is unavailable

### User Experience

- **Queue System**: Built-in task queue for batch processing
- **Progress Tracking**: Real-time progress bars and status updates
- **Error Handling**: Improved error messages and recovery

## Troubleshooting

### Common Issues and Solutions

#### 1. "CUDA not available" errors

- **Expected behavior** in CPU-only environments
- The app will automatically fallback to CPU processing
- Consider upgrading to GPU hardware for faster inference

#### 2. Model download timeouts

- **First run**: Models need to download (can take 10-15 minutes)
- **Solution**: Be patient or upgrade to persistent storage
- **Check**: Network connectivity and HF Hub access

#### 3. Memory errors

- **Cause**: Trying to load large models on insufficient hardware
- **Solution**: Use smaller models like `t2v_1.3B` instead of `t2v`
- **Alternative**: Upgrade to larger hardware (A100 for 14B models)

#### 4. Import errors

- **Check**: All dependencies in requirements.txt are properly installed
- **Solution**: Restart the Space to trigger fresh installation
- **Debug**: Check the startup logs for specific missing packages

#### 5. "spaces has no attribute 'gradio_auto_wrap'" error

- **Cause**: Conflict between installed `spaces` package and HF Spaces built-in module
- **Solution**: Remove `spaces` from requirements.txt (HF Spaces provides it automatically)
- **Fixed**: This issue has been resolved in the current setup

## Model Recommendations by Hardware

### CPU Only

- Limited functionality
- Very slow inference
- Not recommended for production use

### A10G Small (recommended minimum)

- `t2v_1.3B`: ✅ Good performance
- `i2v`: ✅ Works well
- `vace_1.3B`: ✅ Good for control tasks
- `t2v_14B`: ⚠️ Possible but slow

### A100 (optimal)

- All models supported
- Fast inference
- Multiple concurrent users
- Best user experience

## Additional Notes

### Storage Requirements

- **Models**: 5-20GB depending on which models are cached
- **Outputs**: Videos can be large, consider cleanup strategies
- **Recommendation**: Enable persistent storage for better user experience

### Security Considerations

- All user inputs are processed server-side
- Generated content is temporary unless downloaded
- Consider content moderation for public deployments

### Performance Tips

- **Batch Processing**: Use the queue system for multiple generations
- **Parameter Tuning**: Lower step counts for faster generation
- **Resolution**: Start with lower resolutions for testing

## Support

For issues specific to the HF Spaces deployment:

1. Check the Space logs for detailed error information
2. Verify all files were uploaded correctly
3. Ensure hardware requirements are met
4. Test with simpler prompts first

For application-specific issues:

- Refer to the original Wan2GP documentation
- Check model-specific requirements and limitations
- Experiment with different parameter combinations

## License

This setup maintains the original license terms of the Wan2GP project. Check the LICENSE.txt file for details.
