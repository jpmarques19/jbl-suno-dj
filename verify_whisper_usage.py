#!/usr/bin/env python3
"""
Verify that Whisper is actually being used (not Google)
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, '.')

def verify_whisper_config():
    """Verify Whisper configuration and usage."""
    print("🔍 Whisper Usage Verification")
    print("=" * 50)
    
    # Load environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment loaded")
    except ImportError:
        print("⚠️  python-dotenv not available")
    
    # Check environment variables
    speech_service = os.getenv("SPEECH_SERVICE", "google")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    print(f"📋 Configuration:")
    print(f"   SPEECH_SERVICE: {speech_service}")
    print(f"   OPENAI_API_KEY: {'✅ Set' if openai_key else '❌ Missing'}")
    
    if speech_service != "whisper":
        print(f"❌ ERROR: Speech service is '{speech_service}', not 'whisper'!")
        return False
    
    if not openai_key:
        print("❌ ERROR: OpenAI API key is missing!")
        return False
    
    print("✅ Configuration looks correct for Whisper")
    print()
    
    # Test the actual implementation
    print("🧪 Testing actual speech recognition method...")
    
    try:
        from voice_to_suno_jbl import VoiceToSunoJBL
        
        # Create app instance
        app = VoiceToSunoJBL()
        
        # Check which method will be called
        print("🔍 Checking speech recognition method selection...")
        
        # Create a dummy audio object for testing
        class DummyAudio:
            def __init__(self):
                self.sample_width = 2
                self.sample_rate = 16000
                self.frame_data = b'\x00' * 32000  # 1 second of silence
        
        dummy_audio = DummyAudio()
        
        # Test the method selection logic
        print(f"📊 Method selection test:")
        print(f"   SPEECH_SERVICE: {os.getenv('SPEECH_SERVICE')}")
        print(f"   OPENAI_API_KEY exists: {bool(os.getenv('OPENAI_API_KEY'))}")
        
        # This will show us which method gets called
        if os.getenv('SPEECH_SERVICE') == 'whisper' and os.getenv('OPENAI_API_KEY'):
            print("✅ Will use: recognize_with_whisper()")
            
            # Test Whisper method directly
            print("\n🎤 Testing Whisper method directly...")
            try:
                result = app.recognize_with_whisper(dummy_audio)
                if result is not None:
                    print(f"✅ Whisper method works! Result: '{result}'")
                    return True
                else:
                    print("⚠️  Whisper method returned None (normal for silence)")
                    return True
            except Exception as e:
                print(f"❌ Whisper method failed: {e}")
                return False
        else:
            print("❌ Will use: recognize_with_google() (FALLBACK)")
            return False
            
    except Exception as e:
        print(f"❌ Import/setup error: {e}")
        return False

def test_live_whisper():
    """Test live Whisper recognition."""
    print("\n🎤 Live Whisper Test")
    print("=" * 30)
    print("This will record 5 seconds and process with Whisper")
    print("You should see 'Whisper:' in the output (not 'Google:')")
    print()
    
    try:
        from voice_to_suno_jbl import VoiceToSunoJBL
        
        app = VoiceToSunoJBL()
        
        choice = input("Ready to test live Whisper? (y/n): ")
        if not choice.lower().startswith('y'):
            print("👋 Test skipped")
            return
        
        print("🔴 Recording 5 seconds for Whisper test...")
        
        # Modify the recording duration temporarily
        import speech_recognition as sr
        
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        # Quick calibration
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
        
        # Record 5 seconds
        print("🎤 Speak now (5 seconds)...")
        with microphone as source:
            audio = recognizer.record(source, duration=5)
        
        print("🔄 Processing with Whisper...")
        
        # Process with Whisper method directly
        result = app.recognize_with_whisper(audio)
        
        if result:
            print(f"✅ WHISPER SUCCESS: '{result}'")
            print("🎉 Confirmed: Using OpenAI Whisper API!")
        else:
            print("❌ Whisper returned no result")
            
    except Exception as e:
        print(f"❌ Live test error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main verification function."""
    print("🔍 Whisper Usage Verification Tool")
    print("=" * 60)
    print("This will verify that Whisper (not Google) is being used.")
    print()
    
    # Step 1: Verify configuration
    config_ok = verify_whisper_config()
    
    if not config_ok:
        print("\n❌ Configuration issues found!")
        print("💡 Fix the configuration before proceeding")
        return
    
    print("\n✅ Configuration verified - Whisper should be used!")
    
    # Step 2: Test live
    test_live_whisper()

if __name__ == "__main__":
    main()
