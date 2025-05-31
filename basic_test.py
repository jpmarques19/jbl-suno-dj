#!/usr/bin/env python3
"""Basic test without external dependencies."""

import urllib.request
import urllib.parse
import json
import os

def test_basic():
    """Basic test function."""
    print("🧪 Basic Python Test")
    print("=" * 30)
    
    # Test environment
    print(f"Python version: {os.sys.version}")
    print(f"Current directory: {os.getcwd()}")
    
    # Test .env file
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"✅ .env file exists")
        with open(env_file, 'r') as f:
            content = f.read()
            if "SUNO_COOKIE=" in content:
                cookie_line = [line for line in content.split('\n') if line.startswith('SUNO_COOKIE=')][0]
                cookie = cookie_line.split('=', 1)[1]
                print(f"✅ Cookie found: {len(cookie)} characters")
                print(f"Cookie preview: {cookie[:50]}...")
                return cookie
            else:
                print("❌ SUNO_COOKIE not found in .env")
    else:
        print("❌ .env file not found")
    
    return None

def test_simple_request(cookie):
    """Test a simple HTTP request."""
    print("\n🌐 Testing simple HTTP request...")
    
    # Test a simple endpoint
    url = "https://httpbin.org/get"
    
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read().decode('utf-8')
            result = json.loads(data)
            print(f"✅ HTTP request successful")
            print(f"Response origin: {result.get('origin', 'unknown')}")
            return True
            
    except Exception as e:
        print(f"❌ HTTP request failed: {e}")
        return False

if __name__ == "__main__":
    try:
        cookie = test_basic()
        if cookie:
            test_simple_request(cookie)
            print("\n🎉 Basic tests completed!")
        else:
            print("\n❌ Cookie test failed")
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()
