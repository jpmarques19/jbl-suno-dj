#!/usr/bin/env python3
"""
Test the improved voice recognition with countdown timer
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from voice_to_suno_jbl import VoiceToSunoJBL

def test_voice_recognition_with_timer():
    """Test the improved voice recognition."""
    print("🎤 Voice Recognition Test with Timer")
    print("=" * 50)
    
    try:
        # Initialize the app
        print("🔧 Initializing voice recognition...")
        app = VoiceToSunoJBL()
        print("✅ Voice recognition ready!")
        print()
        
        # Test multiple attempts
        for attempt in range(1, 4):
            print(f"🎯 Attempt {attempt}/3")
            print("💡 Try saying something like:")
            print("   'Create a happy song'")
            print("   'Generate rock music'")
            print("   'Make electronic dance music'")
            print()
            
            # Test voice recognition
            result = app.listen_for_voice_command()
            
            if result:
                print(f"\n🎉 Success! Recognized: '{result}'")
                
                # Check if it's a music request
                music_keywords = ['music', 'song', 'create', 'generate', 'make', 'play', 'beat', 'melody']
                if any(keyword in result.lower() for keyword in music_keywords):
                    print("🎵 This sounds like a music request!")
                    print(f"🚀 Would generate music with: '{result}'")
                else:
                    print("🤔 This doesn't sound like a music request")
                    print("💡 Try adding words like 'create', 'generate', 'music', etc.")
                
                # Ask if user wants to continue
                if attempt < 3:
                    choice = input(f"\nTry another voice test? (y/n): ")
                    if not choice.lower().startswith('y'):
                        break
                print()
                
            else:
                print(f"\n❌ Voice recognition failed on attempt {attempt}")
                if attempt < 3:
                    choice = input(f"Try again? (y/n): ")
                    if not choice.lower().startswith('y'):
                        break
                print()
        
        print("🎉 Voice recognition test completed!")
        
    except KeyboardInterrupt:
        print("\n👋 Test cancelled by user")
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()

def test_microphone_levels():
    """Test microphone input levels."""
    print("\n🔊 Microphone Level Test")
    print("=" * 30)
    
    try:
        import speech_recognition as sr
        
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        print("🔧 Calibrating microphone...")
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=2)
        
        print(f"✅ Calibration complete!")
        print(f"📊 Energy threshold: {recognizer.energy_threshold}")
        print(f"💡 Lower values = more sensitive to quiet sounds")
        print(f"💡 Higher values = less sensitive, filters out noise")
        
        if recognizer.energy_threshold < 100:
            print("🔇 Very sensitive - good for quiet environments")
        elif recognizer.energy_threshold < 300:
            print("🔉 Normal sensitivity - good for most environments")
        else:
            print("🔊 Low sensitivity - may need louder speech")
        
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")

def main():
    """Main test function."""
    print("🎤 Enhanced Voice Recognition Tester")
    print("=" * 50)
    print()
    print("This will test the improved voice recognition with:")
    print("✅ Visual countdown timer")
    print("✅ Real-time time remaining display")
    print("✅ Better user feedback")
    print("✅ Clear instructions")
    print()
    
    try:
        # Test microphone levels first
        test_microphone_levels()
        
        print()
        input("Press Enter to start voice recognition test...")
        
        # Test voice recognition
        test_voice_recognition_with_timer()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Error: {e}")

if __name__ == "__main__":
    main()
