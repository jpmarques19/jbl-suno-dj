#!/usr/bin/env python3
"""
Fix JBL connection and test audio output
"""

import subprocess
import time
import sys

JBL_MAC = "04:CB:88:B8:CF:72"
JBL_DEVICE = "bluez_output.04_CB_88_B8_CF_72.1"

def run_command(cmd, description="", timeout=10):
    """Run a command and return result."""
    print(f"🔧 {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, 
                              text=True, timeout=timeout)
        if result.returncode == 0:
            print(f"✅ Success: {description}")
            return result.stdout.strip()
        else:
            print(f"⚠️  Warning: {description} - {result.stderr.strip()}")
            return None
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout: {description}")
        return None
    except Exception as e:
        print(f"❌ Error: {description} - {e}")
        return None

def check_bluetooth_status():
    """Check Bluetooth service status."""
    print("📡 Checking Bluetooth status...")
    
    # Check if Bluetooth service is running
    result = run_command("systemctl is-active bluetooth", "Checking Bluetooth service")
    if result != "active":
        print("🔄 Starting Bluetooth service...")
        run_command("sudo systemctl start bluetooth", "Starting Bluetooth service")
    
    # Check if Bluetooth is powered on
    run_command("bluetoothctl power on", "Powering on Bluetooth")
    time.sleep(2)

def connect_jbl():
    """Connect to JBL speaker."""
    print(f"🔊 Connecting to JBL Flip Essential ({JBL_MAC})...")
    
    # Try to connect
    result = run_command(f"bluetoothctl connect {JBL_MAC}", 
                        "Connecting to JBL", timeout=15)
    
    if result and "Connection successful" in result:
        print("✅ JBL connected successfully!")
        return True
    else:
        print("⚠️  Direct connection failed, trying alternative method...")
        
        # Alternative: use expect script for interactive bluetoothctl
        expect_script = f'''
expect -c "
spawn bluetoothctl
expect \\"#\\"
send \\"connect {JBL_MAC}\\r\\"
expect {{
    \\"Connection successful\\" {{ exit 0 }}
    \\"Failed\\" {{ exit 1 }}
    timeout {{ exit 2 }}
}}
"
'''
        result = run_command(expect_script, "Alternative JBL connection")
        return result is not None

def check_audio_devices():
    """Check available audio devices."""
    print("🔍 Checking audio devices...")
    
    result = run_command("pactl list short sinks", "Listing audio sinks")
    if result:
        print("Available audio devices:")
        for line in result.split('\n'):
            if line.strip():
                parts = line.split('\t')
                if len(parts) >= 2:
                    device_name = parts[1]
                    if JBL_DEVICE in device_name:
                        print(f"  ✅ JBL: {device_name}")
                    else:
                        print(f"  📱 {device_name}")
        
        return JBL_DEVICE in result
    return False

def set_jbl_as_default():
    """Set JBL as default audio output."""
    print("🔊 Setting JBL as default audio output...")
    
    # Set as default sink
    run_command(f"pactl set-default-sink {JBL_DEVICE}", "Setting default sink")
    
    # Set volume
    run_command(f"pactl set-sink-volume {JBL_DEVICE} 80%", "Setting volume to 80%")
    
    # Unmute
    run_command(f"pactl set-sink-mute {JBL_DEVICE} 0", "Unmuting JBL")

def test_audio_simple():
    """Test audio with a simple beep."""
    print("🔊 Testing audio with system beep...")
    
    # Generate a test tone
    run_command(f"paplay /usr/share/sounds/alsa/Front_Left.wav --device={JBL_DEVICE}", 
               "Playing test sound", timeout=5)

def test_audio_stream():
    """Test audio with our music stream."""
    print("🎵 Testing with music stream...")
    
    test_url = "https://mfile.erweima.ai/NjVjZDc0NmItMDRlYi00OGRlLWJkMzQtODE0MDNlMGY3Zjk5"
    
    cmd = f'''mpv "{test_url}" \
        --audio-device=pulse/{JBL_DEVICE} \
        --no-video \
        --volume=80 \
        --length=15 \
        --really-quiet'''
    
    print("▶️  Playing music for 15 seconds...")
    print("🎧 You should hear 'Sunshine in My Pocket' on your JBL speaker")
    
    result = run_command(cmd, "Playing music stream", timeout=20)
    return result is not None

def restart_audio_services():
    """Restart audio services."""
    print("🔄 Restarting audio services...")
    
    # Restart PulseAudio/PipeWire
    run_command("systemctl --user restart pipewire", "Restarting PipeWire")
    run_command("systemctl --user restart pipewire-pulse", "Restarting PipeWire Pulse")
    
    time.sleep(3)

def main():
    """Main troubleshooting and testing function."""
    print("🔊 JBL Flip Essentials Connection & Audio Test")
    print("=" * 60)
    
    try:
        # Step 1: Check Bluetooth
        check_bluetooth_status()
        
        # Step 2: Connect JBL
        if not connect_jbl():
            print("❌ Could not connect to JBL speaker")
            print("💡 Please make sure:")
            print("   - JBL Flip Essential is powered on")
            print("   - It's in pairing mode (if needed)")
            print("   - It's within Bluetooth range")
            return False
        
        # Wait for connection to stabilize
        print("⏳ Waiting for connection to stabilize...")
        time.sleep(5)
        
        # Step 3: Check audio devices
        if not check_audio_devices():
            print("❌ JBL not found in audio devices")
            print("🔄 Restarting audio services...")
            restart_audio_services()
            time.sleep(3)
            
            if not check_audio_devices():
                print("❌ JBL still not available as audio device")
                return False
        
        # Step 4: Set as default
        set_jbl_as_default()
        
        # Step 5: Test audio
        print("\n🧪 Testing audio output...")
        
        # Simple test first
        test_audio_simple()
        time.sleep(2)
        
        # Music stream test
        success = test_audio_stream()
        
        if success:
            print("\n🎉 JBL audio test successful!")
            print("✅ Your JBL Flip Essential is ready for voice-controlled music!")
            return True
        else:
            print("\n❌ Audio test failed")
            return False
            
    except KeyboardInterrupt:
        print("\n👋 Test cancelled by user")
        return False
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
