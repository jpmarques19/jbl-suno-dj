#!/usr/bin/env python3
"""
Complete workflow test with full debugging output and persistent logs
"""

import sys
import os
import time
import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from voice_to_suno_jbl import VoiceToSunoJBL

class DebugLogger:
    """Logger that keeps all output visible and saves to file."""
    
    def __init__(self):
        self.log_file = f"jbl_suno_debug_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.session_start = time.time()
    
    def log(self, message, level="INFO"):
        """Log message with timestamp."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        elapsed = time.time() - self.session_start
        
        log_line = f"[{timestamp}] [{level:5}] [{elapsed:6.1f}s] {message}"
        
        # Print to console (always visible)
        print(log_line)
        
        # Save to file
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_line + "\n")
        except:
            pass  # Don't let logging errors break the app
    
    def section(self, title):
        """Log a section header."""
        separator = "=" * 60
        self.log(separator)
        self.log(f"🎯 {title}")
        self.log(separator)

def test_complete_workflow_with_debug():
    """Test complete workflow with detailed debugging."""
    logger = DebugLogger()
    
    logger.section("JBL-SUNO-DJ COMPLETE WORKFLOW TEST")
    logger.log("🚀 Starting complete voice-to-music-to-JBL workflow test")
    logger.log(f"📁 Debug log will be saved to: {logger.log_file}")
    logger.log("💡 All output will remain visible for copy/paste debugging")
    print()
    
    try:
        # Initialize app
        logger.section("STEP 1: INITIALIZATION")
        logger.log("🔧 Initializing VoiceToSunoJBL application...")
        
        app = VoiceToSunoJBL()
        logger.log("✅ App initialization successful")
        logger.log(f"📊 Microphone energy threshold: {app.recognizer.energy_threshold}")
        
        # Test JBL connection
        logger.section("STEP 2: JBL SPEAKER CONNECTION")
        logger.log("🔊 Testing JBL Flip Essentials connection...")
        
        jbl_success = app.set_jbl_as_default()
        if jbl_success:
            logger.log("✅ JBL speaker set as default audio device")
        else:
            logger.log("⚠️  JBL setup had issues, but continuing test", "WARN")
        
        # Voice recognition test
        logger.section("STEP 3: VOICE RECOGNITION")
        logger.log("🎤 Testing voice recognition with countdown timer...")
        logger.log("💡 When prompted, say something like:")
        logger.log("   - 'Create a happy song'")
        logger.log("   - 'Generate rock music'")
        logger.log("   - 'Make electronic dance music'")
        print()
        
        input("📝 Press Enter when ready to test voice recognition...")
        
        logger.log("🎤 Starting voice recognition test...")
        start_time = time.time()
        
        prompt = app.listen_for_voice_command()
        
        recognition_time = time.time() - start_time
        logger.log(f"⏱️  Voice recognition took {recognition_time:.1f} seconds")
        
        if prompt:
            logger.log(f"✅ Voice recognition SUCCESS: '{prompt}'")
            use_voice = True
        else:
            logger.log("❌ Voice recognition FAILED", "ERROR")
            logger.log("🔄 Falling back to manual input...")
            prompt = input("Enter your music prompt manually: ").strip()
            if not prompt:
                prompt = "happy electronic music"
            logger.log(f"📝 Using manual prompt: '{prompt}'")
            use_voice = False
        
        # Music generation
        logger.section("STEP 4: MUSIC GENERATION")
        logger.log(f"🎵 Generating music with prompt: '{prompt}'")
        logger.log("💰 Using V3_5 model for cost efficiency")
        
        gen_start_time = time.time()
        task_id = app.generate_music(prompt)
        
        if task_id:
            gen_time = time.time() - gen_start_time
            logger.log(f"✅ Music generation request successful in {gen_time:.1f}s")
            logger.log(f"🆔 Task ID: {task_id}")
        else:
            logger.log("❌ Music generation request FAILED", "ERROR")
            return False
        
        # Wait for music
        logger.section("STEP 5: WAITING FOR MUSIC COMPLETION")
        logger.log("⏳ Waiting for Suno to generate your music...")
        logger.log("📡 This typically takes 1-3 minutes")
        
        wait_start_time = time.time()
        tracks = app.wait_for_music(task_id)
        wait_time = time.time() - wait_start_time
        
        if tracks:
            logger.log(f"✅ Music generation completed in {wait_time:.1f}s")
            logger.log(f"🎵 Generated {len(tracks)} track(s):")
            for i, track in enumerate(tracks):
                logger.log(f"   Track {i+1}: '{track['title']}'")
                logger.log(f"   Stream URL: {track['stream_url'][:50]}...")
                if track.get('duration'):
                    logger.log(f"   Duration: {track['duration']}s")
        else:
            logger.log(f"❌ Music generation TIMEOUT after {wait_time:.1f}s", "ERROR")
            logger.log(f"🆔 Task ID for later checking: {task_id}")
            return False
        
        # JBL playback
        logger.section("STEP 6: JBL PLAYBACK")
        logger.log("🔊 Preparing to play generated music on JBL speaker...")
        logger.log("🎮 Playback controls:")
        logger.log("   SPACE - Play/Pause")
        logger.log("   q - Quit")
        logger.log("   ↑↓ - Volume up/down")
        logger.log("   ←→ - Seek backward/forward")
        print()
        
        input("📝 Press Enter when ready to play music on JBL...")
        
        playback_success = False
        for i, track in enumerate(tracks):
            logger.log(f"🎵 Playing track {i+1}/{len(tracks)}: '{track['title']}'")
            
            play_start_time = time.time()
            success = app.play_on_jbl(track)
            play_time = time.time() - play_start_time
            
            if success:
                logger.log(f"✅ Track {i+1} playback completed ({play_time:.1f}s)")
                playback_success = True
            else:
                logger.log(f"❌ Track {i+1} playback FAILED", "ERROR")
            
            # Ask about next track
            if len(tracks) > 1 and i < len(tracks) - 1:
                choice = input(f"\n📝 Play next track? (y/n): ")
                if not choice.lower().startswith('y'):
                    logger.log("⏹️  User stopped playback")
                    break
        
        # Final summary
        logger.section("WORKFLOW SUMMARY")
        logger.log("📊 Test Results:")
        logger.log(f"   ✅ App Initialization: SUCCESS")
        logger.log(f"   {'✅' if jbl_success else '⚠️ '} JBL Connection: {'SUCCESS' if jbl_success else 'PARTIAL'}")
        logger.log(f"   {'✅' if use_voice else '❌'} Voice Recognition: {'SUCCESS' if use_voice else 'FAILED'}")
        logger.log(f"   ✅ Music Generation: SUCCESS")
        logger.log(f"   {'✅' if playback_success else '❌'} JBL Playback: {'SUCCESS' if playback_success else 'FAILED'}")
        
        overall_success = jbl_success and (use_voice or prompt) and task_id and tracks and playback_success
        logger.log(f"🎯 Overall Result: {'COMPLETE SUCCESS' if overall_success else 'PARTIAL SUCCESS'}")
        
        if not use_voice:
            logger.log("💡 Voice recognition needs improvement - check microphone settings")
        
        logger.log(f"📁 Complete debug log saved to: {logger.log_file}")
        logger.log("📋 You can copy/paste these logs for debugging")
        
        return overall_success
        
    except KeyboardInterrupt:
        logger.log("👋 Test cancelled by user", "INFO")
        return False
    except Exception as e:
        logger.log(f"💥 CRITICAL ERROR: {e}", "ERROR")
        import traceback
        logger.log("📋 Full traceback:", "ERROR")
        for line in traceback.format_exc().split('\n'):
            if line.strip():
                logger.log(f"   {line}", "ERROR")
        return False

def main():
    """Main function."""
    print("🎵 JBL-Suno-DJ Complete Workflow Test with Debug Logging")
    print("=" * 70)
    print("📋 This test will:")
    print("   ✅ Keep all output visible for copy/paste debugging")
    print("   ✅ Save detailed logs to file")
    print("   ✅ Show timestamps and elapsed time")
    print("   ✅ Test the complete voice-to-music-to-JBL workflow")
    print()
    print("💡 ALSA warnings are normal and harmless!")
    print("💡 All logs will remain visible throughout the test")
    print()
    
    try:
        choice = input("🚀 Start complete workflow test? (y/n): ")
        if not choice.lower().startswith('y'):
            print("👋 Test cancelled")
            return
        
        success = test_complete_workflow_with_debug()
        
        if success:
            print("\n🎉 Complete workflow test SUCCESSFUL!")
        else:
            print("\n⚠️  Complete workflow test had issues - check logs above")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Error: {e}")

if __name__ == "__main__":
    main()
