#!/usr/bin/env python3
"""
Test OpenAI Whisper speech recognition
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, '.')

def test_whisper_setup():
    """Test OpenAI Whisper setup and configuration."""
    print("🎤 OpenAI Whisper Speech Recognition Test")
    print("=" * 60)
    
    # Check environment variables
    print("🔧 Checking configuration...")
    
    # Load environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment loaded")
    except ImportError:
        print("⚠️  python-dotenv not installed (optional)")
    
    # Check API key
    openai_key = os.getenv("OPENAI_API_KEY")
    speech_service = os.getenv("SPEECH_SERVICE", "google")
    
    print(f"📋 Speech service: {speech_service}")
    
    if openai_key:
        if openai_key.startswith("sk-") and len(openai_key) > 20:
            print(f"✅ OpenAI API key: {'*' * 8}{openai_key[-4:]}")
        elif openai_key == "your-openai-api-key-here":
            print("❌ OpenAI API key: Not configured (placeholder)")
            print("💡 Get your API key from: https://platform.openai.com/api-keys")
            print("💡 Update the .env file with your real API key")
            return False
        else:
            print("❌ OpenAI API key: Invalid format")
            return False
    else:
        print("❌ OpenAI API key: Not found")
        print("💡 Add OPENAI_API_KEY to your .env file")
        return False
    
    print()
    
    # Test speech recognition
    print("🧪 Testing Whisper speech recognition...")
    
    try:
        from voice_to_suno_jbl import VoiceToSunoJBL
        
        print("🔧 Initializing app...")
        app = VoiceToSunoJBL()
        
        print("✅ App initialized successfully!")
        print()
        
        # Test voice recognition
        print("🎤 Voice Recognition Test")
        print("=" * 30)
        print("💡 When prompted, say something like:")
        print("   'Create upbeat electronic music'")
        print("   'Generate a jazz piano melody'")
        print("   'Make energetic rock music'")
        print()
        
        choice = input("Ready to test Whisper? (y/n): ")
        if not choice.lower().startswith('y'):
            print("👋 Test skipped")
            return True
        
        print("🔴 Starting voice recognition test...")
        result = app.listen_for_voice_command()
        
        if result:
            print(f"\n🎉 Whisper SUCCESS!")
            print(f"📝 Recognized: '{result}'")
            
            # Analyze result quality
            word_count = len(result.split())
            has_punctuation = any(p in result for p in '.!?')
            has_capitals = any(c.isupper() for c in result)
            
            print(f"\n📊 Quality Analysis:")
            print(f"   Words: {word_count}")
            print(f"   Punctuation: {'✅' if has_punctuation else '❌'}")
            print(f"   Capitalization: {'✅' if has_capitals else '❌'}")
            
            if word_count >= 3 and (has_punctuation or has_capitals):
                print("🏆 Excellent quality recognition!")
            elif word_count >= 2:
                print("✅ Good recognition!")
            else:
                print("⚠️  Short recognition - try speaking more")
            
            return True
        else:
            print(f"\n❌ Whisper test failed")
            print("💡 Possible issues:")
            print("   - Invalid API key")
            print("   - Network connection")
            print("   - Microphone not working")
            print("   - Speaking too quietly")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_whisper_info():
    """Show information about OpenAI Whisper."""
    print("\n🎯 OpenAI Whisper Information")
    print("=" * 40)
    print("✅ Advantages:")
    print("   - Excellent accuracy (90%+ vs 60-70% Google)")
    print("   - Handles accents and background noise")
    print("   - Proper punctuation and capitalization")
    print("   - Great with music terminology")
    print("   - Consistent, reliable results")
    print()
    print("💰 Cost:")
    print("   - $0.006 per minute")
    print("   - ~$0.01 for 10-second recording")
    print("   - Very affordable for the quality")
    print()
    print("🔗 Setup:")
    print("   1. Get API key: https://platform.openai.com/api-keys")
    print("   2. Update .env file: OPENAI_API_KEY=sk-your-key")
    print("   3. Set service: SPEECH_SERVICE=whisper")

def main():
    """Main test function."""
    print("🎤 OpenAI Whisper Setup & Test")
    print("=" * 50)
    
    try:
        success = test_whisper_setup()
        
        if success:
            print("\n🎉 Whisper is ready!")
            print("💡 You can now use the full workflow with excellent speech recognition")
            print("🚀 Run: python3 run_full_workflow.py")
        else:
            print("\n❌ Whisper setup incomplete")
            show_whisper_info()
        
    except KeyboardInterrupt:
        print("\n👋 Test cancelled")
    except Exception as e:
        print(f"\n💥 Error: {e}")

if __name__ == "__main__":
    main()
