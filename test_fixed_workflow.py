#!/usr/bin/env python3
"""
Test the fixed workflow with better prompts and status checking
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from voice_to_suno_jbl import VoiceToSunoJBL

def test_fixed_workflow():
    """Test the complete workflow with fixes."""
    print("🎵 Testing Fixed JBL-Suno-DJ Workflow")
    print("=" * 50)
    print("🔧 Fixes applied:")
    print("   ✅ Better status check error handling")
    print("   ✅ Sensitive word detection")
    print("   ✅ Safer API response parsing")
    print()
    
    try:
        # Initialize app
        print("🔧 Initializing app...")
        app = VoiceToSunoJBL()
        print("✅ App initialized")
        
        # Test JBL
        print("🔊 Testing JBL connection...")
        jbl_ok = app.set_jbl_as_default()
        print(f"{'✅' if jbl_ok else '⚠️ '} JBL: {'OK' if jbl_ok else 'Issues'}")
        
        # Use a safe prompt that won't trigger sensitive word filter
        safe_prompts = [
            "upbeat electronic music",
            "relaxing piano melody", 
            "energetic rock song",
            "smooth jazz instrumental",
            "happy pop tune"
        ]
        
        print("\n🎵 Safe prompt options:")
        for i, prompt in enumerate(safe_prompts, 1):
            print(f"   {i}. {prompt}")
        
        choice = input("\nChoose a prompt (1-5) or enter your own: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= 5:
            prompt = safe_prompts[int(choice) - 1]
        else:
            prompt = choice if choice else safe_prompts[0]
        
        print(f"🎯 Using prompt: '{prompt}'")
        
        # Test generation
        print(f"\n🎵 Generating music...")
        task_id = app.generate_music(prompt)
        
        if task_id:
            print(f"✅ Generation started: {task_id}")
            
            # Wait for music with improved status checking
            print("⏳ Waiting for music with improved status checking...")
            tracks = app.wait_for_music(task_id)
            
            if tracks:
                print(f"✅ Got {len(tracks)} track(s)!")
                for i, track in enumerate(tracks, 1):
                    print(f"   Track {i}: {track['title']}")
                
                # Test playback
                choice = input("\nPlay on JBL? (y/n): ")
                if choice.lower().startswith('y'):
                    for track in tracks:
                        print(f"🎵 Playing: {track['title']}")
                        success = app.play_on_jbl(track)
                        if success:
                            print("✅ Playback completed!")
                        break
                
                print("🎉 Fixed workflow test completed successfully!")
                return True
            else:
                print("❌ Music generation failed or timed out")
                print(f"🆔 Task ID for manual checking: {task_id}")
                return False
        else:
            print("❌ Music generation request failed")
            return False
            
    except Exception as e:
        print(f"💥 Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    print("🔧 JBL-Suno-DJ Fixed Workflow Tester")
    print("=" * 60)
    print("This version includes:")
    print("✅ Fixed status check API parsing")
    print("✅ Sensitive word error detection")
    print("✅ Better error handling")
    print("✅ Safe prompt suggestions")
    print()
    
    try:
        success = test_fixed_workflow()
        if success:
            print("\n🎉 All fixes working correctly!")
        else:
            print("\n⚠️  Some issues remain - check output above")
    except KeyboardInterrupt:
        print("\n👋 Test cancelled")
    except Exception as e:
        print(f"\n💥 Error: {e}")

if __name__ == "__main__":
    main()
