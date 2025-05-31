#!/usr/bin/env python3
"""Suno POC using SunoAPI.org service."""

import urllib.request
import urllib.parse
import json
import os
import time
import sys

# SunoAPI.org Configuration
BASE_URL = "https://apibox.erweima.ai"
GENERATE_ENDPOINT = "/api/v1/generate"
DETAILS_ENDPOINT = "/api/v1/details"

def load_api_key():
    """Load API key from .env file."""
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            content = f.read()
            for line in content.split('\n'):
                if line.startswith('SUNO_API_KEY='):
                    return line.split('=', 1)[1].strip()
    return None

def make_api_request(endpoint, data=None, api_key=None):
    """Make HTTP request to SunoAPI.org."""
    url = f"{BASE_URL}{endpoint}"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
        'User-Agent': 'SunoPOC/1.0'
    }
    
    if data:
        data = json.dumps(data).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers, method='POST' if data else 'GET')
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            response_data = response.read().decode('utf-8')
            result = json.loads(response_data)
            return {
                'success': True,
                'status_code': response.getcode(),
                'data': result
            }
    except urllib.error.HTTPError as e:
        error_data = e.read().decode('utf-8') if e.fp else str(e)
        try:
            error_json = json.loads(error_data)
        except:
            error_json = {'msg': error_data}
        
        return {
            'success': False,
            'status_code': e.code,
            'error': error_json
        }
    except Exception as e:
        return {
            'success': False,
            'status_code': 0,
            'error': {'msg': str(e)}
        }

def generate_music(api_key, prompt, custom_mode=False, instrumental=False, style=None, title=None, model="V3_5"):
    """Generate music using SunoAPI.org."""
    print(f"🎵 Generating music...")
    print(f"Prompt: '{prompt}'")
    print(f"Mode: {'Custom' if custom_mode else 'Simple'}")
    print(f"Model: {model}")

    # Prepare payload according to API documentation
    payload = {
        "prompt": prompt,
        "customMode": custom_mode,
        "instrumental": instrumental,
        "model": model,
        "callBackUrl": "https://httpbin.org/post"  # Using httpbin as a dummy callback for testing
    }
    
    # Add optional parameters for custom mode
    if custom_mode:
        if style:
            payload["style"] = style
        if title:
            payload["title"] = title
    
    print(f"📡 Sending request to SunoAPI.org...")
    result = make_api_request(GENERATE_ENDPOINT, payload, api_key)
    
    if result['success']:
        data = result['data']
        if data.get('code') == 200:
            print("✅ Music generation request successful!")
            task_id = data.get('data', {}).get('task_id')
            print(f"Task ID: {task_id}")
            return task_id
        else:
            print(f"❌ API Error: {data.get('msg', 'Unknown error')}")
            return None
    else:
        print(f"❌ Request failed: {result['error'].get('msg', 'Unknown error')}")
        print(f"Status code: {result['status_code']}")
        return None

def check_task_status(api_key, task_id):
    """Check the status of a music generation task."""
    print(f"🔍 Checking task status: {task_id}")
    
    # Note: The details endpoint might need the task_id as a parameter
    # Adjusting based on typical API patterns
    endpoint = f"{DETAILS_ENDPOINT}?task_id={task_id}"
    
    result = make_api_request(endpoint, None, api_key)
    
    if result['success']:
        data = result['data']
        if data.get('code') == 200:
            return data.get('data')
        else:
            print(f"❌ Status check error: {data.get('msg', 'Unknown error')}")
            return None
    else:
        print(f"❌ Status check failed: {result['error'].get('msg', 'Unknown error')}")
        return None

def wait_for_completion(api_key, task_id, max_wait_time=300):
    """Wait for music generation to complete."""
    print(f"⏳ Waiting for music generation to complete...")
    print(f"Max wait time: {max_wait_time} seconds")
    
    start_time = time.time()
    check_interval = 10  # Check every 10 seconds
    
    while (time.time() - start_time) < max_wait_time:
        status_data = check_task_status(api_key, task_id)
        
        if status_data:
            # Check if we have completed tracks
            tracks = status_data.get('data', [])
            if tracks and len(tracks) > 0:
                # Check if tracks have audio URLs
                completed_tracks = [track for track in tracks if track.get('audio_url')]
                if completed_tracks:
                    print(f"✅ Generation completed! {len(completed_tracks)} track(s) ready.")
                    return completed_tracks
        
        elapsed = int(time.time() - start_time)
        print(f"⏳ Still generating... ({elapsed}s elapsed)")
        time.sleep(check_interval)
    
    print(f"⚠️ Timeout reached after {max_wait_time} seconds")
    return None

def download_track(track, download_dir="./downloads"):
    """Download a generated music track."""
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    audio_url = track.get('audio_url')
    track_id = track.get('id', 'unknown')
    title = track.get('title', 'untitled').replace(' ', '_')
    
    if not audio_url:
        print(f"❌ No audio URL for track {track_id}")
        return None
    
    filename = f"{title}_{track_id}.mp3"
    filepath = os.path.join(download_dir, filename)
    
    print(f"📥 Downloading: {filename}")
    
    try:
        urllib.request.urlretrieve(audio_url, filepath)
        print(f"✅ Downloaded: {filepath}")
        return filepath
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return None

def main():
    """Main function."""
    print("🎵 SunoAPI.org POC")
    print("=" * 50)
    
    # Load API key
    api_key = load_api_key()
    if not api_key or api_key == "your_api_key_here":
        print("❌ No API key found!")
        print("Please:")
        print("1. Visit https://sunoapi.org/api-key to get your API key")
        print("2. Update the SUNO_API_KEY in your .env file")
        return False
    
    print(f"✅ API key loaded: {api_key[:10]}...")
    
    # Get user input
    prompt = input("\n🎤 Enter your music prompt: ").strip()
    if not prompt:
        prompt = "A peaceful acoustic guitar melody with soft vocals about a sunny day"
        print(f"Using default prompt: {prompt}")
    
    # Generate music
    task_id = generate_music(api_key, prompt)
    if not task_id:
        return False
    
    # Wait for completion
    tracks = wait_for_completion(api_key, task_id)
    if not tracks:
        print("❌ Generation did not complete in time")
        return False
    
    # Display results and download
    print(f"\n🎉 Generated {len(tracks)} track(s):")
    for i, track in enumerate(tracks, 1):
        print(f"\nTrack {i}:")
        print(f"  ID: {track.get('id')}")
        print(f"  Title: {track.get('title', 'Untitled')}")
        print(f"  Duration: {track.get('duration', 'Unknown')}s")
        print(f"  Audio URL: {track.get('audio_url', 'N/A')}")
        
        # Download the track
        download_track(track)
    
    print("\n🎉 POC completed successfully!")
    return True

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
