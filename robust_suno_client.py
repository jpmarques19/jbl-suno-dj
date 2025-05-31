#!/usr/bin/env python3
"""
Robust Suno API client with network error handling and automation.
"""

import urllib.request
import urllib.error
import json
import os
import time
import sys
import subprocess
from typing import Optional, Dict, Any, List

class RobustSunoClient:
    """Robust Suno API client with error handling and retry logic."""
    
    def __init__(self, api_key: str, base_url: str = "https://apibox.erweima.ai"):
        self.api_key = api_key
        self.base_url = base_url
        self.session_headers = {
            'Authorization': f'Bearer {api_key}',
            'User-Agent': 'RobustSunoClient/1.0',
            'Accept': 'application/json'
        }
    
    def _make_request(self, endpoint: str, method: str = 'GET', data: Optional[Dict] = None, 
                     timeout: int = 30, max_retries: int = 3) -> Dict[str, Any]:
        """Make HTTP request with retry logic and error handling."""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(max_retries):
            try:
                headers = self.session_headers.copy()
                request_data = None
                
                if data:
                    request_data = json.dumps(data).encode('utf-8')
                    headers['Content-Type'] = 'application/json'
                
                req = urllib.request.Request(url, data=request_data, headers=headers, method=method)
                
                print(f"🔄 Attempt {attempt + 1}/{max_retries}: {method} {url}")
                
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    response_data = response.read().decode('utf-8')
                    result = json.loads(response_data) if response_data else {}
                    
                    return {
                        'success': True,
                        'status_code': response.getcode(),
                        'data': result
                    }
                    
            except urllib.error.HTTPError as e:
                error_data = e.read().decode('utf-8') if e.fp else str(e)
                print(f"❌ HTTP Error {e.code}: {error_data}")
                
                if e.code in [429, 503, 504]:  # Retry on rate limit or server errors
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 5
                        print(f"⏳ Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                
                return {
                    'success': False,
                    'status_code': e.code,
                    'error': error_data
                }
                
            except (urllib.error.URLError, OSError, ConnectionError) as e:
                print(f"❌ Network Error: {e}")
                
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 10
                    print(f"⏳ Network retry in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                
                return {
                    'success': False,
                    'status_code': 0,
                    'error': f"Network error: {e}"
                }
                
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                return {
                    'success': False,
                    'status_code': 0,
                    'error': f"Unexpected error: {e}"
                }
        
        return {
            'success': False,
            'status_code': 0,
            'error': f"Failed after {max_retries} attempts"
        }
    
    def generate_music(self, prompt: str, model: str = "V3_5", 
                      custom_mode: bool = False, instrumental: bool = False) -> Optional[str]:
        """Generate music and return task ID."""
        print(f"🎵 Generating music: '{prompt}'")
        print(f"💰 Model: {model}")
        
        payload = {
            "prompt": prompt,
            "customMode": custom_mode,
            "instrumental": instrumental,
            "model": model,
            "callBackUrl": "https://httpbin.org/post"
        }
        
        result = self._make_request("/api/v1/generate", "POST", payload)
        
        if result['success'] and result['data'].get('code') == 200:
            task_id = result['data'].get('data', {}).get('taskId')
            print(f"✅ Generation started! Task ID: {task_id}")
            return task_id
        else:
            error_msg = result.get('error', 'Unknown error')
            print(f"❌ Generation failed: {error_msg}")
            return None
    
    def check_status(self, task_id: str) -> Optional[Dict]:
        """Check the status of a music generation task."""
        print(f"🔍 Checking status for: {task_id}")
        
        endpoint = f"/api/v1/generate/record-info?taskId={task_id}"
        result = self._make_request(endpoint, "GET")
        
        if result['success'] and result['data'].get('code') == 200:
            return result['data'].get('data')
        else:
            error_msg = result.get('error', 'Unknown error')
            print(f"❌ Status check failed: {error_msg}")
            return None
    
    def wait_for_completion(self, task_id: str, max_wait_time: int = 300, 
                           check_interval: int = 15) -> Optional[List[Dict]]:
        """Wait for music generation to complete and return track data."""
        print(f"⏳ Waiting for completion (max {max_wait_time}s)...")
        
        start_time = time.time()
        
        while (time.time() - start_time) < max_wait_time:
            elapsed = int(time.time() - start_time)
            print(f"📡 Status check at {elapsed}s...")
            
            status_data = self.check_status(task_id)
            
            if status_data:
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
                completed_tracks = []
                for track in tracks:
                    audio_url = track.get('audio_url')
                    status = track.get('status', 'unknown')
                    
                    print(f"  Track status: {status}")
                    
                    if audio_url:
                        print(f"  ✅ Audio ready!")
                        completed_tracks.append(track)
                
                if completed_tracks:
                    print(f"🎉 {len(completed_tracks)} track(s) completed!")
                    return completed_tracks
            
            if elapsed + check_interval < max_wait_time:
                print(f"⏳ Waiting {check_interval}s before next check...")
                time.sleep(check_interval)
            else:
                break
        
        print(f"⚠️ Timeout after {max_wait_time}s")
        return None
    
    def download_track(self, track: Dict, download_dir: str = "./downloads") -> Optional[str]:
        """Download a track and return the file path."""
        audio_url = track.get('audio_url')
        if not audio_url:
            print("❌ No audio URL in track data")
            return None
        
        # Create download directory
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        
        # Generate filename
        title = track.get('title', 'generated_music')
        track_id = track.get('id', 'unknown')
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = f"{safe_title}_{track_id[:8]}.mp3"
        filepath = os.path.join(download_dir, filename)
        
        print(f"📥 Downloading: {filename}")
        
        try:
            urllib.request.urlretrieve(audio_url, filepath)
            file_size = os.path.getsize(filepath)
            print(f"✅ Downloaded: {filepath} ({file_size} bytes)")
            return filepath
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return None
    
    def play_audio(self, filepath: str) -> bool:
        """Try to play the audio file."""
        print(f"🎵 Playing: {os.path.basename(filepath)}")
        
        # Try different audio players
        players = [
            'mpv', 'vlc', 'mplayer', 'ffplay', 'paplay', 'aplay',
            'open', 'start'  # macOS/Windows
        ]
        
        for player in players:
            try:
                if player in ['open', 'start']:
                    # macOS/Windows - open with default app
                    subprocess.Popen([player, filepath])
                else:
                    # Linux - use audio player
                    subprocess.Popen([player, filepath], 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL)
                
                print(f"✅ Playing with {player}")
                return True
                
            except (FileNotFoundError, subprocess.CalledProcessError):
                continue
        
        print("❌ No audio player found")
        print("💡 Install mpv, vlc, or another audio player")
        print(f"📁 File saved at: {filepath}")
        return False

def main():
    """Main automated workflow."""
    print("🎵 Automated Suno Music Generator")
    print("=" * 50)
    
    # Configuration
    API_KEY = "4e2feeb494648a5f5845dd5b65558544"
    
    # Initialize client
    client = RobustSunoClient(API_KEY)
    
    # Get user input
    prompt = input("Enter music prompt (or press Enter for 'upbeat song'): ").strip()
    if not prompt:
        prompt = "upbeat song"
    
    print(f"\n🎯 Generating: '{prompt}'")
    
    try:
        # Step 1: Generate music
        task_id = client.generate_music(prompt)
        if not task_id:
            print("❌ Failed to start generation")
            return False
        
        # Step 2: Wait for completion
        tracks = client.wait_for_completion(task_id)
        if not tracks:
            print("❌ Generation did not complete in time")
            print(f"🆔 Task ID: {task_id} (check later)")
            return False
        
        # Step 3: Download and play
        for i, track in enumerate(tracks):
            print(f"\n🎵 Processing track {i+1}:")
            
            filepath = client.download_track(track)
            if filepath:
                client.play_audio(filepath)
        
        print("\n🎉 Automated workflow completed successfully!")
        return True
        
    except KeyboardInterrupt:
        print("\n👋 Cancelled by user")
        return False
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()
