#!/usr/bin/env python3
"""Test script for Suno POC functionality."""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from voice2suno import config, SunoClient
from rich.console import Console

console = Console()


def test_config():
    """Test configuration loading."""
    console.print("🔧 Testing configuration...", style="blue")
    
    console.print(f"Suno Cookie: {'✅ Set' if config.suno_cookie else '❌ Missing'}")
    console.print(f"Model Version: {config.suno_model_version}")
    console.print(f"Output Dir: {config.output_dir}")
    console.print(f"Downloads Dir: {config.downloads_dir}")
    
    if not config.validate():
        console.print("❌ Configuration validation failed", style="red")
        missing = config.get_missing_config()
        console.print(f"Missing: {', '.join(missing)}", style="yellow")
        return False
    
    console.print("✅ Configuration is valid", style="green")
    return True


def test_client_initialization():
    """Test Suno client initialization."""
    console.print("\n🎵 Testing Suno client initialization...", style="blue")
    
    try:
        client = SunoClient()
        console.print("✅ Suno client initialized successfully", style="green")
        return client
    except Exception as e:
        console.print(f"❌ Failed to initialize client: {e}", style="red")
        return None


def test_credits(client: SunoClient):
    """Test credits retrieval."""
    console.print("\n💳 Testing credits retrieval...", style="blue")
    
    try:
        credits = client.get_credits_info()
        console.print(f"✅ Credits info retrieved successfully", style="green")
        return True
    except Exception as e:
        console.print(f"❌ Failed to get credits: {e}", style="red")
        return False


def test_simple_generation(client: SunoClient):
    """Test simple music generation."""
    console.print("\n🎶 Testing simple music generation...", style="blue")
    
    test_prompt = "A peaceful acoustic guitar melody with soft vocals about a sunny day"
    
    try:
        console.print(f"Generating with prompt: '{test_prompt}'")
        clips = client.generate_song(
            prompt=test_prompt,
            is_custom=False,
            title="Test Song - Sunny Day",
            tags="acoustic, peaceful, soft vocals",
            wait_audio=True
        )
        
        console.print(f"✅ Generated {len(clips)} song(s)", style="green")
        
        for i, clip in enumerate(clips, 1):
            console.print(f"Song {i}:")
            console.print(f"  ID: {clip.id}")
            console.print(f"  Title: {clip.title}")
            console.print(f"  Status: {clip.status}")
            console.print(f"  Audio URL: {clip.audio_url or 'Pending...'}")
        
        return clips
        
    except Exception as e:
        console.print(f"❌ Generation failed: {e}", style="red")
        return None


def test_download(client: SunoClient, clips):
    """Test song download."""
    console.print("\n📥 Testing song download...", style="blue")
    
    if not clips:
        console.print("❌ No clips to download", style="red")
        return False
    
    try:
        for clip in clips:
            if clip.audio_url:
                file_path = client.download_song(clip)
                console.print(f"✅ Downloaded: {file_path}", style="green")
            else:
                console.print(f"⚠️ Clip {clip.id} not ready for download", style="yellow")
        
        return True
        
    except Exception as e:
        console.print(f"❌ Download failed: {e}", style="red")
        return False


def main():
    """Run all tests."""
    console.print("🧪 Suno POC Test Suite", style="bold magenta")
    console.print("=" * 50)
    
    # Test 1: Configuration
    if not test_config():
        console.print("\n❌ Configuration test failed. Please set up your environment.", style="red")
        console.print("Create a .env file with: SUNO_COOKIE=your_cookie_here", style="yellow")
        return False
    
    # Test 2: Client initialization
    client = test_client_initialization()
    if not client:
        return False
    
    # Test 3: Credits
    test_credits(client)
    
    # Test 4: Simple generation
    clips = test_simple_generation(client)
    
    # Test 5: Download
    if clips:
        test_download(client, clips)
    
    console.print("\n🎉 Test suite completed!", style="bold green")
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        console.print("\n👋 Test interrupted by user", style="yellow")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n💥 Unexpected error: {e}", style="red")
        sys.exit(1)
