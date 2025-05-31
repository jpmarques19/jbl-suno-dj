#!/usr/bin/env python3
"""
Simple complete workflow test
"""

print("🎵 JBL-Suno-DJ Simple Workflow Test")
print("=" * 50)

try:
    # Test imports
    print("📦 Testing imports...")
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from voice_to_suno_jbl import VoiceToSunoJBL
    print("✅ Imports successful")
    
    # Initialize app
    print("🔧 Initializing app...")
    app = VoiceToSunoJBL()
    print("✅ App initialized")
    
    # Test JBL
    print("🔊 Testing JBL connection...")
    jbl_ok = app.set_jbl_as_default()
    print(f"{'✅' if jbl_ok else '⚠️ '} JBL: {'OK' if jbl_ok else 'Issues'}")
    
    # Test voice (single attempt)
    print("🎤 Testing voice recognition...")
    print("💡 Say something like 'create happy music' when prompted")
    
    choice = input("Ready to test voice? (y/n): ")
    if choice.lower().startswith('y'):
        prompt = app.listen_for_voice_command()
        if prompt:
            print(f"✅ Voice: '{prompt}'")
        else:
            print("❌ Voice failed, using manual input")
            prompt = input("Enter prompt: ") or "happy music"
    else:
        prompt = "happy electronic music"
        print(f"📝 Using default: '{prompt}'")
    
    # Test generation
    print(f"🎵 Generating music: '{prompt}'")
    task_id = app.generate_music(prompt)
    
    if task_id:
        print(f"✅ Generation started: {task_id}")
        
        # Wait for music
        print("⏳ Waiting for music (this may take 2-3 minutes)...")
        tracks = app.wait_for_music(task_id)
        
        if tracks:
            print(f"✅ Got {len(tracks)} track(s)")
            
            # Test playback
            choice = input("Play on JBL? (y/n): ")
            if choice.lower().startswith('y'):
                for track in tracks:
                    print(f"🎵 Playing: {track['title']}")
                    app.play_on_jbl(track)
                    break
            
            print("🎉 Workflow test completed!")
        else:
            print("❌ Music generation timed out")
    else:
        print("❌ Music generation failed")

except Exception as e:
    print(f"💥 Error: {e}")
    import traceback
    traceback.print_exc()
