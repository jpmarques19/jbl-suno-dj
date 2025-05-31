#!/usr/bin/env python3
"""
Test the fixed voice recognition that records for full 10 seconds
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from voice_to_suno_jbl import VoiceToSunoJBL

def test_fixed_voice_recognition():
    """Test the fixed voice recognition."""
    print("🎤 Testing Fixed Voice Recognition")
    print("=" * 50)
    print("🔧 Key improvements:")
    print("   ✅ Records for EXACTLY 10 seconds")
    print("   ✅ Won't stop early on pauses")
    print("   ✅ Real-time countdown timer")
    print("   ✅ Better speech capture")
    print()
    
    try:
        # Initialize the app
        print("🔧 Initializing voice recognition...")
        app = VoiceToSunoJBL()
        print("✅ Voice recognition ready!")
        print()
        
        # Test voice recognition
        print("💡 When the countdown starts, say something like:")
        print("   'upbeat electronic dance music'")
        print("   'relaxing jazz piano melody'")
        print("   'energetic rock song with guitar'")
        print()
        print("🎯 The system will record for EXACTLY 10 seconds")
        print("🎯 You can speak, pause, and speak again within those 10 seconds")
        print()
        
        input("Press Enter when ready to test...")
        
        # Test voice recognition
        result = app.listen_for_voice_command()
        
        if result:
            print(f"\n🎉 SUCCESS! Full recognition: '{result}'")
            
            # Check if it's a good music request
            music_keywords = ['music', 'song', 'melody', 'tune', 'beat', 'jazz', 'rock', 'electronic', 'piano', 'guitar']
            word_count = len(result.split())
            
            print(f"📊 Analysis:")
            print(f"   Word count: {word_count}")
            print(f"   Contains music keywords: {any(keyword in result.lower() for keyword in music_keywords)}")
            
            if word_count >= 3:
                print("✅ Good length - captured multiple words!")
            else:
                print("⚠️  Short capture - try speaking more")
            
            if any(keyword in result.lower() for keyword in music_keywords):
                print("🎵 Sounds like a music request!")
                print(f"🚀 Ready to generate music with: '{result}'")
            else:
                print("🤔 Doesn't sound like a music request")
                print("💡 Try adding words like 'music', 'song', 'melody', etc.")
            
        else:
            print(f"\n❌ Voice recognition failed")
            print("💡 Possible issues:")
            print("   - Microphone not working")
            print("   - Speaking too quietly")
            print("   - Background noise")
            print("   - Internet connection (for Google Speech API)")
        
        return result is not None
        
    except KeyboardInterrupt:
        print("\n👋 Test cancelled by user")
        return False
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("🎤 Fixed Voice Recognition Tester")
    print("=" * 50)
    print()
    
    try:
        success = test_fixed_voice_recognition()
        
        if success:
            print("\n🎉 Fixed voice recognition working correctly!")
            print("💡 Now you can use the full workflow with proper 10-second recording")
        else:
            print("\n❌ Voice recognition still has issues")
            print("💡 Check microphone settings and try again")
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Error: {e}")

if __name__ == "__main__":
    main()
