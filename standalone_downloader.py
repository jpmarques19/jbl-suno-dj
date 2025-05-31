#!/usr/bin/env python3
"""
Standalone music downloader for Suno API.
This script can be run in any Python environment with internet access.
"""

import urllib.request
import json
import os
import sys

def download_suno_music(api_key, task_id, download_dir="./downloads"):
    """
    Download music from Suno API using task ID.
    
    Args:
        api_key: Your Suno API key
        task_id: Task ID from music generation
        download_dir: Directory to save the music
    """
    print(f"🎵 Suno Music Downloader")
    print(f"🆔 Task ID: {task_id}")
    print(f"📁 Download directory: {download_dir}")
    print("=" * 50)
    
    # Create download directory
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
        print(f"📁 Created directory: {download_dir}")
    
    # Check status endpoint
    status_url = f"https://apibox.erweima.ai/api/v1/generate/record-info?taskId={task_id}"
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'User-Agent': 'SunoDownloader/1.0'
    }
    
    print(f"📡 Checking status...")
    
    try:
        req = urllib.request.Request(status_url, headers=headers, method='GET')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            print(f"✅ Status response received (HTTP {response.getcode()})")
            print(f"📄 Response data:")
            print(json.dumps(result, indent=2))
            
            if result.get('code') != 200:
                print(f"❌ API Error: {result.get('msg', 'Unknown error')}")
                return False
            
            # Extract track data
            data = result.get('data')
            if not data:
                print("❌ No data in response")
                return False
            
            # Handle different response formats
            tracks = []
            if isinstance(data, list):
                tracks = data
            elif isinstance(data, dict):
                if 'audio_url' in data:
                    tracks = [data]
                else:
                    tracks = [data]
            
            if not tracks:
                print("❌ No tracks found")
                return False
            
            print(f"🎵 Found {len(tracks)} track(s)")
            
            # Download each track
            downloaded_files = []
            for i, track in enumerate(tracks):
                print(f"\n🎵 Processing track {i+1}:")
                
                # Track info
                title = track.get('title', f'track_{i+1}')
                status = track.get('status', 'unknown')
                audio_url = track.get('audio_url')
                
                print(f"  Title: {title}")
                print(f"  Status: {status}")
                
                if not audio_url:
                    print(f"  ⏳ Audio not ready yet")
                    continue
                
                print(f"  🔗 Audio URL: {audio_url[:50]}...")
                
                # Generate filename
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"{safe_title}_{task_id[:8]}.mp3"
                filepath = os.path.join(download_dir, filename)
                
                # Download the file
                print(f"  📥 Downloading to: {filename}")
                
                try:
                    urllib.request.urlretrieve(audio_url, filepath)
                    file_size = os.path.getsize(filepath)
                    print(f"  ✅ Downloaded: {file_size} bytes")
                    downloaded_files.append(filepath)
                    
                except Exception as e:
                    print(f"  ❌ Download failed: {e}")
            
            if downloaded_files:
                print(f"\n🎉 Successfully downloaded {len(downloaded_files)} file(s):")
                for file in downloaded_files:
                    print(f"  📁 {os.path.abspath(file)}")
                
                # Try to play the first file
                if len(downloaded_files) > 0:
                    first_file = downloaded_files[0]
                    print(f"\n🎵 Attempting to play: {os.path.basename(first_file)}")
                    
                    # Try different audio players
                    players = ['mpv', 'vlc', 'mplayer', 'ffplay', 'paplay', 'open', 'start']
                    
                    for player in players:
                        try:
                            import subprocess
                            if player in ['open', 'start']:  # macOS/Windows
                                subprocess.Popen([player, first_file])
                            else:  # Linux
                                subprocess.Popen([player, first_file], 
                                               stdout=subprocess.DEVNULL, 
                                               stderr=subprocess.DEVNULL)
                            print(f"✅ Playing with {player}")
                            break
                        except (FileNotFoundError, subprocess.CalledProcessError):
                            continue
                    else:
                        print("❌ No audio player found")
                        print("💡 Install mpv, vlc, or another audio player")
                        print(f"📁 You can manually play: {first_file}")
                
                return True
            else:
                print("❌ No files were downloaded")
                return False
                
    except urllib.error.HTTPError as e:
        error_data = e.read().decode('utf-8') if e.fp else str(e)
        print(f"❌ HTTP Error {e.code}: {error_data}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function."""
    # Configuration
    API_KEY = "4e2feeb494648a5f5845dd5b65558544"
    
    # Your generated music task ID
    TASK_ID = "9f2107e5fd428822811ea5dc996bafa9"
    
    print("🎵 Standalone Suno Music Downloader")
    print("=" * 50)
    print("This script will download your generated music.")
    print(f"Task ID: {TASK_ID}")
    print()
    
    # Allow user to specify different task ID
    user_task_id = input(f"Enter task ID (or press Enter to use {TASK_ID[:8]}...): ").strip()
    if user_task_id:
        TASK_ID = user_task_id
    
    # Download the music
    success = download_suno_music(API_KEY, TASK_ID)
    
    if success:
        print("\n🎉 Download completed successfully!")
    else:
        print("\n❌ Download failed")
        print("💡 Possible reasons:")
        print("  - Music is still generating (try again in a few minutes)")
        print("  - Network connectivity issues")
        print("  - Invalid task ID")
        print("  - API service temporarily unavailable")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Download cancelled by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()

# Instructions for use:
"""
USAGE INSTRUCTIONS:

1. Save this file as 'standalone_downloader.py'
2. Run it with: python3 standalone_downloader.py
3. The script will:
   - Check the status of your generated music
   - Download the MP3 file(s) if ready
   - Try to play the music automatically
   - Save files in ./downloads/ directory

If the music isn't ready yet, wait a few minutes and try again.
Music generation typically takes 1-3 minutes.

Your task ID: 9f2107e5fd428822811ea5dc996bafa9
"""
