#!/usr/bin/env python3
"""Test the Python environment and Suno API connectivity."""

import sys
import os

def test_imports():
    """Test all required imports."""
    print("🔍 Testing imports...")
    
    try:
        import requests
        print("✅ requests imported")
    except ImportError as e:
        print(f"❌ requests failed: {e}")
        return False
    
    try:
        import json
        print("✅ json imported")
    except ImportError as e:
        print(f"❌ json failed: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv imported")
    except ImportError as e:
        print(f"❌ python-dotenv failed: {e}")
        return False
    
    try:
        from rich.console import Console
        print("✅ rich imported")
    except ImportError as e:
        print(f"❌ rich failed: {e}")
        return False
    
    return True

def test_environment():
    """Test environment variables."""
    print("\n🔍 Testing environment...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('SUNO_API_KEY')
        if api_key and api_key != "your_api_key_here":
            print(f"✅ API key loaded: {api_key[:10]}...")
            return api_key
        else:
            print("❌ API key not found or invalid")
            return None
    except Exception as e:
        print(f"❌ Environment test failed: {e}")
        return None

def test_api_connectivity(api_key):
    """Test API connectivity."""
    print("\n🔍 Testing API connectivity...")
    
    try:
        import requests
        import json
        
        url = 'https://apibox.erweima.ai/api/v1/generate'
        payload = {
            'prompt': 'test song',
            'customMode': False,
            'instrumental': False,
            'model': 'V3_5',
            'callBackUrl': 'https://httpbin.org/post'
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        print("🚀 Making API request...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📄 Response: {result}")
            
            if result.get('code') == 200:
                task_id = result.get('data', {}).get('taskId')
                print(f"🎉 SUCCESS! Generated task ID: {task_id}")
                return task_id
            else:
                print(f"❌ API Error: {result.get('msg', 'Unknown error')}")
                return None
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return None

def test_status_check(api_key, task_id):
    """Test status checking."""
    print(f"\n🔍 Testing status check for task: {task_id}")
    
    try:
        import requests
        import time
        
        # Wait a bit before checking
        print("⏳ Waiting 10 seconds before status check...")
        time.sleep(10)
        
        url = f'https://apibox.erweima.ai/api/v1/generate/record-info?taskId={task_id}'
        headers = {
            'Authorization': f'Bearer {api_key}'
        }
        
        print("🚀 Checking status...")
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"📡 Status response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📄 Status data: {result}")
            
            if result.get('code') == 200:
                data = result.get('data')
                print(f"✅ Status check successful!")
                return data
            else:
                print(f"❌ Status API Error: {result.get('msg', 'Unknown error')}")
                return None
        else:
            print(f"❌ Status HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        return None

def main():
    """Main test function."""
    print("🧪 Environment and API Test Suite")
    print("=" * 50)
    
    # Test 1: Imports
    if not test_imports():
        print("\n❌ Import tests failed")
        return False
    
    # Test 2: Environment
    api_key = test_environment()
    if not api_key:
        print("\n❌ Environment tests failed")
        return False
    
    # Test 3: API connectivity
    task_id = test_api_connectivity(api_key)
    if not task_id:
        print("\n❌ API connectivity tests failed")
        return False
    
    # Test 4: Status check
    status_data = test_status_check(api_key, task_id)
    
    print("\n🎉 All tests completed!")
    print(f"🆔 Generated task ID: {task_id}")
    
    if status_data:
        print("✅ Status check working")
    else:
        print("⚠️ Status check had issues (music might still be generating)")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 Environment is working correctly!")
        else:
            print("\n❌ Environment has issues")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Test cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
