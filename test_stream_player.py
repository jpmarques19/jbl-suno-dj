#!/usr/bin/env python3
"""
Quick test of stream player with existing Suno track
"""

import subprocess
import sys

def test_stream_playback():
    """Test streaming playback with existing track."""
    
    # Use the track we generated earlier
    stream_url = "https://mfile.erweima.ai/NjVjZDc0NmItMDRlYi00OGRlLWJkMzQtODE0MDNlMGY3Zjk5"
    title = "Sunshine in My Pocket"
    
    print("🎵 Testing Suno Stream Playback")
    print("=" * 40)
    print(f"🎵 Track: {title}")
    print(f"🔗 Stream URL: {stream_url[:50]}...")
    print()
    
    # Find available player
    players = [
        ('mpv', [
            'mpv', stream_url,
            f'--title=Suno: {title}',
            '--no-video',
            '--volume=70',
            '--osd-level=2'
        ]),
        ('vlc', [
            'vlc', stream_url,
            '--intf', 'ncurses',
            '--no-video',
            '--volume', '70'
        ]),
        ('mplayer', [
            'mplayer', stream_url,
            '-volume', '70',
            '-title', f'Suno: {title}'
        ]),
        ('ffplay', [
            'ffplay', stream_url,
            '-nodisp',
            '-volume', '70'
        ])
    ]
    
    for player_name, command in players:
        try:
            # Test if player is available
            subprocess.run([player_name, '--version'], 
                         capture_output=True, timeout=5)
            
            print(f"✅ Using {player_name} player")
            print()
            print("🎮 PLAYBACK CONTROLS:")
            if player_name == 'mpv':
                print("  SPACE - Play/Pause")
                print("  ← → - Seek backward/forward")
                print("  ↑ ↓ - Volume up/down")
                print("  q - Quit")
                print("  m - Mute/Unmute")
            elif player_name == 'vlc':
                print("  SPACE - Play/Pause")
                print("  Ctrl+← → - Seek")
                print("  Ctrl+↑ ↓ - Volume")
                print("  q - Quit")
            else:
                print("  SPACE - Play/Pause")
                print("  ← → - Seek")
                print("  ↑ ↓ - Volume")
                print("  q - Quit")
            
            print()
            print("▶️  Starting playback...")
            print()
            
            # Start playback
            subprocess.run(command)
            
            print()
            print("✅ Playback completed!")
            return True
            
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            continue
    
    print("❌ No compatible audio player found!")
    print("💡 Please install one of: mpv, vlc, mplayer, or ffplay")
    print(f"🔗 Direct stream URL: {stream_url}")
    return False

def main():
    """Main function."""
    try:
        test_stream_playback()
    except KeyboardInterrupt:
        print("\n👋 Playback interrupted by user")
    except Exception as e:
        print(f"\n💥 Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
