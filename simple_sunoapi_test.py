#!/usr/bin/env python3
"""Simple test of SunoAPI.org"""

import urllib.request
import json

# Configuration
API_KEY = "4e2feeb494648a5f5845dd5b65558544"
BASE_URL = "https://apibox.erweima.ai"
ENDPOINT = "/api/v1/generate"

def test_api():
    """Test the SunoAPI.org service."""
    print("🧪 Testing SunoAPI.org")
    print("=" * 30)
    
    url = f"{BASE_URL}{ENDPOINT}"
    
    payload = {
        "prompt": "A peaceful acoustic guitar melody",
        "customMode": False,
        "instrumental": False,
        "model": "V3_5",
        "callBackUrl": "https://httpbin.org/post"
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}',
        'User-Agent': 'SunoPOC/1.0'
    }
    
    print(f"📡 URL: {url}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    print(f"🔑 API Key: {API_KEY[:10]}...")
    
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        
        print("🚀 Sending request...")
        with urllib.request.urlopen(req, timeout=30) as response:
            response_data = response.read().decode('utf-8')
            result = json.loads(response_data)
            
            print(f"✅ Status: {response.getcode()}")
            print(f"📄 Response: {json.dumps(result, indent=2)}")
            
            if result.get('code') == 200:
                task_id = result.get('data', {}).get('task_id')
                print(f"🎉 Success! Task ID: {task_id}")
                return True
            else:
                print(f"❌ API Error: {result.get('msg', 'Unknown error')}")
                return False
                
    except urllib.error.HTTPError as e:
        error_data = e.read().decode('utf-8') if e.fp else str(e)
        print(f"❌ HTTP Error {e.code}: {error_data}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_api()
