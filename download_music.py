#!/usr/bin/env python3
"""Download generated music from Suno API."""

import urllib.request
import json
import os
import time

# Configuration
API_KEY = "4e2feeb494648a5f5845dd5b65558544"
BASE_URL = "https://apibox.erweima.ai"
DOWNLOAD_DIR = "./downloads"

def check_status(task_id):
    """Check the status of a music generation task."""
    print(f"🔍 Checking status for task: {task_id}")
    
    url = f"{BASE_URL}/api/v1/generate/record-info?taskId={task_id}"
    
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'User-Agent': 'SunoDownloader/1.0'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers, method='GET')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            print(f"📄 Raw response:")
            print(json.dumps(result, indent=2))
            
            if result.get('code') == 200:
                return result.get('data')
            else:
                print(f"❌ Status check error: {result.get('msg')}")
                return None
                
    except urllib.error.HTTPError as e:
        error_data = e.read().decode('utf-8') if e.fp else str(e)
        print(f"❌ HTTP Error {e.code}: {error_data}")
        return None
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        return None

def download_audio(audio_url, filename):
    """Download audio file from URL."""
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
    
    filepath = os.path.join(DOWNLOAD_DIR, filename)
    
    print(f"📥 Downloading: {filename}")
    print(f"🔗 URL: {audio_url}")
    
    try:
        urllib.request.urlretrieve(audio_url, filepath)
        print(f"✅ Downloaded to: {filepath}")
        return filepath
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return None

def play_audio(filepath):
    """Try to play the audio file."""
    print(f"🎵 Attempting to play: {filepath}")
    
    # Try different audio players
    players = [
        "mpv",
        "vlc",
        "mplayer", 
        "paplay",
        "aplay",
        "ffplay"
    ]
    
    for player in players:
        try:
            import subprocess
            result = subprocess.run([player, filepath], 
                                  capture_output=True, 
                                  timeout=5)
            if result.returncode == 0:
                print(f"✅ Playing with {player}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            continue
    
    print("❌ No audio player found. Please install mpv, vlc, or another audio player")
    print(f"📁 Audio file saved at: {filepath}")
    return False

def main():
    """Main function to check status and download music."""
    print("🎵 Suno Music Downloader")
    print("=" * 40)
    
    # Use the task ID from our successful generation
    task_id = "9f2107e5fd428822811ea5dc996bafa9"
    
    print(f"🆔 Task ID: {task_id}")
    
    # Check status
    status_data = check_status(task_id)
    
    if not status_data:
        print("❌ Could not get status data")
        print("💡 The music might still be generating, or there might be a network issue")
        print("🌐 Try checking your dashboard at: https://sunoapi.org/dashboard")
        return False
    
    print(f"📊 Status data received!")
    
    # Handle different response formats
    tracks = []
    if isinstance(status_data, list):
        tracks = status_data
    elif isinstance(status_data, dict):
        if 'tracks' in status_data:
            tracks = status_data['tracks']
        elif 'audio_url' in status_data:
            tracks = [status_data]
        else:
            # Check if the dict itself is a track
            tracks = [status_data]
    
    if not tracks:
        print("❌ No tracks found in response")
        return False
    
    print(f"🎵 Found {len(tracks)} track(s)")
    
    # Process each track
    downloaded_files = []
    for i, track in enumerate(tracks):
        print(f"\n🎵 Track {i+1}:")
        print(f"  Status: {track.get('status', 'Unknown')}")
        print(f"  Title: {track.get('title', 'Untitled')}")
        
        audio_url = track.get('audio_url')
        if audio_url:
            print(f"  ✅ Audio URL available: {audio_url[:50]}...")
            
            # Generate filename
            title = track.get('title', f'track_{i+1}').replace(' ', '_')
            track_id = track.get('id', f'unknown_{i+1}')
            filename = f"{title}_{track_id}.mp3"
            
            # Download the file
            filepath = download_audio(audio_url, filename)
            if filepath:
                downloaded_files.append(filepath)
        else:
            print(f"  ⏳ Audio not ready yet")
    
    # Play the first downloaded file
    if downloaded_files:
        print(f"\n🎉 Downloaded {len(downloaded_files)} file(s)!")
        first_file = downloaded_files[0]
        
        print(f"\n🎵 Playing first track: {os.path.basename(first_file)}")
        play_audio(first_file)
        
        print(f"\n📁 All files saved in: {DOWNLOAD_DIR}")
        for file in downloaded_files:
            print(f"  - {os.path.basename(file)}")
        
        return True
    else:
        print("❌ No audio files were ready for download")
        print("⏳ The music might still be generating")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n💡 Tips:")
            print("1. Wait a few minutes and try again")
            print("2. Check https://sunoapi.org/dashboard")
            print("3. Music generation can take 1-3 minutes")
    except KeyboardInterrupt:
        print("\n👋 Download cancelled")
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()
