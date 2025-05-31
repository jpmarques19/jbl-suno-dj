#!/usr/bin/env python3
"""Simple Suno API test using direct HTTP requests."""

import os
import json
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Suno API endpoints (trying different options)
BASE_URL_1 = "https://studio-api.suno.ai"
BASE_URL_2 = "https://api.bltcy.ai"  # Hosted service
BASE_URL_3 = "https://suno.gcui.ai"  # Demo service

# Try multiple endpoints
ENDPOINTS_TO_TRY = [
    {
        "name": "Official Studio API",
        "base": BASE_URL_1,
        "generate": f"{BASE_URL_1}/api/generate/v2/",
        "feed": f"{BASE_URL_1}/api/feed/"
    },
    {
        "name": "Hosted Service",
        "base": BASE_URL_2,
        "generate": f"{BASE_URL_2}/api/generate",
        "feed": f"{BASE_URL_2}/api/get_limit"
    },
    {
        "name": "Demo Service",
        "base": BASE_URL_3,
        "generate": f"{BASE_URL_3}/api/generate",
        "feed": f"{BASE_URL_3}/api/get_limit"
    }
]

def get_headers(cookie):
    """Get headers for Suno API requests."""
    return {
        "Cookie": cookie,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://app.suno.ai/",
        "Origin": "https://app.suno.ai"
    }

def test_connection(cookie):
    """Test connection to Suno API endpoints."""
    print("🔗 Testing connection to Suno API endpoints...")

    headers = get_headers(cookie)

    for endpoint in ENDPOINTS_TO_TRY:
        print(f"\n🔍 Testing {endpoint['name']}...")
        try:
            # Try to get the feed/limit endpoint
            response = requests.get(endpoint['feed'], headers=headers, timeout=10)
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                print(f"✅ {endpoint['name']} connection successful!")
                try:
                    data = response.json()
                    print(f"Response data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    print(f"Sample response: {str(data)[:200]}...")
                    return endpoint  # Return the working endpoint
                except:
                    print("Response is not JSON")
            else:
                print(f"❌ {endpoint['name']} failed: {response.status_code}")
                print(f"Response: {response.text[:200]}...")

        except Exception as e:
            print(f"❌ {endpoint['name']} error: {e}")

    return None

def generate_music(cookie, prompt, endpoint, is_custom=False):
    """Generate music using Suno API."""
    print(f"🎵 Generating music with prompt: '{prompt}'")
    print(f"Using endpoint: {endpoint['name']}")

    headers = get_headers(cookie)

    # Prepare the payload
    payload = {
        "prompt": prompt,
        "make_instrumental": False,
        "wait_audio": False
    }

    if is_custom:
        payload["tags"] = "custom"
        payload["title"] = "Generated Song"

    try:
        response = requests.post(endpoint['generate'], headers=headers, json=payload, timeout=30)
        print(f"Generate Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Generation request successful!")
            print(f"Response: {json.dumps(data, indent=2)}")
            return data
        else:
            print(f"❌ Generation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Generation error: {e}")
        return None

def main():
    """Main test function."""
    print("🧪 Simple Suno API Test")
    print("=" * 50)
    
    # Get cookie from environment
    cookie = os.getenv("SUNO_COOKIE")
    if not cookie:
        print("❌ SUNO_COOKIE not found in environment variables")
        print("Please set your cookie in the .env file")
        return False
    
    print(f"Cookie loaded: {len(cookie)} characters")
    
    # Test connection
    working_endpoint = test_connection(cookie)
    if not working_endpoint:
        print("❌ No working endpoints found")
        return False

    # Test music generation
    prompt = "A peaceful acoustic guitar melody with soft vocals about a sunny day"
    result = generate_music(cookie, prompt, working_endpoint)

    if result:
        print("🎉 Test completed successfully!")
        return True
    else:
        print("❌ Music generation failed")
        return False

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
