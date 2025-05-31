#!/usr/bin/env python3
"""Working Suno POC using direct API calls."""

import urllib.request
import urllib.parse
import json
import os
import time
import sys

def load_cookie():
    """Load cookie from .env file."""
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            content = f.read()
            for line in content.split('\n'):
                if line.startswith('SUNO_COOKIE='):
                    return line.split('=', 1)[1].strip()
    return None

def make_request(url, method='GET', data=None, cookie=None):
    """Make HTTP request with proper headers."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://app.suno.ai/',
        'Origin': 'https://app.suno.ai'
    }
    
    if cookie:
        headers['Cookie'] = cookie
    
    if data:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(data).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            response_data = response.read().decode('utf-8')
            return {
                'status_code': response.getcode(),
                'data': json.loads(response_data) if response_data else None,
                'success': True
            }
    except urllib.error.HTTPError as e:
        error_data = e.read().decode('utf-8') if e.fp else str(e)
        return {
            'status_code': e.code,
            'data': error_data,
            'success': False,
            'error': str(e)
        }
    except Exception as e:
        return {
            'status_code': 0,
            'data': None,
            'success': False,
            'error': str(e)
        }

def test_suno_endpoints(cookie):
    """Test different Suno API endpoints."""
    print("🔍 Testing Suno API endpoints...")
    
    endpoints = [
        "https://studio-api.suno.ai/api/feed/",
        "https://clerk.suno.com/v1/me",
        "https://studio-api.suno.ai/api/billing/info/",
        "https://app.suno.ai/api/feed/",
    ]
    
    for endpoint in endpoints:
        print(f"\n📡 Testing: {endpoint}")
        result = make_request(endpoint, cookie=cookie)
        
        print(f"Status: {result['status_code']}")
        if result['success']:
            print("✅ Success!")
            if result['data']:
                print(f"Response keys: {list(result['data'].keys()) if isinstance(result['data'], dict) else 'Not a dict'}")
                return endpoint
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
            if result['data']:
                print(f"Response: {str(result['data'])[:200]}...")
    
    return None

def generate_music_simple(cookie, prompt):
    """Try to generate music using simple approach."""
    print(f"\n🎵 Attempting to generate music...")
    print(f"Prompt: '{prompt}'")
    
    # Try different generation endpoints
    generation_endpoints = [
        "https://studio-api.suno.ai/api/generate/v2/",
        "https://studio-api.suno.ai/api/generate/",
        "https://app.suno.ai/api/generate/",
    ]
    
    payload = {
        "prompt": prompt,
        "make_instrumental": False,
        "wait_audio": False
    }
    
    for endpoint in generation_endpoints:
        print(f"\n🎯 Trying endpoint: {endpoint}")
        result = make_request(endpoint, method='POST', data=payload, cookie=cookie)
        
        print(f"Status: {result['status_code']}")
        if result['success']:
            print("✅ Generation request successful!")
            print(f"Response: {json.dumps(result['data'], indent=2)}")
            return result['data']
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
            if result['data']:
                print(f"Response: {str(result['data'])[:300]}...")
    
    return None

def main():
    """Main function."""
    print("🎵 Working Suno POC")
    print("=" * 50)
    
    # Load cookie
    cookie = load_cookie()
    if not cookie:
        print("❌ No cookie found. Please set SUNO_COOKIE in .env file")
        return False
    
    print(f"✅ Cookie loaded: {len(cookie)} characters")
    
    # Test endpoints
    working_endpoint = test_suno_endpoints(cookie)
    if working_endpoint:
        print(f"\n✅ Found working endpoint: {working_endpoint}")
    else:
        print("\n⚠️ No working endpoints found, but continuing with generation test...")
    
    # Try to generate music
    prompt = "A peaceful acoustic guitar melody with soft vocals about a sunny day"
    result = generate_music_simple(cookie, prompt)
    
    if result:
        print("\n🎉 Music generation test completed!")
        print("Note: This is a proof of concept. The actual generation may require")
        print("additional steps like polling for completion and downloading the audio.")
        return True
    else:
        print("\n❌ Music generation failed")
        print("\nPossible reasons:")
        print("1. Cookie may have expired")
        print("2. API endpoints may have changed")
        print("3. Additional authentication may be required")
        print("4. Rate limiting or CAPTCHA challenges")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
