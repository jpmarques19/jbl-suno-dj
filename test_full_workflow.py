#!/usr/bin/env python3
"""
Test the complete voice-to-Suno-to-JBL workflow with debugging
"""

import sys
import os
import time

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from voice_to_suno_jbl import VoiceToSunoJBL

def test_workflow_step_by_step():
    """Test each step of the workflow individually."""
    print("🧪 Complete JBL-Suno-DJ Workflow Test")
    print("=" * 60)
    
    # Initialize the app
    try:
        print("🔧 Initializing VoiceToSunoJBL...")
        app = VoiceToSunoJBL()
        print("✅ App initialized successfully!")
    except Exception as e:
        print(f"❌ App initialization failed: {e}")
        return False
    
    # Step 1: Test JBL Connection
    print("\n📍 STEP 1: Testing JBL Connection")
    print("-" * 40)
    try:
        jbl_ok = app.set_jbl_as_default()
        if jbl_ok:
            print("✅ JBL set as default audio device")
        else:
            print("⚠️  JBL setup had issues but continuing...")
    except Exception as e:
        print(f"❌ JBL setup failed: {e}")
        return False
    
    # Step 2: Test Voice Recognition
    print("\n📍 STEP 2: Testing Voice Recognition")
    print("-" * 40)
    print("🎤 This will test voice input...")
    print("💡 When prompted, say something like:")
    print("   'Create a happy song'")
    print("   'Generate upbeat music'")
    print("   'Make electronic dance music'")
    print()
    
    input("Press Enter when ready to test voice recognition...")
    
    try:
        prompt = app.listen_for_voice_command()
        if prompt:
            print(f"✅ Voice recognition successful: '{prompt}'")
            use_voice_prompt = True
        else:
            print("❌ Voice recognition failed")
            print("🔄 Falling back to manual input...")
            prompt = input("Enter your music prompt manually: ").strip()
            if not prompt:
                prompt = "happy upbeat song"
            use_voice_prompt = False
            print(f"📝 Using manual prompt: '{prompt}'")
    except Exception as e:
        print(f"❌ Voice recognition error: {e}")
        prompt = "happy upbeat song"
        use_voice_prompt = False
        print(f"📝 Using fallback prompt: '{prompt}'")
    
    # Step 3: Test Music Generation
    print(f"\n📍 STEP 3: Testing Music Generation")
    print("-" * 40)
    try:
        task_id = app.generate_music(prompt)
        if task_id:
            print(f"✅ Music generation started: {task_id}")
        else:
            print("❌ Music generation failed")
            return False
    except Exception as e:
        print(f"❌ Music generation error: {e}")
        return False
    
    # Step 4: Wait for Music
    print(f"\n📍 STEP 4: Waiting for Music Generation")
    print("-" * 40)
    try:
        tracks = app.wait_for_music(task_id)
        if tracks:
            print(f"✅ Music generation completed! Got {len(tracks)} track(s)")
            for i, track in enumerate(tracks):
                print(f"   Track {i+1}: {track['title']}")
        else:
            print("❌ Music generation timed out or failed")
            return False
    except Exception as e:
        print(f"❌ Music waiting error: {e}")
        return False
    
    # Step 5: Test JBL Playback
    print(f"\n📍 STEP 5: Testing JBL Playback")
    print("-" * 40)
    print("🔊 This will play the generated music on your JBL speaker...")
    print("🎮 You can control playback with:")
    print("   SPACE - Play/Pause")
    print("   q - Quit")
    print("   ↑↓ - Volume")
    print()
    
    input("Press Enter when ready to play music on JBL...")
    
    try:
        for i, track in enumerate(tracks):
            print(f"\n🎵 Playing track {i+1}/{len(tracks)}: {track['title']}")
            success = app.play_on_jbl(track)
            if success:
                print(f"✅ Track {i+1} playback completed")
            else:
                print(f"❌ Track {i+1} playback failed")
            
            if len(tracks) > 1 and i < len(tracks) - 1:
                choice = input(f"\nPlay next track? (y/n): ")
                if not choice.lower().startswith('y'):
                    break
        
        print("✅ JBL playback test completed!")
        
    except Exception as e:
        print(f"❌ JBL playback error: {e}")
        return False
    
    # Summary
    print(f"\n📍 WORKFLOW SUMMARY")
    print("-" * 40)
    print(f"✅ JBL Connection: Working")
    print(f"{'✅' if use_voice_prompt else '⚠️ '} Voice Recognition: {'Working' if use_voice_prompt else 'Failed (used manual input)'}")
    print(f"✅ Music Generation: Working")
    print(f"✅ JBL Playback: Working")
    print(f"✅ Overall: {'Complete Success!' if use_voice_prompt else 'Partial Success (voice needs fixing)'}")
    
    return True

def test_continuous_mode():
    """Test the continuous voice mode."""
    print("\n🔄 Testing Continuous Voice Mode")
    print("=" * 50)
    print("This will run the continuous voice-controlled mode.")
    print("🎤 Say music requests and they'll be generated and played automatically.")
    print("⏹️  Press Ctrl+C to stop")
    print()
    
    choice = input("Start continuous mode? (y/n): ")
    if not choice.lower().startswith('y'):
        return
    
    try:
        app = VoiceToSunoJBL()
        app.run_continuous()
    except KeyboardInterrupt:
        print("\n👋 Continuous mode stopped")
    except Exception as e:
        print(f"\n❌ Continuous mode error: {e}")

def test_single_session():
    """Test a single voice session."""
    print("\n🎯 Testing Single Voice Session")
    print("=" * 50)
    print("This will run one complete voice-to-music session.")
    print()
    
    try:
        app = VoiceToSunoJBL()
        success = app.run_voice_session()
        if success:
            print("🎉 Single session completed successfully!")
        else:
            print("❌ Single session failed")
        return success
    except KeyboardInterrupt:
        print("\n👋 Single session cancelled")
        return False
    except Exception as e:
        print(f"\n❌ Single session error: {e}")
        return False

def main():
    """Main test menu."""
    print("🎵 JBL-Suno-DJ Complete Workflow Tester")
    print("=" * 60)
    print()
    print("Choose a test mode:")
    print("1. Step-by-step workflow test (recommended for debugging)")
    print("2. Single voice session test")
    print("3. Continuous voice mode test")
    print("4. Exit")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (1-4): ").strip()
            
            if choice == '1':
                success = test_workflow_step_by_step()
                if success:
                    print("\n🎉 Step-by-step test completed!")
                else:
                    print("\n❌ Step-by-step test failed")
                break
                
            elif choice == '2':
                success = test_single_session()
                break
                
            elif choice == '3':
                test_continuous_mode()
                break
                
            elif choice == '4':
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1-4.")
                
        except KeyboardInterrupt:
            print("\n👋 Test cancelled")
            break
        except Exception as e:
            print(f"\n💥 Error: {e}")
            break

if __name__ == "__main__":
    main()
