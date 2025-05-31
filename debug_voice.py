#!/usr/bin/env python3
"""
Debug voice recognition step by step
"""

import speech_recognition as sr
import pyaudio
import wave
import sys
import time

def list_audio_devices():
    """List all available audio input devices."""
    print("🎤 Available Audio Input Devices:")
    print("=" * 50)
    
    p = pyaudio.PyAudio()
    
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:  # Input device
            print(f"  {i}: {info['name']}")
            print(f"      Channels: {info['maxInputChannels']}")
            print(f"      Sample Rate: {info['defaultSampleRate']}")
            print()
    
    p.terminate()

def test_microphone_levels():
    """Test microphone input levels."""
    print("🎤 Testing Microphone Input Levels")
    print("=" * 40)
    print("Speak into your microphone for 5 seconds...")
    
    recognizer = sr.Recognizer()
    
    # Try different microphone devices
    mic_list = sr.Microphone.list_microphone_names()
    print(f"Found {len(mic_list)} microphone devices:")
    for i, name in enumerate(mic_list):
        print(f"  {i}: {name}")
    print()
    
    # Test default microphone
    try:
        microphone = sr.Microphone()
        
        print("🔧 Testing default microphone...")
        with microphone as source:
            print("📊 Measuring ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=2)
            print(f"   Energy threshold: {recognizer.energy_threshold}")
            
            print("🎤 Recording for 5 seconds... SPEAK NOW!")
            audio = recognizer.listen(source, timeout=1, phrase_time_limit=5)
            print(f"✅ Recorded {len(audio.frame_data)} bytes of audio")
            
            return audio
            
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")
        return None

def test_speech_recognition_engines(audio):
    """Test different speech recognition engines."""
    print("\n🧠 Testing Speech Recognition Engines")
    print("=" * 50)
    
    recognizer = sr.Recognizer()
    
    # Test Google (free)
    print("🔍 Testing Google Speech Recognition (free)...")
    try:
        text = recognizer.recognize_google(audio)
        print(f"✅ Google: '{text}'")
    except sr.UnknownValueError:
        print("❓ Google: Could not understand audio")
    except sr.RequestError as e:
        print(f"❌ Google: Request error - {e}")
    except Exception as e:
        print(f"❌ Google: Error - {e}")
    
    # Test Sphinx (offline)
    print("\n🔍 Testing Sphinx (offline)...")
    try:
        text = recognizer.recognize_sphinx(audio)
        print(f"✅ Sphinx: '{text}'")
    except sr.UnknownValueError:
        print("❓ Sphinx: Could not understand audio")
    except sr.RequestError as e:
        print(f"❌ Sphinx: Request error - {e}")
    except Exception as e:
        print(f"❌ Sphinx: Error - {e}")

def save_audio_for_analysis(audio):
    """Save recorded audio to file for manual analysis."""
    print("\n💾 Saving Audio for Analysis")
    print("=" * 40)
    
    try:
        filename = f"voice_test_{int(time.time())}.wav"
        with open(filename, "wb") as f:
            f.write(audio.get_wav_data())
        
        print(f"✅ Audio saved as: {filename}")
        print(f"📁 You can play this file to hear what was recorded:")
        print(f"   mpv {filename}")
        print(f"   or")
        print(f"   aplay {filename}")
        
        return filename
        
    except Exception as e:
        print(f"❌ Failed to save audio: {e}")
        return None

def test_manual_input():
    """Test with manual text input instead of voice."""
    print("\n⌨️  Manual Text Input Test")
    print("=" * 40)
    
    while True:
        try:
            text = input("Enter a music prompt (or 'quit' to exit): ").strip()
            if text.lower() in ['quit', 'exit', 'q']:
                break
            
            if text:
                print(f"📝 You entered: '{text}'")
                
                # Check if it sounds like a music request
                music_keywords = ['music', 'song', 'play', 'generate', 'create', 'make', 
                                'beat', 'melody', 'tune', 'track', 'audio', 'sound']
                
                if any(keyword in text.lower() for keyword in music_keywords):
                    print("🎵 This looks like a music request!")
                    print(f"🚀 Would generate music with prompt: '{text}'")
                else:
                    print("🤔 This doesn't look like a music request")
                    print("💡 Try adding words like 'music', 'song', 'create', etc.")
                
                print()
            
        except KeyboardInterrupt:
            print("\n👋 Manual test cancelled")
            break

def interactive_voice_test():
    """Interactive voice testing with multiple attempts."""
    print("\n🎤 Interactive Voice Test")
    print("=" * 40)
    
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    # Calibrate
    print("🔧 Calibrating microphone...")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=2)
    
    print(f"✅ Calibration complete. Energy threshold: {recognizer.energy_threshold}")
    print()
    
    attempt = 1
    while attempt <= 5:
        print(f"🎤 Attempt {attempt}/5")
        print("📢 Say something clearly (you have 10 seconds)...")
        print("💡 Try saying: 'Create a happy song' or 'Generate upbeat music'")
        
        try:
            with microphone as source:
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
            
            print("🔄 Processing...")
            
            # Try Google first
            try:
                text = recognizer.recognize_google(audio)
                print(f"✅ Recognized: '{text}'")
                
                # Save this successful audio
                filename = save_audio_for_analysis(audio)
                
                return text
                
            except sr.UnknownValueError:
                print("❓ Could not understand the audio")
                # Save for analysis
                save_audio_for_analysis(audio)
                
            except sr.RequestError as e:
                print(f"❌ Recognition service error: {e}")
        
        except sr.WaitTimeoutError:
            print("⏰ No speech detected within timeout")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        attempt += 1
        if attempt <= 5:
            print("🔄 Let's try again...\n")
    
    print("❌ Voice recognition failed after 5 attempts")
    return None

def main():
    """Main debug function."""
    print("🔍 Voice Recognition Debug Tool")
    print("=" * 50)
    
    try:
        # Step 1: List audio devices
        list_audio_devices()
        
        # Step 2: Test microphone levels
        audio = test_microphone_levels()
        
        if audio:
            # Step 3: Test recognition engines
            test_speech_recognition_engines(audio)
            
            # Step 4: Save audio for analysis
            save_audio_for_analysis(audio)
        
        # Step 5: Interactive voice test
        print("\n" + "="*50)
        choice = input("Would you like to try interactive voice testing? (y/n): ")
        if choice.lower().startswith('y'):
            result = interactive_voice_test()
            if result:
                print(f"\n🎉 Success! Final result: '{result}'")
        
        # Step 6: Manual input test
        print("\n" + "="*50)
        choice = input("Would you like to test manual text input? (y/n): ")
        if choice.lower().startswith('y'):
            test_manual_input()
        
        print("\n🎉 Debug session completed!")
        
    except KeyboardInterrupt:
        print("\n👋 Debug cancelled by user")
    except Exception as e:
        print(f"\n💥 Debug error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
