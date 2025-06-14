#!/usr/bin/env python3
"""
Hugging Face Spaces wrapper for Wan2GP
This script ensures the application runs properly in the HF Spaces environment
"""

import os
import sys
import warnings
import subprocess

# Set environment variables for HF Spaces
os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "0"  # Allow online model downloads
os.environ["HF_HUB_OFFLINE"] = "0"  # Allow HF Hub access

# Suppress warnings that might clutter the HF Spaces logs
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

def setup_directories():
    """Create necessary directories for the application"""
    directories = [
        "outputs", "settings", "loras", "loras_i2v", "loras_ltxv", 
        "loras_hunyuan", "loras_hunyuan_i2v", "ckpts", "ckpts/umt5-xxl",
        "ckpts/xlm-roberta-large", "ckpts/T5_xxl_1.1", "ckpts/llava-llama-3-8b"
    ]
    
    for dir_name in directories:
        try:
            os.makedirs(dir_name, exist_ok=True)
            print(f"✅ Created directory: {dir_name}")
        except Exception as e:
            print(f"⚠️  Could not create directory {dir_name}: {e}")

def check_dependencies():
    """Check if critical dependencies are available"""
    critical_deps = ['torch', 'gradio', 'transformers', 'diffusers', 'mmgp']
    missing_deps = []
    
    for dep in critical_deps:
        try:
            __import__(dep)
            print(f"✅ {dep} is available")
        except ImportError:
            missing_deps.append(dep)
            print(f"❌ {dep} is missing")
    
    if missing_deps:
        print(f"❌ Missing critical dependencies: {', '.join(missing_deps)}")
        return False
    return True

def main():
    print("🚀 Starting Wan2GP for Hugging Face Spaces...")
    
    # Add current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Setup directories
    setup_directories()
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed")
        sys.exit(1)
    
    # Import and run the main application
    try:
        print("📦 Loading Wan2GP application...")
        import app
        print("✅ Wan2GP loaded successfully for Hugging Face Spaces")
        print("🌐 Application should be accessible shortly...")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("This might be due to missing dependencies or incorrect installation")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading Wan2GP: {e}")
        import traceback
        traceback.print_exc()
        
        # Try to provide helpful error information
        if "CUDA" in str(e):
            print("💡 CUDA-related error detected. This is normal in CPU-only environments.")
        elif "model" in str(e).lower():
            print("💡 Model loading error. Models will be downloaded on first use.")
        elif "torch" in str(e).lower():
            print("💡 PyTorch-related error. Check if PyTorch is properly installed.")
            
        sys.exit(1)

if __name__ == "__main__":
    main() 