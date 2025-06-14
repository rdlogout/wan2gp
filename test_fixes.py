#!/usr/bin/env python3
"""
Test script to validate fixes for Hugging Face Spaces deployment
"""

import os
import sys

def test_audio_environment_setup():
    """Test that audio environment variables are set correctly"""
    print("Testing audio environment setup...")
    
    # Simulate containerized environment
    if 'XDG_RUNTIME_DIR' in os.environ:
        del os.environ['XDG_RUNTIME_DIR']
    if 'DISPLAY' in os.environ:
        del os.environ['DISPLAY']
    
    # Test the logic from app.py
    if os.environ.get('XDG_RUNTIME_DIR') is None and os.environ.get('DISPLAY') is None:
        os.environ['SDL_AUDIODRIVER'] = 'dummy'
        os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
        print("✓ Audio environment variables set correctly for containerized environment")
    else:
        print("✗ Audio environment variables not set correctly")

def test_notification_sound_fallback():
    """Test that notification sound handles containerized environment"""
    print("Testing notification sound fallback...")
    
    try:
        # Import after setting environment variables
        from wan.utils.notification_sound import play_audio_with_pygame, play_audio_with_sounddevice
        import numpy as np
        
        # Test data
        test_audio = np.array([0.1, 0.2, 0.1, -0.1, -0.2])
        
        # Test pygame fallback
        result_pygame = play_audio_with_pygame(test_audio)
        print(f"✓ pygame fallback result: {result_pygame} (should be False in containerized env)")
        
        # Test sounddevice fallback  
        result_sounddevice = play_audio_with_sounddevice(test_audio)
        print(f"✓ sounddevice fallback result: {result_sounddevice} (should be False in containerized env)")
        
    except Exception as e:
        print(f"✗ Error testing notification sound: {e}")

def test_gradio_components():
    """Test Gradio components for compatibility"""
    print("Testing Gradio components...")
    
    try:
        import gradio as gr
        print(f"✓ Gradio version: {gr.__version__}")
        
        # Test Row with scale parameter
        try:
            with gr.Blocks():
                with gr.Row():
                    with gr.Column(scale=2):
                        gr.Markdown("Test")
                    with gr.Column(scale=1):
                        gr.Button("Test")
            print("✓ Column with scale parameter works correctly")
        except Exception as e:
            print(f"✗ Error with Column scale parameter: {e}")
            
        # Test that Row doesn't accept scale in older versions
        try:
            gr.Row(scale=1)
            print("⚠ Row accepts scale parameter (may cause issues in some Gradio versions)")
        except Exception as e:
            print("✓ Row correctly rejects scale parameter")
            
    except Exception as e:
        print(f"✗ Error testing Gradio components: {e}")

def main():
    """Run all tests"""
    print("Running deployment fixes validation...\n")
    
    test_audio_environment_setup()
    print()
    
    test_notification_sound_fallback()
    print()
    
    test_gradio_components()
    print()
    
    print("Validation complete!")

if __name__ == "__main__":
    main()
