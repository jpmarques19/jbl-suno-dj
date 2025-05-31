#!/usr/bin/env python3
"""
Test the complete voice-to-Suno-to-JBL workflow
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from voice_to_suno_jbl import VoiceToSunoJBL

def test_jbl_audio():
    """Test JBL audio output."""
    print("🔊 Testing JBL Audio Output")
    print("=" * 40)
    
    app = VoiceToSunoJBL()
    
    # Test JBL connection
    if app.set_jbl_as_default():
        print("✅ JBL set as default audio device")
        
        # Test with system sound
        import subprocess
        try:
            subprocess.run(['paplay', '/usr/share/sounds/alsa/Front_Right.wav', 
                          '--device=bluez_output.04_CB_88_B8_CF_72.1'], 
                         check=True, timeout=5)
            print("✅ JBL audio test successful!")
            return True
        except Exception as e:
            print(f"❌ JBL audio test failed: {e}")
            return False
    else:
        print("❌ Could not set JBL as default")
        return False

def test_voice_recognition():
    """Test voice recognition."""
    print("\n🎤 Testing Voice Recognition")
    print("=" * 40)
    
    app = VoiceToSunoJBL()
    
    print("🎤 Say something (you have 10 seconds)...")
    prompt = app.listen_for_voice_command()
    
    if prompt:
        print(f"✅ Voice recognition successful: '{prompt}'")
        return prompt
    else:
        print("❌ Voice recognition failed")
        return None

def test_music_generation(prompt="happy upbeat song"):
    """Test music generation."""
    print(f"\n🎵 Testing Music Generation")
    print("=" * 40)
    
    app = VoiceToSunoJBL()
    
    # Generate music
    task_id = app.generate_music(prompt)
    if not task_id:
        print("❌ Music generation failed")
        return None
    
    # Wait for completion
    tracks = app.wait_for_music(task_id)
    if tracks:
        print(f"✅ Music generation successful! Got {len(tracks)} track(s)")
        return tracks
    else:
        print("❌ Music generation timed out")
        return None

def test_complete_workflow():
    """Test the complete workflow."""
    print("\n🎯 Testing Complete Workflow")
    print("=" * 40)
    
    app = VoiceToSunoJBL()
    
    print("🎤 This will test the complete voice-to-music workflow")
    print("📝 You'll be asked to speak a music request")
    print("🎵 The system will generate music and play it on your JBL")
    print("⏹️  Press Ctrl+C to cancel at any time")
    print()
    
    input("Press Enter when ready to start...")
    
    try:
        success = app.run_voice_session()
        if success:
            print("🎉 Complete workflow test successful!")
        else:
            print("❌ Complete workflow test failed")
        return success
    except KeyboardInterrupt:
        print("\n👋 Test cancelled by user")
        return False

def main():
    """Main test function."""
    print("🧪 JBL-Suno-DJ Complete System Test")
    print("=" * 50)
    
    try:
        # Test 1: JBL Audio
        jbl_ok = test_jbl_audio()
        
        if not jbl_ok:
            print("\n❌ JBL audio test failed - please check your speaker connection")
            return False
        
        # Test 2: Voice Recognition (optional)
        print("\n🎤 Would you like to test voice recognition? (y/n): ", end="")
        if input().lower().startswith('y'):
            voice_prompt = test_voice_recognition()
            if voice_prompt:
                # Test 3: Music Generation with voice prompt
                tracks = test_music_generation(voice_prompt)
            else:
                print("⚠️  Voice recognition failed, using default prompt")
                tracks = test_music_generation()
        else:
            # Test 3: Music Generation with default prompt
            tracks = test_music_generation()
        
        if not tracks:
            print("\n❌ Music generation test failed")
            return False
        
        # Test 4: Play on JBL
        print(f"\n🔊 Playing generated music on JBL...")
        app = VoiceToSunoJBL()
        for track in tracks:
            success = app.play_on_jbl(track)
            if success:
                print("✅ JBL playback successful!")
                break
        
        # Test 5: Complete workflow (optional)
        print("\n🎯 Would you like to test the complete voice workflow? (y/n): ", end="")
        if input().lower().startswith('y'):
            test_complete_workflow()
        
        print("\n🎉 All tests completed!")
        return True
        
    except KeyboardInterrupt:
        print("\n👋 Tests cancelled by user")
        return False
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
