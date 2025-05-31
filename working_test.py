#!/usr/bin/env python3
"""Working test that successfully generates music."""

import urllib.request
import json
import time

# Configuration
API_KEY = "4e2feeb494648a5f5845dd5b65558544"
BASE_URL = "https://apibox.erweima.ai"

def generate_music(prompt="rock music"):
    """Generate music and return task ID."""
    print(f"🎵 Generating music with prompt: '{prompt}'")
    print(f"💰 Using V3_5 model (cheaper option)")
    
    url = f"{BASE_URL}/api/v1/generate"
    
    payload = {
        "prompt": prompt,
        "customMode": False,
        "instrumental": False,
        "model": "V3_5",
        "callBackUrl": "https://httpbin.org/post"
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}',
        'User-Agent': 'SunoTest/1.0'
    }
    
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if result.get('code') == 200:
                task_id = result.get('data', {}).get('taskId')
                print(f"✅ Success! Task ID: {task_id}")
                return task_id
            else:
                print(f"❌ Error: {result.get('msg')}")
                return None
                
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def check_status(task_id):
    """Check the status of a music generation task."""
    print(f"🔍 Checking status for task: {task_id}")

    # Correct endpoint from documentation
    url = f"{BASE_URL}/api/v1/generate/record-info?taskId={task_id}"

    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'User-Agent': 'SunoTest/1.0'
    }

    try:
        req = urllib.request.Request(url, headers=headers, method='GET')

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))

            if result.get('code') == 200:
                return result.get('data')
            else:
                print(f"❌ Status check error: {result.get('msg')}")
                return None

    except Exception as e:
        print(f"❌ Status check failed: {e}")
        return None

def main():
    """Main test function."""
    print("🎵 Suno API Working Test")
    print("=" * 40)
    
    # Generate music
    task_id = generate_music("upbeat rock song")
    
    if not task_id:
        print("❌ Generation failed")
        return
    
    print(f"\n⏳ Waiting for music generation...")
    print(f"🆔 Task ID: {task_id}")
    
    # Check status a few times
    for attempt in range(5):
        print(f"\n📡 Status check #{attempt + 1}")
        status_data = check_status(task_id)
        
        if status_data:
            print(f"📄 Status response:")
            print(json.dumps(status_data, indent=2))
            
            # Check if we have audio URLs
            if isinstance(status_data, list) and len(status_data) > 0:
                for i, track in enumerate(status_data):
                    audio_url = track.get('audio_url')
                    if audio_url:
                        print(f"🎵 Track {i+1} ready: {audio_url}")
                        return True
            elif isinstance(status_data, dict):
                audio_url = status_data.get('audio_url')
                if audio_url:
                    print(f"🎵 Music ready: {audio_url}")
                    return True
        
        if attempt < 4:  # Don't wait after the last attempt
            print("⏳ Still generating... waiting 10 seconds")
            time.sleep(10)
    
    print(f"\n⚠️ Music generation may still be in progress")
    print(f"🆔 Save this task ID to check later: {task_id}")
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Test interrupted")
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()
