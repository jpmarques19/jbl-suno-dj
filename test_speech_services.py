#!/usr/bin/env python3
"""
Test and compare different speech recognition services
"""

import os
import sys
import time

# Add current directory to path
sys.path.insert(0, '.')

def test_speech_services():
    """Test different speech recognition services."""
    print("🎤 Speech Recognition Service Comparison")
    print("=" * 60)
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("💡 Install python-dotenv for .env support: pip install python-dotenv")
    
    # Check available services
    services = []
    
    # Google (always available)
    services.append(("google", "Google Speech (Free)", True))
    
    # OpenAI Whisper
    openai_key = os.getenv("OPENAI_API_KEY")
    services.append(("whisper", "OpenAI Whisper API", bool(openai_key)))
    
    # Deepgram
    deepgram_key = os.getenv("DEEPGRAM_API_KEY")
    services.append(("deepgram", "Deepgram API", bool(deepgram_key)))
    
    print("📋 Available Services:")
    for service_id, name, available in services:
        status = "✅ Ready" if available else "❌ No API key"
        print(f"   {name}: {status}")
    
    print()
    
    # Test each available service
    available_services = [s for s in services if s[2]]
    
    if not available_services:
        print("❌ No speech recognition services available!")
        print("💡 Run setup_speech_recognition.py to configure services")
        return
    
    print("🧪 Testing Services")
    print("=" * 30)
    print("You'll record once, and we'll test it with each service")
    print()
    
    input("Press Enter when ready to record...")
    
    # Record audio once
    print("🎤 Recording 10 seconds of audio...")
    audio = record_audio()
    
    if not audio:
        print("❌ Recording failed")
        return
    
    print("✅ Recording complete!")
    print()
    
    # Test each service
    results = {}
    
    for service_id, name, available in available_services:
        if not available:
            continue
            
        print(f"🔄 Testing {name}...")
        start_time = time.time()
        
        try:
            # Temporarily set the service
            original_service = os.environ.get('SPEECH_SERVICE', 'google')
            os.environ['SPEECH_SERVICE'] = service_id
            
            # Import and test
            from voice_to_suno_jbl import VoiceToSunoJBL
            app = VoiceToSunoJBL()
            
            # Process the audio
            result = app.process_audio_with_service(audio)
            
            # Restore original service
            os.environ['SPEECH_SERVICE'] = original_service
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            results[service_id] = {
                'name': name,
                'result': result,
                'time': processing_time,
                'success': bool(result)
            }
            
            if result:
                print(f"   ✅ Result: '{result}'")
                print(f"   ⏱️  Time: {processing_time:.1f}s")
            else:
                print(f"   ❌ Failed to recognize")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results[service_id] = {
                'name': name,
                'result': None,
                'time': 0,
                'success': False,
                'error': str(e)
            }
        
        print()
    
    # Show comparison
    show_results_comparison(results)

def record_audio():
    """Record audio for testing."""
    try:
        import speech_recognition as sr
        
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        # Quick calibration
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
        
        # Countdown
        for i in range(3, 0, -1):
            print(f"Starting in {i}...")
            time.sleep(1)
        
        print("🔴 Recording 10 seconds - speak now!")
        
        # Record
        with microphone as source:
            audio = recognizer.record(source, duration=10)
        
        print("⏹️  Recording stopped")
        return audio
        
    except Exception as e:
        print(f"❌ Recording error: {e}")
        return None

def show_results_comparison(results):
    """Show comparison of results."""
    print("📊 Results Comparison")
    print("=" * 60)
    
    if not results:
        print("❌ No results to compare")
        return
    
    # Find the most common result (likely correct)
    result_counts = {}
    for data in results.values():
        if data['success']:
            result = data['result'].lower().strip()
            result_counts[result] = result_counts.get(result, 0) + 1
    
    if result_counts:
        most_common = max(result_counts.items(), key=lambda x: x[1])
        print(f"🎯 Most likely correct: '{most_common[0]}'")
        print()
    
    # Show detailed results
    print("Service              | Result                    | Time  | Status")
    print("-" * 70)
    
    for service_id, data in results.items():
        name = data['name'][:18].ljust(18)
        
        if data['success']:
            result = data['result'][:24].ljust(24)
            time_str = f"{data['time']:.1f}s".ljust(5)
            status = "✅ Success"
        else:
            result = "Failed".ljust(24)
            time_str = "-".ljust(5)
            status = "❌ Failed"
        
        print(f"{name} | {result} | {time_str} | {status}")
    
    print()
    
    # Recommendations
    successful_services = [data for data in results.values() if data['success']]
    
    if successful_services:
        # Find fastest
        fastest = min(successful_services, key=lambda x: x['time'])
        print(f"⚡ Fastest: {fastest['name']} ({fastest['time']:.1f}s)")
        
        # Find most accurate (if we can determine)
        if result_counts and most_common[1] > 1:
            accurate_services = [
                data for data in successful_services 
                if data['result'].lower().strip() == most_common[0]
            ]
            if accurate_services:
                print(f"🎯 Most accurate: {', '.join(data['name'] for data in accurate_services)}")
    
    print()
    print("💡 Recommendations:")
    print("   - For best accuracy: OpenAI Whisper")
    print("   - For speed + accuracy: Deepgram")
    print("   - For free option: Google Speech")

def main():
    """Main test function."""
    print("🎤 Speech Recognition Service Tester")
    print("=" * 50)
    print()
    print("This tool will:")
    print("1. Record 10 seconds of audio")
    print("2. Test it with all available speech services")
    print("3. Compare accuracy and speed")
    print()
    
    try:
        test_speech_services()
    except KeyboardInterrupt:
        print("\n👋 Test cancelled")
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
