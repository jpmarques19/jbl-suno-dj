#!/usr/bin/env python3
"""
Test JBL speaker audio output
"""

import subprocess
import sys
import time

JBL_DEVICE = "bluez_output.04_CB_88_B8_CF_72.1"

def test_jbl_connection():
    """Test JBL speaker connection and audio output."""
    print("🔊 Testing JBL Flip Essentials Connection")
    print("=" * 50)
    
    # Check if JBL is available
    print("📡 Checking available audio devices...")
    try:
        result = subprocess.run(['pactl', 'list', 'short', 'sinks'], 
                              capture_output=True, text=True, check=True)
        
        print("Available audio sinks:")
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    device_id = parts[0]
                    device_name = parts[1]
                    status = parts[3] if len(parts) > 3 else "UNKNOWN"
                    
                    if JBL_DEVICE in device_name:
                        print(f"  ✅ JBL Found: {device_name} (Status: {status})")
                    else:
                        print(f"  📱 {device_name} (Status: {status})")
        
        if JBL_DEVICE not in result.stdout:
            print("❌ JBL Flip Essentials not found!")
            print("💡 Make sure your JBL speaker is:")
            print("   - Powered on")
            print("   - Paired with your computer")
            print("   - Connected via Bluetooth")
            return False
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error checking audio devices: {e}")
        return False
    
    # Set JBL as default
    print(f"\n🔧 Setting JBL as default audio output...")
    try:
        subprocess.run(['pactl', 'set-default-sink', JBL_DEVICE], 
                     check=True, capture_output=True)
        print("✅ JBL set as default audio output")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Could not set JBL as default: {e}")
    
    # Test audio with existing stream
    print(f"\n🎵 Testing audio playback on JBL...")
    print("🔊 You should hear music playing on your JBL speaker...")
    
    # Use our existing generated music
    test_url = "https://mfile.erweima.ai/NjVjZDc0NmItMDRlYi00OGRlLWJkMzQtODE0MDNlMGY3Zjk5"
    
    try:
        cmd = [
            'mpv', test_url,
            f'--audio-device=pulse/{JBL_DEVICE}',
            '--title=JBL Test: Sunshine in My Pocket',
            '--no-video',
            '--volume=70',
            '--length=30'  # Play for 30 seconds
        ]
        
        print("▶️  Playing test audio for 30 seconds...")
        print("🎮 Press Ctrl+C to stop early")
        
        subprocess.run(cmd)
        
        print("✅ Audio test completed!")
        return True
        
    except KeyboardInterrupt:
        print("\n⏸️  Audio test stopped by user")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Audio playback failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_volume_control():
    """Test volume control on JBL."""
    print(f"\n🔊 Testing volume control...")
    
    volumes = [30, 50, 70, 90, 70]  # Test different volumes
    
    for vol in volumes:
        print(f"🔊 Setting volume to {vol}%...")
        try:
            subprocess.run(['pactl', 'set-sink-volume', JBL_DEVICE, f'{vol}%'], 
                         check=True, capture_output=True)
            time.sleep(1)
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Volume control failed: {e}")
    
    print("✅ Volume control test completed!")

def main():
    """Main test function."""
    try:
        success = test_jbl_connection()
        
        if success:
            test_volume_control()
            print("\n🎉 JBL audio test completed successfully!")
            print("💡 Your JBL Flip Essentials is ready for voice-controlled music!")
        else:
            print("\n❌ JBL audio test failed")
            print("💡 Please check your Bluetooth connection and try again")
            
    except KeyboardInterrupt:
        print("\n👋 Test cancelled")
    except Exception as e:
        print(f"\n💥 Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
