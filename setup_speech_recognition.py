#!/usr/bin/env python3
"""
Setup script for enhanced speech recognition services
"""

import os
import sys

def setup_speech_services():
    """Interactive setup for speech recognition services."""
    print("🎤 Enhanced Speech Recognition Setup")
    print("=" * 60)
    print()
    print("Current speech recognition options:")
    print("1. 🆓 Google Speech (Free) - Basic accuracy")
    print("2. 🏆 OpenAI Whisper API - Excellent accuracy ($0.006/min)")
    print("3. ⚡ Deepgram API - Excellent accuracy, fast ($0.0043/min)")
    print("4. 🔵 Azure Speech - Very good accuracy ($1/hour)")
    print()
    
    # Check current configuration
    env_file = ".env"
    current_config = {}
    
    if os.path.exists(env_file):
        print("📋 Current configuration:")
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    current_config[key] = value
                    if 'API_KEY' in key and value:
                        print(f"   ✅ {key}: {'*' * 8}{value[-4:] if len(value) > 4 else '****'}")
                    elif 'SPEECH_SERVICE' in key:
                        print(f"   🎤 {key}: {value}")
    else:
        print("📋 No configuration file found")
    
    print()
    
    # Service selection
    print("🔧 Choose your preferred speech recognition service:")
    print("1. Google Speech (Free, basic accuracy)")
    print("2. OpenAI Whisper (Best accuracy, $0.006/min)")
    print("3. Deepgram (Excellent accuracy, fast, $0.0043/min)")
    print("4. Keep current setting")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    service_map = {
        "1": "google",
        "2": "whisper", 
        "3": "deepgram"
    }
    
    if choice in service_map:
        selected_service = service_map[choice]
        current_config["SPEECH_SERVICE"] = selected_service
        print(f"✅ Selected: {selected_service}")
        
        # Get API key if needed
        if selected_service == "whisper":
            setup_openai_key(current_config)
        elif selected_service == "deepgram":
            setup_deepgram_key(current_config)
    elif choice == "4":
        print("✅ Keeping current setting")
    else:
        print("❌ Invalid choice")
        return
    
    # Save configuration
    save_config(current_config)
    
    # Test the configuration
    test_choice = input("\n🧪 Test speech recognition? (y/n): ")
    if test_choice.lower().startswith('y'):
        test_speech_recognition()

def setup_openai_key(config):
    """Setup OpenAI API key for Whisper."""
    print("\n🔑 OpenAI Whisper API Setup")
    print("=" * 40)
    print("To use OpenAI Whisper API:")
    print("1. Go to https://platform.openai.com/api-keys")
    print("2. Create a new API key")
    print("3. Copy the key (starts with 'sk-')")
    print()
    
    current_key = config.get("OPENAI_API_KEY", "")
    if current_key:
        print(f"Current key: {'*' * 8}{current_key[-4:]}")
        keep = input("Keep current key? (y/n): ")
        if keep.lower().startswith('y'):
            return
    
    api_key = input("Enter your OpenAI API key: ").strip()
    if api_key.startswith('sk-') and len(api_key) > 20:
        config["OPENAI_API_KEY"] = api_key
        print("✅ OpenAI API key saved")
        print("💰 Cost: ~$0.006 per minute (~$0.10 for 10 seconds)")
    else:
        print("❌ Invalid API key format")

def setup_deepgram_key(config):
    """Setup Deepgram API key."""
    print("\n🔑 Deepgram API Setup")
    print("=" * 40)
    print("To use Deepgram API:")
    print("1. Go to https://console.deepgram.com/")
    print("2. Sign up for free account (includes $200 credit)")
    print("3. Create a new API key")
    print("4. Copy the key")
    print()
    
    current_key = config.get("DEEPGRAM_API_KEY", "")
    if current_key:
        print(f"Current key: {'*' * 8}{current_key[-4:]}")
        keep = input("Keep current key? (y/n): ")
        if keep.lower().startswith('y'):
            return
    
    api_key = input("Enter your Deepgram API key: ").strip()
    if len(api_key) > 20:
        config["DEEPGRAM_API_KEY"] = api_key
        print("✅ Deepgram API key saved")
        print("💰 Cost: ~$0.0043 per minute (~$0.07 for 10 seconds)")
        print("🎁 Free tier includes $200 credit")
    else:
        print("❌ Invalid API key")

def save_config(config):
    """Save configuration to .env file."""
    try:
        with open(".env", "w") as f:
            f.write("# JBL-Suno-DJ Configuration\n")
            f.write("# Speech Recognition Settings\n")
            for key, value in config.items():
                f.write(f"{key}={value}\n")
        print("✅ Configuration saved to .env")
    except Exception as e:
        print(f"❌ Error saving config: {e}")

def test_speech_recognition():
    """Test the configured speech recognition."""
    print("\n🧪 Testing Speech Recognition")
    print("=" * 40)
    
    try:
        # Import and test
        import sys
        sys.path.insert(0, '.')
        
        # Reload environment
        from dotenv import load_dotenv
        load_dotenv()
        
        from voice_to_suno_jbl import VoiceToSunoJBL
        
        print("🔧 Initializing speech recognition...")
        app = VoiceToSunoJBL()
        
        print("✅ Ready for test!")
        print("💡 Say something like 'test speech recognition'")
        
        result = app.listen_for_voice_command()
        
        if result:
            print(f"🎉 Test successful: '{result}'")
        else:
            print("❌ Test failed")
            
    except ImportError:
        print("❌ Missing dependency: pip install python-dotenv")
    except Exception as e:
        print(f"❌ Test error: {e}")

def show_pricing_comparison():
    """Show pricing comparison of services."""
    print("\n💰 Speech Recognition Pricing Comparison")
    print("=" * 60)
    print("Service          | Cost/minute | 10s cost | Accuracy | Speed")
    print("-" * 60)
    print("Google (Free)    | $0.000      | $0.00    | Basic    | Medium")
    print("OpenAI Whisper   | $0.006      | $0.01    | Excellent| Medium")
    print("Deepgram         | $0.0043     | $0.007   | Excellent| Fast")
    print("Azure Speech     | $0.017      | $0.028   | Very Good| Fast")
    print()
    print("💡 Recommendation: OpenAI Whisper for best accuracy")
    print("💡 Alternative: Deepgram for speed + accuracy")

def main():
    """Main setup function."""
    print("🎤 JBL-Suno-DJ Enhanced Speech Recognition")
    print("=" * 60)
    
    while True:
        print("\nChoose an option:")
        print("1. 🔧 Setup speech recognition service")
        print("2. 💰 View pricing comparison")
        print("3. 🧪 Test current configuration")
        print("4. ❌ Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            setup_speech_services()
        elif choice == "2":
            show_pricing_comparison()
        elif choice == "3":
            test_speech_recognition()
        elif choice == "4":
            print("👋 Setup complete!")
            break
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()
