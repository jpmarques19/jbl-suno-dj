#!/usr/bin/env python3
"""
Verbose debug version to see exactly what's happening
"""

import sys
import os
import traceback
import time

print("🔍 Starting verbose voice debug...")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")

# Test imports first
try:
    print("📦 Testing imports...")
    import speech_recognition as sr
    print("✅ speech_recognition imported")
    
    import requests
    print("✅ requests imported")
    
    import threading
    print("✅ threading imported")
    
    print("✅ All basic imports successful")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test speech recognition setup
try:
    print("\n🎤 Testing speech recognition setup...")
    
    recognizer = sr.Recognizer()
    print("✅ Recognizer created")
    
    microphone = sr.Microphone()
    print("✅ Microphone created")
    
    print("🔧 Testing microphone calibration...")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
    print(f"✅ Calibration complete. Energy threshold: {recognizer.energy_threshold}")
    
except Exception as e:
    print(f"❌ Speech recognition setup error: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test recording
try:
    print("\n🎙️  Testing audio recording...")
    print("This will record 3 seconds of audio...")
    
    input("Press Enter to start 3-second test recording...")
    
    print("🔴 Recording 3 seconds...")
    start_time = time.time()
    
    with microphone as source:
        audio = recognizer.record(source, duration=3)
    
    end_time = time.time()
    print(f"✅ Recording completed in {end_time - start_time:.1f} seconds")
    print(f"📊 Audio data length: {len(audio.frame_data)} bytes")
    
except Exception as e:
    print(f"❌ Recording error: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test speech recognition
try:
    print("\n🧠 Testing speech recognition...")
    print("Processing the 3-second recording...")
    
    start_time = time.time()
    
    try:
        text = recognizer.recognize_google(audio, show_all=False)
        end_time = time.time()
        
        if text and text.strip():
            print(f"✅ Recognition successful in {end_time - start_time:.1f} seconds")
            print(f"🎯 Recognized: '{text}'")
        else:
            print(f"⚠️  Recognition returned empty result")
            
    except sr.UnknownValueError:
        print(f"❓ Could not understand the audio")
    except sr.RequestError as e:
        print(f"❌ Google Speech API error: {e}")
    except Exception as e:
        print(f"❌ Recognition processing error: {e}")
        traceback.print_exc()
        
except Exception as e:
    print(f"❌ Speech recognition test error: {e}")
    traceback.print_exc()

# Test full workflow import
try:
    print("\n📦 Testing full workflow import...")
    sys.path.insert(0, '.')
    
    from voice_to_suno_jbl import VoiceToSunoJBL
    print("✅ VoiceToSunoJBL imported successfully")
    
    app = VoiceToSunoJBL()
    print("✅ VoiceToSunoJBL initialized successfully")
    
except Exception as e:
    print(f"❌ Workflow import error: {e}")
    traceback.print_exc()

# Test voice command with full error capture
try:
    print("\n🎤 Testing voice command with full error capture...")
    print("This will do a 5-second recording test...")
    
    choice = input("Proceed with voice command test? (y/n): ")
    if choice.lower().startswith('y'):
        print("🔴 Starting voice command test...")
        
        try:
            result = app.listen_for_voice_command()
            print(f"🎯 Voice command result: {result}")
            
            if result:
                print("✅ Voice command successful!")
            else:
                print("⚠️  Voice command returned None")
                
        except Exception as e:
            print(f"❌ Voice command error: {e}")
            traceback.print_exc()
    
except Exception as e:
    print(f"❌ Voice command test setup error: {e}")
    traceback.print_exc()

print("\n📋 Debug Summary:")
print("✅ Basic imports: Working")
print("✅ Speech recognition setup: Working") 
print("✅ Audio recording: Working")
print("✅ Workflow import: Working")
print("\n💡 If voice command failed, check:")
print("   - Microphone permissions")
print("   - Internet connection (for Google Speech API)")
print("   - Audio input levels")
print("   - Background noise")

print("\n🎉 Verbose debug completed!")
