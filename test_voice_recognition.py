#!/usr/bin/env python3
"""
Test voice recognition functionality
"""

import speech_recognition as sr
import sys

def test_microphone():
    """Test microphone and voice recognition."""
    print("🎤 Testing Voice Recognition")
    print("=" * 40)
    
    # Initialize recognizer and microphone
    recognizer = sr.Recognizer()
    
    # List available microphones
    print("📱 Available microphones:")
    for i, mic_name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"  {i}: {mic_name}")
    print()
    
    # Use default microphone
    microphone = sr.Microphone()
    
    print("🔧 Calibrating for ambient noise...")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=2)
    print("✅ Calibration complete!")
    print()
    
    # Test voice recognition
    for attempt in range(3):
        print(f"🎤 Test {attempt + 1}/3: Say something (you have 10 seconds)...")
        
        try:
            with microphone as source:
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
            
            print("🔄 Processing speech...")
            
            # Try to recognize speech
            text = recognizer.recognize_google(audio)
            print(f"✅ Recognized: '{text}'")
            
            # Test if it sounds like a music request
            music_keywords = ['music', 'song', 'play', 'generate', 'create', 'make']
            if any(keyword in text.lower() for keyword in music_keywords):
                print("🎵 This sounds like a music request!")
            
            print()
            
        except sr.WaitTimeoutError:
            print("⏰ No speech detected within timeout")
            print()
        except sr.UnknownValueError:
            print("❓ Could not understand the audio")
            print()
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            print()
        except KeyboardInterrupt:
            print("\n👋 Test cancelled")
            break
    
    print("🎉 Voice recognition test completed!")

if __name__ == "__main__":
    try:
        test_microphone()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Error: {e}")
        sys.exit(1)
