#!/usr/bin/env python3
"""Generate music and download it - complete workflow."""

import urllib.request
import json
import os
import time
import sys

# Configuration
API_KEY = "4e2feeb494648a5f5845dd5b65558544"
BASE_URL = "https://apibox.erweima.ai"
DOWNLOAD_DIR = "./downloads"

def make_request(url, method='GET', data=None, headers=None, timeout=30):
    """Make HTTP request with better error handling."""
    if headers is None:
        headers = {}
    
    try:
        if data:
            data = json.dumps(data).encode('utf-8')
            headers['Content-Type'] = 'application/json'
        
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            response_data = response.read().decode('utf-8')
            return {
                'success': True,
                'status_code': response.getcode(),
                'data': json.loads(response_data) if response_data else None
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

def generate_music(prompt="short test song"):
    """Generate music with a short prompt to save credits."""
    print(f"🎵 Generating music: '{prompt}'")
    print(f"💰 Using V3_5 model (cheaper)")
    
    url = f"{BASE_URL}/api/v1/generate"
    
    payload = {
        "prompt": prompt,
        "customMode": False,
        "instrumental": False,
        "model": "V3_5",
        "callBackUrl": "https://httpbin.org/post"
    }
    
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'User-Agent': 'SunoTest/1.0'
    }
    
    result = make_request(url, 'POST', payload, headers)
    
    if result['success'] and result['data'].get('code') == 200:
        task_id = result['data'].get('data', {}).get('taskId')
        print(f"✅ Generation started! Task ID: {task_id}")
        return task_id
    else:
        error_msg = result.get('error', {}).get('msg', 'Unknown error')
        print(f"❌ Generation failed: {error_msg}")
        return None

def check_status_with_retry(task_id, max_retries=3):
    """Check status with retry logic."""
    print(f"🔍 Checking status for: {task_id}")
    
    for attempt in range(max_retries):
        try:
            url = f"{BASE_URL}/api/v1/generate/record-info?taskId={task_id}"
            headers = {'Authorization': f'Bearer {API_KEY}'}
            
            result = make_request(url, 'GET', None, headers, timeout=15)
            
            if result['success']:
                if result['data'].get('code') == 200:
                    return result['data'].get('data')
                else:
                    print(f"API Error: {result['data'].get('msg')}")
            else:
                print(f"Request failed: {result.get('error', {}).get('msg')}")
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
        
        if attempt < max_retries - 1:
            print(f"Retrying in 5 seconds...")
            time.sleep(5)
    
    return None

def download_audio_file(audio_url, filename):
    """Download audio file."""
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
    
    filepath = os.path.join(DOWNLOAD_DIR, filename)
    
    print(f"📥 Downloading: {filename}")
    
    try:
        urllib.request.urlretrieve(audio_url, filepath)
        file_size = os.path.getsize(filepath)
        print(f"✅ Downloaded: {filepath} ({file_size} bytes)")
        return filepath
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return None

def play_audio_file(filepath):
    """Try to play the audio file."""
    print(f"🎵 Trying to play: {os.path.basename(filepath)}")
    
    # Try different players
    players = ['mpv', 'vlc', 'mplayer', 'ffplay', 'paplay']
    
    for player in players:
        try:
            import subprocess
            print(f"Trying {player}...")
            result = subprocess.run([player, filepath], 
                                  capture_output=True, 
                                  timeout=3,
                                  text=True)
            if result.returncode == 0:
                print(f"✅ Playing with {player}")
                # Start playing in background
                subprocess.Popen([player, filepath], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError) as e:
            print(f"{player} failed: {e}")
            continue
    
    print("❌ No audio player found")
    print(f"📁 File saved at: {filepath}")
    print("💡 Install mpv, vlc, or another audio player to hear the music")
    return False

def main():
    """Main workflow: generate, wait, download, play."""
    print("🎵 Complete Suno Workflow: Generate → Download → Play")
    print("=" * 60)
    
    # Get user input
    prompt = input("Enter your music prompt (or press Enter for 'happy tune'): ").strip()
    if not prompt:
        prompt = "happy tune"
    
    print(f"Using prompt: '{prompt}'")
    
    # Step 1: Generate music
    task_id = generate_music(prompt)
    if not task_id:
        return False
    
    # Step 2: Wait and check status
    print(f"\n⏳ Waiting for generation to complete...")
    max_wait_time = 180  # 3 minutes
    check_interval = 15  # Check every 15 seconds
    
    start_time = time.time()
    while (time.time() - start_time) < max_wait_time:
        print(f"\n📡 Checking status... ({int(time.time() - start_time)}s elapsed)")
        
        status_data = check_status_with_retry(task_id)
        
        if status_data:
            print("📄 Got status data!")
            
            # Handle different response formats
            tracks = []
            if isinstance(status_data, list):
                tracks = status_data
            elif isinstance(status_data, dict):
                if 'audio_url' in status_data:
                    tracks = [status_data]
                else:
                    tracks = [status_data]
            
            # Check for completed tracks
            for i, track in enumerate(tracks):
                audio_url = track.get('audio_url')
                status = track.get('status', 'unknown')
                
                print(f"Track {i+1}: Status = {status}")
                
                if audio_url:
                    print(f"🎉 Audio ready! URL: {audio_url[:50]}...")
                    
                    # Download and play
                    title = track.get('title', 'generated_music')
                    filename = f"{title.replace(' ', '_')}_{task_id[:8]}.mp3"
                    
                    filepath = download_audio_file(audio_url, filename)
                    if filepath:
                        play_audio_file(filepath)
                        return True
        
        print(f"⏳ Still generating... waiting {check_interval} seconds")
        time.sleep(check_interval)
    
    print(f"⚠️ Timeout after {max_wait_time} seconds")
    print(f"🆔 Task ID: {task_id}")
    print("💡 Music might still be generating. Check later or visit the dashboard.")
    return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 Success! Music generated, downloaded, and played!")
        else:
            print("\n❌ Workflow incomplete. Check the messages above.")
    except KeyboardInterrupt:
        print("\n👋 Cancelled by user")
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()
