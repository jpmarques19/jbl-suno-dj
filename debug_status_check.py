#!/usr/bin/env python3
"""
Debug the status check API to see what's wrong
"""

import requests
import json
import time

# Configuration
API_KEY = "4e2feeb494648a5f5845dd5b65558544"
BASE_URL = "https://apibox.erweima.ai"

# Use the task ID from the recent test
TASK_ID = "0a578ebf46b99f6b2bf0b3a2a3e9088a"

def debug_status_endpoint():
    """Debug the status check endpoint."""
    print("🔍 Debugging Suno Status Check API")
    print("=" * 50)
    print(f"🆔 Task ID: {TASK_ID}")
    print(f"🔗 Base URL: {BASE_URL}")
    print()
    
    session = requests.Session()
    session.headers.update({
        'Authorization': f'Bearer {API_KEY}',
        'User-Agent': 'DebugStatusCheck/1.0'
    })
    
    url = f"{BASE_URL}/api/v1/generate/record-info?taskId={TASK_ID}"
    print(f"📡 Full URL: {url}")
    print()
    
    try:
        print("🚀 Making status check request...")
        response = session.get(url, timeout=30)
        
        print(f"📊 HTTP Status Code: {response.status_code}")
        print(f"📋 Response Headers:")
        for key, value in response.headers.items():
            print(f"   {key}: {value}")
        print()
        
        print(f"📄 Raw Response Text:")
        raw_text = response.text
        print(f"   Length: {len(raw_text)} characters")
        print(f"   Content: {raw_text[:500]}...")
        print()
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ JSON Parse Successful")
                print(f"📋 Parsed JSON Structure:")
                print(json.dumps(result, indent=2))
                print()
                
                # Analyze the structure
                print(f"🔍 Structure Analysis:")
                print(f"   Type: {type(result)}")
                
                if isinstance(result, dict):
                    print(f"   Keys: {list(result.keys())}")
                    
                    code = result.get('code')
                    print(f"   Code: {code}")
                    
                    data = result.get('data')
                    print(f"   Data type: {type(data)}")
                    
                    if data is None:
                        print("   ❌ Data is None - this is the problem!")
                        print(f"   Message: {result.get('msg', 'No message')}")
                    elif isinstance(data, dict):
                        print(f"   Data keys: {list(data.keys())}")
                        
                        # Check for sunoData
                        response_data = data.get('response', {})
                        suno_data = response_data.get('sunoData', [])
                        print(f"   SunoData type: {type(suno_data)}")
                        print(f"   SunoData length: {len(suno_data) if suno_data else 0}")
                        
                        if suno_data:
                            print(f"   First track keys: {list(suno_data[0].keys()) if suno_data[0] else 'Empty'}")
                    elif isinstance(data, list):
                        print(f"   Data length: {len(data)}")
                        if data:
                            print(f"   First item type: {type(data[0])}")
                            if isinstance(data[0], dict):
                                print(f"   First item keys: {list(data[0].keys())}")
                
                return result
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON Parse Failed: {e}")
                return None
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Failed: {e}")
        return None

def test_new_generation():
    """Generate a new song and immediately check its status."""
    print("\n🎵 Testing New Generation + Status Check")
    print("=" * 50)
    
    session = requests.Session()
    session.headers.update({
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
        'User-Agent': 'DebugStatusCheck/1.0'
    })
    
    # Generate new music
    print("🚀 Generating new music...")
    gen_url = f"{BASE_URL}/api/v1/generate"
    payload = {
        "prompt": "debug status check song",
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
            print(f"📄 Generation Response:")
            print(json.dumps(result, indent=2))
            
            if result.get('code') == 200:
                new_task_id = result.get('data', {}).get('taskId')
                print(f"✅ New Task ID: {new_task_id}")
                
                # Wait a bit and check status
                print(f"\n⏳ Waiting 10 seconds before status check...")
                time.sleep(10)
                
                print(f"📡 Checking status for new task...")
                status_url = f"{BASE_URL}/api/v1/generate/record-info?taskId={new_task_id}"
                status_response = session.get(status_url, timeout=30)
                
                print(f"📊 Status Check Code: {status_response.status_code}")
                print(f"📄 Status Response:")
                print(status_response.text[:1000])
                
                if status_response.status_code == 200:
                    status_result = status_response.json()
                    print(f"📋 Status JSON:")
                    print(json.dumps(status_result, indent=2))
                
                return new_task_id
            else:
                print(f"❌ Generation failed: {result.get('msg')}")
        else:
            print(f"❌ Generation HTTP error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Generation test failed: {e}")
    
    return None

def main():
    """Main debug function."""
    print("🔍 Suno API Status Check Debugger")
    print("=" * 60)
    
    # Debug existing task
    print("1️⃣ Debugging existing task status...")
    debug_status_endpoint()
    
    # Test new generation
    print("\n2️⃣ Testing new generation...")
    new_task = test_new_generation()
    
    print(f"\n📋 Debug Summary:")
    print(f"   Original Task: {TASK_ID}")
    print(f"   New Task: {new_task}")
    print(f"   Check these task IDs manually at: https://sunoapi.org/dashboard")

if __name__ == "__main__":
    main()
