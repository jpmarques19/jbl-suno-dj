#!/usr/bin/env python3
"""Network diagnostics and connectivity fixes for Suno API."""

import urllib.request
import urllib.error
import socket
import ssl
import json
import time
import subprocess
import sys

def test_basic_connectivity():
    """Test basic network connectivity."""
    print("🔍 Testing basic network connectivity...")
    
    tests = [
        ("DNS Resolution", lambda: socket.gethostbyname('google.com')),
        ("HTTP Request", lambda: urllib.request.urlopen('http://httpbin.org/get', timeout=10).getcode()),
        ("HTTPS Request", lambda: urllib.request.urlopen('https://httpbin.org/get', timeout=10).getcode()),
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            print(f"✅ {test_name}: {result}")
        except Exception as e:
            print(f"❌ {test_name}: {e}")
            return False
    
    return True

def test_suno_api_connectivity():
    """Test connectivity to Suno API specifically."""
    print("\n🔍 Testing Suno API connectivity...")
    
    api_host = "apibox.erweima.ai"
    
    # Test DNS resolution
    try:
        ip = socket.gethostbyname(api_host)
        print(f"✅ DNS Resolution: {api_host} -> {ip}")
    except Exception as e:
        print(f"❌ DNS Resolution failed: {e}")
        return False
    
    # Test HTTPS connection
    try:
        response = urllib.request.urlopen(f"https://{api_host}", timeout=15)
        print(f"✅ HTTPS Connection: {response.getcode()}")
    except urllib.error.HTTPError as e:
        if e.code in [404, 403]:  # Expected for API endpoints
            print(f"✅ HTTPS Connection: {e.code} (expected)")
        else:
            print(f"❌ HTTPS Connection: {e.code}")
            return False
    except Exception as e:
        print(f"❌ HTTPS Connection failed: {e}")
        return False
    
    return True

def test_suno_api_auth():
    """Test Suno API authentication."""
    print("\n🔍 Testing Suno API authentication...")
    
    api_key = "4e2feeb494648a5f5845dd5b65558544"
    url = "https://apibox.erweima.ai/api/v1/generate"
    
    # Test with minimal payload
    payload = {
        "prompt": "test",
        "customMode": False,
        "instrumental": False,
        "model": "V3_5",
        "callBackUrl": "https://httpbin.org/post"
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
        'User-Agent': 'NetworkDiagnostics/1.0'
    }
    
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if result.get('code') == 200:
                print(f"✅ API Authentication: Success")
                task_id = result.get('data', {}).get('taskId')
                print(f"✅ Generated Task ID: {task_id}")
                return task_id
            else:
                print(f"❌ API Authentication: {result.get('msg', 'Unknown error')}")
                return None
                
    except Exception as e:
        print(f"❌ API Authentication failed: {e}")
        return None

def fix_network_issues():
    """Attempt to fix common network issues."""
    print("\n🔧 Attempting to fix network issues...")
    
    fixes = [
        ("Flush DNS cache", ["sudo", "systemctl", "flush-dns"]),
        ("Reset network", ["sudo", "systemctl", "restart", "networking"]),
        ("Update CA certificates", ["sudo", "update-ca-certificates"]),
    ]
    
    for fix_name, command in fixes:
        try:
            print(f"🔄 {fix_name}...")
            result = subprocess.run(command, capture_output=True, timeout=30)
            if result.returncode == 0:
                print(f"✅ {fix_name}: Success")
            else:
                print(f"⚠️ {fix_name}: {result.stderr.decode()}")
        except Exception as e:
            print(f"❌ {fix_name}: {e}")

def create_fallback_solution():
    """Create a fallback solution for network issues."""
    print("\n🛠️ Creating fallback solution...")
    
    fallback_script = '''#!/bin/bash
# Fallback script for Suno API when Python has network issues

API_KEY="4e2feeb494648a5f5845dd5b65558544"
BASE_URL="https://apibox.erweima.ai"

echo "🎵 Fallback Suno API Client"
echo "=========================="

# Function to generate music
generate_music() {
    local prompt="$1"
    echo "🎵 Generating music: '$prompt'"
    
    curl -X POST "$BASE_URL/api/v1/generate" \\
        -H "Content-Type: application/json" \\
        -H "Authorization: Bearer $API_KEY" \\
        -d "{
            \\"prompt\\": \\"$prompt\\",
            \\"customMode\\": false,
            \\"instrumental\\": false,
            \\"model\\": \\"V3_5\\",
            \\"callBackUrl\\": \\"https://httpbin.org/post\\"
        }" \\
        --timeout 30
}

# Function to check status
check_status() {
    local task_id="$1"
    echo "🔍 Checking status: $task_id"
    
    curl -X GET "$BASE_URL/api/v1/generate/record-info?taskId=$task_id" \\
        -H "Authorization: Bearer $API_KEY" \\
        --timeout 30
}

# Main workflow
if [ "$#" -eq 0 ]; then
    echo "Usage: $0 <prompt> [task_id_to_check]"
    echo "Example: $0 'happy song'"
    echo "Example: $0 '' existing_task_id_here"
    exit 1
fi

if [ -n "$1" ]; then
    echo "Generating music..."
    generate_music "$1"
fi

if [ -n "$2" ]; then
    echo "Checking status..."
    check_status "$2"
fi
'''
    
    with open("fallback_suno.sh", "w") as f:
        f.write(fallback_script)
    
    # Make executable
    try:
        subprocess.run(["chmod", "+x", "fallback_suno.sh"])
        print("✅ Created fallback_suno.sh")
        print("💡 Usage: ./fallback_suno.sh 'your prompt here'")
    except Exception as e:
        print(f"❌ Failed to create fallback: {e}")

def main():
    """Main diagnostic function."""
    print("🔍 Suno API Network Diagnostics")
    print("=" * 50)
    
    # Test basic connectivity
    if not test_basic_connectivity():
        print("\n❌ Basic connectivity failed")
        fix_network_issues()
        return False
    
    # Test Suno API connectivity
    if not test_suno_api_connectivity():
        print("\n❌ Suno API connectivity failed")
        create_fallback_solution()
        return False
    
    # Test API authentication and generation
    task_id = test_suno_api_auth()
    if task_id:
        print(f"\n🎉 All tests passed! Generated task ID: {task_id}")
        
        # Test status check
        print("\n🔍 Testing status check...")
        time.sleep(5)  # Wait a bit
        
        try:
            url = f"https://apibox.erweima.ai/api/v1/generate/record-info?taskId={task_id}"
            headers = {'Authorization': 'Bearer 4e2feeb494648a5f5845dd5b65558544'}
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                print(f"✅ Status check works: {result.get('code')}")
                
        except Exception as e:
            print(f"❌ Status check failed: {e}")
        
        return True
    else:
        print("\n❌ API authentication failed")
        create_fallback_solution()
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 Network diagnostics completed successfully!")
            print("💡 You can now use robust_suno_client.py")
        else:
            print("\n❌ Network issues detected")
            print("💡 Try using the fallback script: ./fallback_suno.sh")
    except KeyboardInterrupt:
        print("\n👋 Diagnostics cancelled")
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()
