#!/usr/bin/env python3
"""
Voice-to-Suno-to-JBL: Complete hands-free music generation workflow
Listen for voice commands → Generate music with Suno → Play on JBL speaker
"""

import speech_recognition as sr
import requests
import json
import time
import subprocess
import sys
import os
import threading
import tempfile
import wave
from typing import Optional, Dict, List

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional

# Configuration
API_KEY = "4e2feeb494648a5f5845dd5b65558544"
BASE_URL = "https://apibox.erweima.ai"
JBL_DEVICE = "bluez_output.04_CB_88_B8_CF_72.1"  # Your JBL Flip Essentials

# Speech Recognition Configuration
SPEECH_SERVICE = "whisper"  # Options: "google", "whisper", "deepgram", "azure"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Set this for Whisper API
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")  # Set this for Deepgram
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")  # Set this for Azure Speech

class VoiceToSunoJBL:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json',
            'User-Agent': 'VoiceToSunoJBL/1.0'
        })
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Adjust for ambient noise and speech recognition settings
        print("🎤 Calibrating microphone for ambient noise...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)

        # Optimize settings for better speech capture
        self.recognizer.pause_threshold = 1.0  # Wait 1 second of silence before considering phrase complete
        self.recognizer.phrase_threshold = 0.3  # Minimum audio length to consider as speech
        self.recognizer.non_speaking_duration = 0.8  # How long to wait for speech to start

        print("✅ Microphone calibrated!")
    
    def log(self, message: str, color: str = "blue"):
        colors = {
            "blue": "\033[0;34m",
            "green": "\033[0;32m", 
            "yellow": "\033[1;33m",
            "red": "\033[0;31m",
            "cyan": "\033[0;36m",
            "magenta": "\033[0;35m",
            "reset": "\033[0m"
        }
        print(f"{colors.get(color, '')}{message}{colors['reset']}")
    
    def listen_for_voice_command(self) -> Optional[str]:
        """Listen for voice input and convert to text with visual countdown."""
        import threading
        import time

        self.log("🎤 Get ready to speak your music request!", "cyan")
        self.log("💡 Example: 'upbeat rock music' or 'jazz melody'", "cyan")

        # Countdown before listening
        for i in range(3, 0, -1):
            print(f"\r🕐 Starting in {i}...", end="", flush=True)
            time.sleep(1)
        print(f"\r🎤 SPEAK NOW! Recording for 10 seconds...                    ")

        # Variables for countdown
        listening = True
        start_time = time.time()
        record_seconds = 10

        def countdown_timer():
            """Show countdown timer while listening."""
            while listening:
                elapsed = time.time() - start_time
                remaining = max(0, record_seconds - elapsed)

                if remaining > 0:
                    print(f"\r⏱️  Recording: {remaining:.1f}s remaining - Keep speaking!    ", end="", flush=True)
                    time.sleep(0.1)
                else:
                    print(f"\r⏰ Recording complete!                                        ")
                    break

        try:
            # Start countdown timer in background
            timer_thread = threading.Thread(target=countdown_timer, daemon=True)
            timer_thread.start()

            with self.microphone as source:
                # Record for exactly 10 seconds, regardless of pauses
                # This ensures we capture the complete speech
                audio = self.recognizer.record(source, duration=record_seconds)

            # Stop countdown and wait for timer thread to finish
            listening = False
            time.sleep(0.2)  # Give timer thread time to finish

            print(f"\r🔄 Processing {record_seconds} seconds of audio... Please wait.              ")

            # Use the configured speech recognition service
            return self.process_audio_with_service(audio)

        except Exception as e:
            listening = False
            time.sleep(0.2)  # Wait for timer thread
            print(f"\r❌ Recording error                                      ")
            self.log(f"❌ Recording error: {e}", "red")
            import traceback
            self.log(f"❌ Traceback: {traceback.format_exc()}", "red")
            return None

    def process_audio_with_service(self, audio) -> Optional[str]:
        """Process audio using the configured speech recognition service."""
        try:
            if SPEECH_SERVICE == "whisper" and OPENAI_API_KEY:
                return self.recognize_with_whisper(audio)
            elif SPEECH_SERVICE == "deepgram" and DEEPGRAM_API_KEY:
                return self.recognize_with_deepgram(audio)
            elif SPEECH_SERVICE == "azure" and AZURE_SPEECH_KEY:
                return self.recognize_with_azure(audio)
            else:
                # Fallback to Google (free)
                return self.recognize_with_google(audio)
        except Exception as e:
            self.log(f"❌ Speech recognition error: {e}", "red")
            return None

    def recognize_with_google(self, audio) -> Optional[str]:
        """Use Google's free speech recognition."""
        try:
            text = self.recognizer.recognize_google(audio, show_all=False)
            if text and text.strip():
                print(f"\r✅ Google: '{text}'                                   ")
                self.log(f"🎯 Google recognized: '{text}'", "green")
                return text.strip()
            else:
                print(f"\r❓ Google: Empty result                                ")
                return None
        except sr.UnknownValueError:
            print(f"\r❓ Google: Could not understand audio                   ")
            return None
        except sr.RequestError as e:
            print(f"\r❌ Google: API error                                    ")
            self.log(f"❌ Google API error: {e}", "red")
            return None

    def recognize_with_whisper(self, audio) -> Optional[str]:
        """Use OpenAI Whisper API for superior accuracy."""
        try:
            # Save audio to temporary WAV file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name

            # Convert audio to WAV format
            with wave.open(temp_path, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(audio.sample_width)
                wav_file.setframerate(audio.sample_rate)
                wav_file.writeframes(audio.frame_data)

            # Call OpenAI Whisper API
            headers = {
                'Authorization': f'Bearer {OPENAI_API_KEY}'
            }

            with open(temp_path, 'rb') as audio_file:
                files = {
                    'file': ('audio.wav', audio_file, 'audio/wav'),
                    'model': (None, 'whisper-1'),
                    'language': (None, 'en')
                }

                response = requests.post(
                    'https://api.openai.com/v1/audio/transcriptions',
                    headers=headers,
                    files=files,
                    timeout=30
                )

            # Clean up temp file
            os.unlink(temp_path)

            if response.status_code == 200:
                result = response.json()
                text = result.get('text', '').strip()
                if text:
                    print(f"\r✅ Whisper: '{text}'                                 ")
                    self.log(f"🎯 Whisper recognized: '{text}'", "green")
                    return text
                else:
                    print(f"\r❓ Whisper: Empty result                              ")
                    return None
            else:
                print(f"\r❌ Whisper: API error {response.status_code}           ")
                self.log(f"❌ Whisper API error: {response.text}", "red")
                return None

        except Exception as e:
            print(f"\r❌ Whisper: Processing error                           ")
            self.log(f"❌ Whisper error: {e}", "red")
            # Clean up temp file if it exists
            try:
                if 'temp_path' in locals():
                    os.unlink(temp_path)
            except:
                pass
            return None

    def recognize_with_deepgram(self, audio) -> Optional[str]:
        """Use Deepgram API for high accuracy."""
        try:
            headers = {
                'Authorization': f'Token {DEEPGRAM_API_KEY}',
                'Content-Type': 'audio/wav'
            }

            # Convert audio to bytes
            audio_data = audio.get_wav_data()

            response = requests.post(
                'https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true',
                headers=headers,
                data=audio_data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                transcript = result.get('results', {}).get('channels', [{}])[0].get('alternatives', [{}])[0].get('transcript', '').strip()
                if transcript:
                    print(f"\r✅ Deepgram: '{transcript}'                          ")
                    self.log(f"🎯 Deepgram recognized: '{transcript}'", "green")
                    return transcript
                else:
                    print(f"\r❓ Deepgram: Empty result                             ")
                    return None
            else:
                print(f"\r❌ Deepgram: API error {response.status_code}         ")
                self.log(f"❌ Deepgram API error: {response.text}", "red")
                return None

        except Exception as e:
            print(f"\r❌ Deepgram: Processing error                          ")
            self.log(f"❌ Deepgram error: {e}", "red")
            return None

    def recognize_with_azure(self, audio) -> Optional[str]:
        """Use Azure Speech Services."""
        try:
            # Azure Speech SDK would be needed here
            # For now, fallback to Google
            self.log("⚠️  Azure Speech not implemented yet, using Google", "yellow")
            return self.recognize_with_google(audio)
        except Exception as e:
            self.log(f"❌ Azure error: {e}", "red")
            return None

    def generate_music(self, prompt: str) -> Optional[str]:
        """Generate music with Suno API."""
        self.log(f"🎵 Generating music: '{prompt}'", "magenta")
        
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
                self.log(f"✅ Generation started! Task ID: {task_id}", "green")
                return task_id
            else:
                self.log(f"❌ API Error: {result.get('msg', 'Unknown error')}", "red")
                return None
                
        except Exception as e:
            self.log(f"❌ Generation failed: {e}", "red")
            return None
    
    def wait_for_music(self, task_id: str) -> List[Dict]:
        """Wait for music generation and return track data."""
        self.log("⏳ Waiting for your music to be generated...", "yellow")
        
        max_attempts = 24  # 6 minutes total
        for attempt in range(1, max_attempts + 1):
            time.sleep(15)
            self.log(f"📡 Checking progress... ({attempt * 15}s elapsed)", "cyan")
            
            try:
                response = self.session.get(
                    f"{BASE_URL}/api/v1/generate/record-info?taskId={task_id}",
                    timeout=30
                )
                response.raise_for_status()
                
                result = response.json()
                if result.get('code') == 200:
                    data = result.get('data', {})

                    # Check for errors first
                    status = data.get('status')
                    if status == 'SENSITIVE_WORD_ERROR':
                        self.log(f"❌ Sensitive word error: {data.get('errorMessage', 'Please rephrase your prompt')}", "red")
                        return []
                    elif status == 'FAILED':
                        self.log(f"❌ Generation failed: {data.get('errorMessage', 'Unknown error')}", "red")
                        return []

                    # Handle response data safely
                    response_data = data.get('response')
                    if response_data is None:
                        # Still pending
                        self.log(f"⏳ Status: {status or 'PENDING'}", "yellow")
                        continue

                    # Get suno data safely
                    suno_data = response_data.get('sunoData') if isinstance(response_data, dict) else None
                    if suno_data is None:
                        # Still processing
                        continue

                    # Check for ready tracks
                    ready_tracks = []
                    if isinstance(suno_data, list):
                        for track in suno_data:
                            if isinstance(track, dict):
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
                        self.log(f"🎉 Music ready! Generated {len(ready_tracks)} track(s)", "green")
                        return ready_tracks
                
            except Exception as e:
                self.log(f"⚠️  Status check failed: {e}", "yellow")
            
            if attempt == max_attempts:
                self.log("⚠️  Generation timeout - music might still be processing", "yellow")
                break
        
        return []
    
    def set_jbl_as_default(self):
        """Set JBL speaker as default audio output."""
        try:
            subprocess.run(['pactl', 'set-default-sink', JBL_DEVICE], 
                         check=True, capture_output=True)
            self.log("🔊 JBL speaker set as audio output", "green")
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"⚠️  Could not set JBL as default: {e}", "yellow")
            return False
    
    def play_on_jbl(self, track: Dict) -> bool:
        """Play music directly on JBL speaker."""
        title = track['title']
        stream_url = track['stream_url']

        self.log(f"🎵 Playing on JBL: {title}", "magenta")
        self.log(f"🔗 Stream URL: {stream_url[:50]}...", "cyan")

        # Test JBL connection first
        self.log("🔊 Testing JBL connection...", "cyan")
        try:
            subprocess.run(['paplay', '/usr/share/sounds/alsa/Front_Right.wav',
                          f'--device={JBL_DEVICE}'],
                         check=True, capture_output=True, timeout=5)
            self.log("✅ JBL connection verified", "green")
        except Exception as e:
            self.log(f"⚠️  JBL connection issue: {e}", "yellow")
            # Try to reconnect
            self.set_jbl_as_default()

        try:
            # Use mpv with specific audio device
            cmd = [
                'mpv', stream_url,
                f'--audio-device=pulse/{JBL_DEVICE}',
                f'--title=JBL: {title}',
                '--no-video',
                '--volume=80',
                '--osd-level=1',
                '--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            ]

            self.log("🔊 Starting playback on JBL Flip Essentials...", "green")
            self.log("🎮 Press 'q' to stop, SPACE to pause/play", "cyan")

            result = subprocess.run(cmd, timeout=300)  # 5 minute timeout

            if result.returncode == 0:
                self.log("✅ Playback completed successfully", "green")
            else:
                self.log(f"⚠️  Playback ended with code {result.returncode}", "yellow")

            return True

        except subprocess.TimeoutExpired:
            self.log("⏰ Playback timeout (5 minutes)", "yellow")
            return True
        except KeyboardInterrupt:
            self.log("\n⏸️  Playback stopped by user", "yellow")
            return True
        except Exception as e:
            self.log(f"❌ JBL playback failed: {e}", "red")

            # Fallback: try with default audio device
            self.log("🔄 Trying fallback playback...", "yellow")
            try:
                subprocess.run(['mpv', stream_url, '--no-video', '--volume=80'],
                             timeout=30)
                return True
            except:
                return False
    
    def speak_status(self, message: str):
        """Use text-to-speech to announce status (optional)."""
        try:
            # Use espeak if available for status announcements
            subprocess.run(['espeak', message], 
                         capture_output=True, timeout=5)
        except:
            pass  # TTS is optional
    
    def run_voice_session(self):
        """Run a single voice-to-music session."""
        # Step 1: Listen for voice command
        prompt = self.listen_for_voice_command()
        if not prompt:
            return False
        
        # Step 2: Generate music
        task_id = self.generate_music(prompt)
        if not task_id:
            self.speak_status("Music generation failed")
            return False
        
        # Step 3: Set JBL as output
        self.set_jbl_as_default()
        
        # Step 4: Wait for music
        self.speak_status("Generating your music, please wait")
        tracks = self.wait_for_music(task_id)
        
        if not tracks:
            self.speak_status("Music generation timed out")
            return False
        
        # Step 5: Play on JBL
        self.speak_status("Your music is ready")
        for track in tracks:
            if not self.play_on_jbl(track):
                break
        
        return True
    
    def run_continuous(self):
        """Run continuous voice listening mode."""
        self.log("🎵 JBL-Suno-DJ: Voice-Controlled Music Generator", "magenta")
        self.log("=" * 60, "magenta")
        self.log("🎤 Say your music request and I'll generate it for you!", "cyan")
        self.log("🔊 Music will play automatically on your JBL Flip Essentials", "cyan")
        self.log("⏹️  Press Ctrl+C to stop", "cyan")
        print()
        
        session_count = 0
        
        try:
            while True:
                session_count += 1
                self.log(f"🎯 Session #{session_count} - Ready for your request!", "blue")
                
                success = self.run_voice_session()
                
                if success:
                    self.log("✅ Session completed successfully!", "green")
                else:
                    self.log("❌ Session failed", "red")
                
                print()
                self.log("🔄 Ready for next request in 3 seconds...", "cyan")
                time.sleep(3)
                
        except KeyboardInterrupt:
            self.log("\n👋 JBL-Suno-DJ stopped. Thanks for using!", "magenta")

def main():
    """Main entry point."""
    try:
        # Check if JBL is connected
        result = subprocess.run(['pactl', 'list', 'short', 'sinks'], 
                              capture_output=True, text=True)
        if JBL_DEVICE not in result.stdout:
            print("❌ JBL Flip Essentials not found!")
            print("💡 Make sure your JBL speaker is paired and connected")
            sys.exit(1)
        
        # Initialize and run
        app = VoiceToSunoJBL()
        
        # Check command line arguments
        if len(sys.argv) > 1 and sys.argv[1] == "--single":
            # Single session mode
            app.run_voice_session()
        else:
            # Continuous mode
            app.run_continuous()
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
