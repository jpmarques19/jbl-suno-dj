#!/usr/bin/env python3
"""
Test OpenAI API quota and permissions
"""

import requests
import os

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def test_openai_api():
    """Test OpenAI API access and quota."""
    print("🔍 OpenAI API Quota & Permissions Test")
    print("=" * 50)
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ No API key found")
        return False
    
    print(f"🔑 API Key: {'*' * 8}{api_key[-4:]}")
    
    # Test 1: Check API key validity
    print("\n1️⃣ Testing API key validity...")
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Test with models endpoint (lightweight)
        response = requests.get(
            'https://api.openai.com/v1/models',
            headers=headers,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ API key is valid")
            models = response.json()
            whisper_models = [m for m in models['data'] if 'whisper' in m['id']]
            print(f"   🎤 Whisper models available: {len(whisper_models)}")
        elif response.status_code == 401:
            print("   ❌ API key is invalid")
            return False
        elif response.status_code == 429:
            print("   ⚠️  Rate limited or quota exceeded")
            print(f"   Response: {response.text}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        return False
    
    # Test 2: Check account usage/billing
    print("\n2️⃣ Testing account access...")
    try:
        # This endpoint shows usage info
        response = requests.get(
            'https://api.openai.com/v1/usage?date=2024-01-28',
            headers=headers,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Account access working")
        elif response.status_code == 403:
            print("   ⚠️  Account access restricted")
            print("   💡 May need to add payment method")
        else:
            print(f"   Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Usage check failed: {e}")
    
    # Test 3: Try a minimal Whisper request
    print("\n3️⃣ Testing Whisper API access...")
    
    # Create a tiny test audio file (silence)
    import tempfile
    import wave
    
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Create 1 second of silence
        with wave.open(temp_path, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(16000)  # 16kHz
            wav_file.writeframes(b'\x00' * 32000)  # 1 second of silence
        
        # Test Whisper API
        with open(temp_path, 'rb') as audio_file:
            files = {
                'file': ('test.wav', audio_file, 'audio/wav'),
                'model': (None, 'whisper-1')
            }
            
            response = requests.post(
                'https://api.openai.com/v1/audio/transcriptions',
                headers={'Authorization': f'Bearer {api_key}'},
                files=files,
                timeout=30
            )
        
        # Clean up
        os.unlink(temp_path)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Whisper API working!")
            result = response.json()
            print(f"   Result: {result.get('text', 'No text')}")
            return True
        elif response.status_code == 429:
            print("   ❌ Quota exceeded")
            error_data = response.json()
            print(f"   Error: {error_data.get('error', {}).get('message', 'Unknown')}")
            
            # Check error details
            error_type = error_data.get('error', {}).get('type')
            if error_type == 'insufficient_quota':
                print("   💡 Solutions:")
                print("      1. Add payment method: https://platform.openai.com/account/billing")
                print("      2. Check usage: https://platform.openai.com/usage")
                print("      3. Wait if rate limited")
            
            return False
        else:
            print(f"   ❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Whisper test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🔍 OpenAI API Diagnostic Tool")
    print("=" * 40)
    print("This will test your OpenAI API access and identify quota issues.")
    print()
    
    success = test_openai_api()
    
    print("\n📋 Summary:")
    if success:
        print("✅ OpenAI Whisper API is working!")
        print("🚀 You can switch back to Whisper:")
        print("   Edit .env: SPEECH_SERVICE=whisper")
    else:
        print("❌ OpenAI API has issues")
        print("💡 Check the solutions above")
        print("🔄 Using Google Speech as fallback for now")

if __name__ == "__main__":
    main()
