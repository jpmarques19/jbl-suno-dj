#!/usr/bin/env python3
"""
Suno Stream Player - Generate and stream music directly with controls
"""

import requests
import json
import time
import subprocess
import sys
import os
from typing import List, Dict, Optional

# Configuration
API_KEY = "4e2feeb494648a5f5845dd5b65558544"
BASE_URL = "https://apibox.erweima.ai"

class SunoStreamPlayer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json',
            'User-Agent': 'SunoStreamPlayer/1.0'
        })
    
    def log(self, message: str, color: str = "blue"):
        colors = {
            "blue": "\033[0;34m",
            "green": "\033[0;32m", 
            "yellow": "\033[1;33m",
            "red": "\033[0;31m",
            "cyan": "\033[0;36m",
            "reset": "\033[0m"
        }
        print(f"{colors.get(color, '')}{message}{colors['reset']}")
    
    def generate_music(self, prompt: str) -> Optional[str]:
        """Generate music and return task ID."""
        self.log(f"🎵 Generating music: '{prompt}'")
        
        payload = {
            "prompt": prompt,
            "customMode": False,
            "instrumental": False,
            "model": "V3_5",
            "callBackUrl": "https://httpbin.org/post"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/api/v1/generate", json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if result.get('code') == 200:
                task_id = result.get('data', {}).get('taskId')
                self.log(f"✅ Generated! Task ID: {task_id}", "green")
                return task_id
            else:
                self.log(f"❌ API Error: {result.get('msg', 'Unknown error')}", "red")
                return None
                
        except Exception as e:
            self.log(f"❌ Generation failed: {e}", "red")
            return None
    
    def wait_for_music(self, task_id: str) -> List[Dict]:
        """Wait for music generation and return track data."""
        self.log("⏳ Waiting for music generation...")
        
        max_attempts = 24  # 6 minutes total
        for attempt in range(1, max_attempts + 1):
            time.sleep(15)
            self.log(f"ℹ️  Status check #{attempt} ({attempt * 15}s elapsed)", "cyan")
            
            try:
                response = self.session.get(
                    f"{BASE_URL}/api/v1/generate/record-info?taskId={task_id}",
                    timeout=30
                )
                response.raise_for_status()
                
                result = response.json()
                if result.get('code') == 200:
                    data = result.get('data', {})
                    suno_data = data.get('response', {}).get('sunoData', [])
                    
                    # Check if we have tracks with stream URLs
                    ready_tracks = []
                    for track in suno_data:
                        stream_url = track.get('streamAudioUrl')
                        if stream_url and stream_url != "null":
                            ready_tracks.append({
                                'title': track.get('title', 'Untitled'),
                                'stream_url': stream_url,
                                'id': track.get('id'),
                                'tags': track.get('tags', ''),
                                'duration': track.get('duration')
                            })
                    
                    if ready_tracks:
                        self.log(f"✅ Music ready! Found {len(ready_tracks)} track(s)", "green")
                        return ready_tracks
                
            except Exception as e:
                self.log(f"⚠️  Status check failed: {e}", "yellow")
            
            if attempt == max_attempts:
                self.log("⚠️  Timeout reached after 6 minutes", "yellow")
                break
        
        return []
    
    def find_audio_player(self) -> Optional[str]:
        """Find available audio player."""
        players = ['mpv', 'vlc', 'mplayer', 'ffplay']
        
        for player in players:
            try:
                subprocess.run([player, '--version'], 
                             capture_output=True, timeout=5)
                return player
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
                continue
        
        return None
    
    def play_stream(self, track: Dict) -> bool:
        """Play a stream with the best available player."""
        title = track['title']
        stream_url = track['stream_url']
        
        self.log(f"▶️  Now playing: {title}", "green")
        self.log(f"ℹ️  Stream URL: {stream_url[:50]}...", "cyan")
        
        player = self.find_audio_player()
        if not player:
            self.log("❌ No compatible audio player found!", "red")
            self.log("ℹ️  Please install one of: mpv, vlc, mplayer, or ffplay", "cyan")
            self.log(f"🔗 Stream URL: {stream_url}", "cyan")
            return False
        
        self.log(f"🎮 Using {player} player", "green")
        print()
        self.log("🎮 PLAYBACK CONTROLS:", "cyan")
        
        try:
            if player == 'mpv':
                self.log("  SPACE - Play/Pause", "cyan")
                self.log("  ← → - Seek backward/forward", "cyan") 
                self.log("  ↑ ↓ - Volume up/down", "cyan")
                self.log("  q - Quit", "cyan")
                self.log("  m - Mute/Unmute", "cyan")
                print()
                
                subprocess.run([
                    'mpv', stream_url,
                    f'--title=Suno: {title}',
                    '--no-video',
                    '--volume=70',
                    '--osd-level=2',
                    '--osd-duration=2000'
                ])
                
            elif player == 'vlc':
                self.log("  SPACE - Play/Pause", "cyan")
                self.log("  Ctrl+← → - Seek", "cyan")
                self.log("  Ctrl+↑ ↓ - Volume", "cyan")
                self.log("  q - Quit", "cyan")
                print()
                
                subprocess.run([
                    'vlc', stream_url,
                    '--intf', 'ncurses',
                    '--no-video',
                    '--volume', '70'
                ])
                
            elif player == 'mplayer':
                self.log("  SPACE - Play/Pause", "cyan")
                self.log("  ← → - Seek", "cyan")
                self.log("  ↑ ↓ - Volume", "cyan")
                self.log("  q - Quit", "cyan")
                print()
                
                subprocess.run([
                    'mplayer', stream_url,
                    '-volume', '70'
                ])
                
            elif player == 'ffplay':
                self.log("  SPACE - Play/Pause", "cyan")
                self.log("  ← → - Seek", "cyan")
                self.log("  ↑ ↓ - Volume", "cyan")
                self.log("  q - Quit", "cyan")
                print()
                
                subprocess.run([
                    'ffplay', stream_url,
                    '-nodisp',
                    '-volume', '70'
                ])
            
            return True
            
        except KeyboardInterrupt:
            self.log("\n⏸️  Playback interrupted", "yellow")
            return True
        except Exception as e:
            self.log(f"❌ Playback failed: {e}", "red")
            return False
    
    def select_and_play_tracks(self, tracks: List[Dict]):
        """Handle track selection and playback."""
        if len(tracks) == 1:
            # Only one track, play it directly
            self.play_stream(tracks[0])
        else:
            # Multiple tracks, show selection menu
            print()
            self.log("🎵 Multiple tracks available:", "green")
            for i, track in enumerate(tracks, 1):
                duration = f" ({track['duration']}s)" if track['duration'] else ""
                tags = f" [{track['tags']}]" if track['tags'] else ""
                print(f"  {i}. {track['title']}{duration}{tags}")
            print("  a. Play all tracks sequentially")
            print()
            
            while True:
                try:
                    choice = input(f"Select track to play (1-{len(tracks)}, a for all): ").strip()
                    
                    if choice.lower() == 'a':
                        # Play all tracks sequentially
                        for i, track in enumerate(tracks, 1):
                            print()
                            self.log(f"🎵 Playing track {i}/{len(tracks)}", "blue")
                            if not self.play_stream(track):
                                break
                        break
                    elif choice.isdigit():
                        track_num = int(choice)
                        if 1 <= track_num <= len(tracks):
                            print()
                            self.play_stream(tracks[track_num - 1])
                            break
                        else:
                            self.log(f"⚠️  Invalid choice. Please enter 1-{len(tracks)} or 'a'", "yellow")
                    else:
                        self.log(f"⚠️  Invalid choice. Please enter 1-{len(tracks)} or 'a'", "yellow")
                        
                except KeyboardInterrupt:
                    self.log("\n👋 Cancelled by user", "yellow")
                    break
    
    def run(self, prompt: Optional[str] = None):
        """Main application flow."""
        print("🎵 Suno Stream Player")
        print("=" * 30)
        print()
        
        # Get prompt
        if not prompt:
            try:
                prompt = input("Enter music prompt: ").strip()
            except KeyboardInterrupt:
                self.log("\n👋 Cancelled by user", "yellow")
                return
        
        if not prompt:
            self.log("❌ No prompt provided", "red")
            return
        
        # Generate music
        task_id = self.generate_music(prompt)
        if not task_id:
            return
        
        # Wait for completion
        tracks = self.wait_for_music(task_id)
        if not tracks:
            self.log("❌ No tracks were generated", "red")
            return
        
        # Play tracks
        self.select_and_play_tracks(tracks)
        
        self.log("🎉 Playback completed!", "green")

def main():
    """Entry point."""
    try:
        player = SunoStreamPlayer()
        prompt = sys.argv[1] if len(sys.argv) > 1 else None
        player.run(prompt)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
