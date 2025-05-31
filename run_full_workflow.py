#!/usr/bin/env python3
"""
Simple, working full workflow runner
"""

import subprocess
import sys
import os

def run_workflow():
    """Run the complete voice-to-Suno-to-JBL workflow."""
    print("🎵 JBL-Suno-DJ Full Workflow")
    print("=" * 50)
    print("This will run the complete workflow:")
    print("1. 🎤 Voice recognition (with countdown timer)")
    print("2. 🎵 Music generation via Suno API")
    print("3. 🔊 Playback on JBL Flip Essentials")
    print()
    
    # Check if virtual environment exists
    venv_python = ".venv/bin/python"
    if not os.path.exists(venv_python):
        print("❌ Virtual environment not found!")
        print("💡 Run this first:")
        print("   python3 -m venv .venv")
        print("   source .venv/bin/activate")
        print("   pip install speechrecognition pyaudio requests")
        return False
    
    # Check if JBL is connected
    try:
        result = subprocess.run(['pactl', 'list', 'short', 'sinks'], 
                              capture_output=True, text=True, timeout=5)
        if "bluez_output.04_CB_88_B8_CF_72.1" not in result.stdout:
            print("❌ JBL Flip Essentials not found!")
            print("💡 Make sure your JBL speaker is:")
            print("   - Powered on")
            print("   - Connected via Bluetooth")
            return False
        else:
            print("✅ JBL Flip Essentials detected")
    except:
        print("⚠️  Could not check JBL status, continuing anyway...")
    
    print()
    choice = input("🚀 Start the full workflow? (y/n): ")
    if not choice.lower().startswith('y'):
        print("👋 Cancelled")
        return False
    
    print("\n🎯 Starting workflow...")
    print("💡 ALSA warnings are normal and can be ignored")
    print("💡 Speak clearly when prompted")
    print("💡 Use phrases like 'upbeat music' or 'rock song'")
    print()
    
    try:
        # Run the voice-to-Suno-to-JBL workflow
        cmd = [venv_python, "-c", """
import sys
import os
sys.path.insert(0, '.')

try:
    from voice_to_suno_jbl import VoiceToSunoJBL
    
    print("🔧 Initializing JBL-Suno-DJ...")
    app = VoiceToSunoJBL()
    
    print("✅ Ready! Running single voice session...")
    print()
    
    success = app.run_voice_session()
    
    if success:
        print("\\n🎉 Workflow completed successfully!")
    else:
        print("\\n❌ Workflow had issues")
        
except Exception as e:
    print(f"💥 Error: {e}")
    import traceback
    traceback.print_exc()
"""]
        
        # Run the workflow
        result = subprocess.run(cmd, cwd=os.getcwd())
        
        if result.returncode == 0:
            print("\n✅ Workflow completed!")
        else:
            print(f"\n⚠️  Workflow ended with code {result.returncode}")
        
        return True
        
    except KeyboardInterrupt:
        print("\n👋 Workflow cancelled by user")
        return False
    except Exception as e:
        print(f"\n💥 Error running workflow: {e}")
        return False

def run_manual_test():
    """Run a manual test with text input instead of voice."""
    print("\n🔧 Manual Test Mode")
    print("=" * 30)
    print("This will skip voice recognition and use text input")
    print()
    
    prompt = input("Enter your music prompt: ").strip()
    if not prompt:
        prompt = "upbeat electronic music"
    
    print(f"🎵 Using prompt: '{prompt}'")
    
    venv_python = ".venv/bin/python"
    
    try:
        cmd = [venv_python, "-c", f"""
import sys
import os
sys.path.insert(0, '.')

try:
    from voice_to_suno_jbl import VoiceToSunoJBL
    
    print("🔧 Initializing app...")
    app = VoiceToSunoJBL()
    
    # Set JBL as default
    app.set_jbl_as_default()
    
    # Generate music
    print("🎵 Generating music...")
    task_id = app.generate_music("{prompt}")
    
    if task_id:
        print(f"✅ Generation started: {{task_id}}")
        
        # Wait for music
        tracks = app.wait_for_music(task_id)
        
        if tracks:
            print(f"✅ Got {{len(tracks)}} track(s)!")
            
            # Play on JBL
            for track in tracks:
                print(f"🎵 Playing: {{track['title']}}")
                app.play_on_jbl(track)
                break
        else:
            print("❌ Music generation failed")
    else:
        print("❌ Generation request failed")
        
except Exception as e:
    print(f"💥 Error: {{e}}")
    import traceback
    traceback.print_exc()
"""]
        
        result = subprocess.run(cmd, cwd=os.getcwd())
        return result.returncode == 0
        
    except Exception as e:
        print(f"💥 Manual test error: {e}")
        return False

def main():
    """Main menu."""
    print("🎵 JBL-Suno-DJ Workflow Runner")
    print("=" * 50)
    print()
    print("Choose an option:")
    print("1. 🎤 Full workflow (voice → music → JBL)")
    print("2. ⌨️  Manual test (text → music → JBL)")
    print("3. 🔧 Check system requirements")
    print("4. ❌ Exit")
    print()
    
    while True:
        try:
            choice = input("Enter choice (1-4): ").strip()
            
            if choice == '1':
                run_workflow()
                break
            elif choice == '2':
                run_manual_test()
                break
            elif choice == '3':
                check_requirements()
            elif choice == '4':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-4.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

def check_requirements():
    """Check system requirements."""
    print("\n🔍 System Requirements Check")
    print("=" * 40)
    
    # Check Python
    print(f"🐍 Python: {sys.version}")
    
    # Check virtual environment
    if os.path.exists(".venv/bin/python"):
        print("✅ Virtual environment: Found")
    else:
        print("❌ Virtual environment: Missing")
        print("   Run: python3 -m venv .venv")
    
    # Check dependencies
    try:
        import speech_recognition
        print("✅ SpeechRecognition: Installed")
    except ImportError:
        print("❌ SpeechRecognition: Missing")
        print("   Run: pip install speechrecognition")
    
    try:
        import requests
        print("✅ Requests: Installed")
    except ImportError:
        print("❌ Requests: Missing")
        print("   Run: pip install requests")
    
    # Check JBL
    try:
        result = subprocess.run(['pactl', 'list', 'short', 'sinks'], 
                              capture_output=True, text=True, timeout=5)
        if "bluez_output.04_CB_88_B8_CF_72.1" in result.stdout:
            print("✅ JBL Flip Essentials: Connected")
        else:
            print("❌ JBL Flip Essentials: Not found")
    except:
        print("⚠️  JBL check: Could not verify")
    
    # Check audio players
    players = ['mpv', 'vlc', 'mplayer', 'ffplay']
    found_player = False
    for player in players:
        try:
            subprocess.run([player, '--version'], 
                         capture_output=True, timeout=2)
            print(f"✅ Audio player: {player}")
            found_player = True
            break
        except:
            continue
    
    if not found_player:
        print("❌ Audio player: None found")
        print("   Install: sudo apt install mpv")
    
    print()

if __name__ == "__main__":
    main()
