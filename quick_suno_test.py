#!/usr/bin/env python3
"""Quick Suno test with model selection and credit-conscious options."""

import urllib.request
import json
import os

# Configuration
API_KEY = "4e2feeb494648a5f5845dd5b65558544"
BASE_URL = "https://apibox.erweima.ai"
ENDPOINT = "/api/v1/generate"

def test_suno_with_model(model="V3_5", prompt="happy song"):
    """Test Suno API with specific model and prompt."""
    print(f"🎵 Testing Suno API")
    print(f"Model: {model} (cheaper option)")
    print(f"Prompt: '{prompt}' (short to save credits)")
    print("=" * 50)
    
    url = f"{BASE_URL}{ENDPOINT}"
    
    payload = {
        "prompt": prompt,
        "customMode": False,
        "instrumental": False,
        "model": model,
        "callBackUrl": "https://httpbin.org/post"
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}',
        'User-Agent': 'SunoQuickTest/1.0'
    }
    
    print(f"📡 Sending request to: {url}")
    print(f"📦 Model: {model}")
    print(f"💰 Using cheaper model to conserve credits")
    
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        
        print("🚀 Sending request...")
        with urllib.request.urlopen(req, timeout=30) as response:
            response_data = response.read().decode('utf-8')
            result = json.loads(response_data)
            
            print(f"✅ Response Status: {response.getcode()}")
            print(f"📄 Response Data:")
            print(json.dumps(result, indent=2))
            
            if result.get('code') == 200:
                task_id = result.get('data', {}).get('taskId')  # Fixed: API returns 'taskId' not 'task_id'
                print(f"\n🎉 SUCCESS! Music generation started!")
                print(f"🆔 Task ID: {task_id}")
                print(f"⏳ Music is being generated...")
                print(f"💡 You can check the status using the task ID")
                return task_id
            else:
                print(f"\n❌ API Error: {result.get('msg', 'Unknown error')}")
                return None
                
    except urllib.error.HTTPError as e:
        error_data = e.read().decode('utf-8') if e.fp else str(e)
        print(f"❌ HTTP Error {e.code}:")
        try:
            error_json = json.loads(error_data)
            print(json.dumps(error_json, indent=2))
        except:
            print(error_data)
        return None
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        print("💡 This might be a network issue or the API might be temporarily unavailable")
        return None

def main():
    """Main function with model options."""
    print("🎵 Quick Suno API Test (Credit-Conscious)")
    print("=" * 50)
    
    # Model options (from cheapest to most expensive)
    models = {
        "1": ("V3_5", "Chirp V3.5 - Cheaper option"),
        "2": ("V4", "Chirp V4 - Standard option"),
        "3": ("V4_5", "Chirp V4.5 - Premium option")
    }
    
    print("Available models:")
    for key, (model, desc) in models.items():
        print(f"  {key}. {desc}")
    
    # Default to cheapest option
    choice = input("\nChoose model (1-3, default=1 for cheapest): ").strip()
    if choice not in models:
        choice = "1"
    
    selected_model, model_desc = models[choice]
    print(f"Selected: {model_desc}")
    
    # Short prompt options to save credits
    prompts = [
        "happy song",
        "sad melody",
        "rock music",
        "jazz tune",
        "classical piece"
    ]
    
    print(f"\nSample short prompts (to save credits):")
    for i, prompt in enumerate(prompts, 1):
        print(f"  {i}. {prompt}")
    
    custom_prompt = input("\nEnter your prompt (or press Enter for 'happy song'): ").strip()
    if not custom_prompt:
        custom_prompt = "happy song"
    
    print(f"\n💰 Using model {selected_model} with prompt '{custom_prompt}'")
    print("🔄 Starting generation...")
    
    task_id = test_suno_with_model(selected_model, custom_prompt)
    
    if task_id:
        print(f"\n🎉 Test completed successfully!")
        print(f"🆔 Your task ID: {task_id}")
        print(f"📝 Save this ID to check the status later")
    else:
        print(f"\n❌ Test failed - check the error messages above")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Test cancelled by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
