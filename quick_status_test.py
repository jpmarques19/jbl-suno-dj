#!/usr/bin/env python3
"""
Quick test of the status check fixes
"""

import requests
import json

# Configuration
API_KEY = "4e2feeb494648a5f5845dd5b65558544"
BASE_URL = "https://apibox.erweima.ai"

def test_generation_and_status():
    """Test generation and status check with safe prompt."""
    print("🧪 Quick Status Check Test")
    print("=" * 40)
    
    session = requests.Session()
    session.headers.update({
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    })
    
    # Generate with safe prompt
    print("🎵 Generating music with safe prompt...")
    gen_url = f"{BASE_URL}/api/v1/generate"
    payload = {
        "prompt": "upbeat electronic music",  # Safe prompt
        "customMode": False,
        "instrumental": False,
        "model": "V3_5",
        "callBackUrl": "https://httpbin.org/post"
    }
    
    try:
        response = session.post(gen_url, json=payload, timeout=30)
        print(f"📊 Generation Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Generation Response:")
            print(json.dumps(result, indent=2))
            
            if result.get('code') == 200:
                task_id = result.get('data', {}).get('taskId')
                print(f"🆔 Task ID: {task_id}")
                
                # Test status check immediately
                print(f"\n📡 Testing status check...")
                status_url = f"{BASE_URL}/api/v1/generate/record-info?taskId={task_id}"
                status_response = session.get(status_url, timeout=30)
                
                print(f"📊 Status Code: {status_response.status_code}")
                
                if status_response.status_code == 200:
                    status_result = status_response.json()
                    print(f"📄 Status Response:")
                    print(json.dumps(status_result, indent=2))
                    
                    # Test our parsing logic
                    if status_result.get('code') == 200:
                        data = status_result.get('data', {})
                        status = data.get('status')
                        print(f"\n🔍 Parsing Test:")
                        print(f"   Status: {status}")
                        
                        if status == 'SENSITIVE_WORD_ERROR':
                            print(f"   ❌ Sensitive word detected!")
                        elif status == 'FAILED':
                            print(f"   ❌ Generation failed!")
                        else:
                            response_data = data.get('response')
                            print(f"   Response data type: {type(response_data)}")
                            
                            if response_data is None:
                                print(f"   ⏳ Still pending...")
                            elif isinstance(response_data, dict):
                                suno_data = response_data.get('sunoData')
                                print(f"   SunoData type: {type(suno_data)}")
                                
                                if suno_data is None:
                                    print(f"   ⏳ Still processing...")
                                elif isinstance(suno_data, list):
                                    print(f"   ✅ Got {len(suno_data)} tracks")
                                    for i, track in enumerate(suno_data):
                                        if isinstance(track, dict):
                                            title = track.get('title', 'Untitled')
                                            stream_url = track.get('streamAudioUrl')
                                            print(f"     Track {i+1}: {title}")
                                            print(f"     Stream: {'✅' if stream_url and stream_url != 'null' else '⏳'}")
                    
                    print(f"\n✅ Status check parsing successful!")
                    return task_id
                else:
                    print(f"❌ Status check failed: {status_response.text}")
            else:
                print(f"❌ Generation API error: {result.get('msg')}")
        else:
            print(f"❌ Generation failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    return None

if __name__ == "__main__":
    test_generation_and_status()
