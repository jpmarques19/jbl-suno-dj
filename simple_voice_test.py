#!/usr/bin/env python3
"""
Simple voice test without complex initialization
"""

import speech_recognition as sr
import time
import threading

def simple_voice_test():
    """Simple voice test with 10-second recording."""
    print("🎤 Simple Voice Test")
    print("=" * 30)
    
    try:
        # Create recognizer and microphone
        print("🔧 Creating recognizer...")
        recognizer = sr.Recognizer()
        
        print("🔧 Creating microphone...")
        microphone = sr.Microphone()
        
        print("🔧 Quick calibration...")
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
        
        print(f"✅ Ready! Energy threshold: {recognizer.energy_threshold}")
        print()
        
        # Countdown
        print("🎤 Get ready to speak...")
        for i in range(3, 0, -1):
            print(f"Starting in {i}...")
            time.sleep(1)
        
        print("🔴 RECORDING 10 SECONDS - SPEAK NOW!")
        
        # Recording with timer
        listening = True
        start_time = time.time()
        record_seconds = 10
        
        def show_timer():
            while listening:
                elapsed = time.time() - start_time
                remaining = max(0, record_seconds - elapsed)
                if remaining > 0:
                    print(f"\r⏱️  {remaining:.1f}s remaining", end="", flush=True)
                    time.sleep(0.1)
                else:
                    print(f"\r⏰ Recording complete!")
                    break
        
        # Start timer thread
        timer_thread = threading.Thread(target=show_timer, daemon=True)
        timer_thread.start()
        
        # Record audio
        with microphone as source:
            audio = recognizer.record(source, duration=record_seconds)
        
        listening = False
        time.sleep(0.2)  # Let timer finish
        
        print(f"\n🔄 Processing audio...")
        
        # Process with Google Speech Recognition
        try:
            text = recognizer.recognize_google(audio)
            print(f"✅ SUCCESS: '{text}'")
            return text
        except sr.UnknownValueError:
            print(f"❓ Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Google API error: {e}")
            return None
        except Exception as e:
            print(f"❌ Processing error: {e}")
            return None
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function."""
    print("🎤 Simple Voice Recognition Test")
    print("=" * 50)
    print("This is a simplified test to isolate the voice recognition issue.")
    print()
    
    try:
        result = simple_voice_test()
        
        if result:
            print(f"\n🎉 Voice test successful!")
            print(f"📝 You said: '{result}'")
            
            # Check if it's music-related
            music_words = ['music', 'song', 'melody', 'tune', 'jazz', 'rock', 'electronic']
            if any(word in result.lower() for word in music_words):
                print("🎵 Detected as music request!")
            else:
                print("💡 Try adding music-related words")
        else:
            print(f"\n⚠️  Voice test failed")
            print("💡 This helps us understand what's not working")
        
    except KeyboardInterrupt:
        print("\n👋 Test cancelled")
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
