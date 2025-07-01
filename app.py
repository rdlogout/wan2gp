#!/usr/bin/env python3

import os
import sys
import warnings

# Suppress warnings for cleaner deployment
warnings.filterwarnings("ignore")

# Set environment variables for Hugging Face Spaces
os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

# Override command line arguments for Hugging Face Spaces deployment
original_argv = sys.argv.copy()
sys.argv = ["app.py", "--server-name", "0.0.0.0", "--server-port", "7860"]

# Import the main application
try:
    from wgp import create_ui
    print("✅ WanGP modules loaded successfully")
except ImportError as e:
    print(f"❌ Error importing WanGP: {e}")
    print("Please ensure all required dependencies are installed")
    sys.exit(1)

# Create and launch the Gradio interface
if __name__ == "__main__":
    try:
        # Create the UI
        demo = create_ui()
        print("✅ Gradio UI created successfully")
        
        # Launch with Hugging Face Spaces compatible settings
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            show_error=True,
            show_api=False,
            quiet=True
        )
    except Exception as e:
        print(f"❌ Error starting the application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 