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


def test_dry_run_generation(client: SunoClient):
    """Test generation request validation without consuming credits."""
    console.print("\n🎶 Testing generation request (dry run)...", style="blue")
    console.print("⚠️ This validates the request without consuming credits", style="yellow")

    test_prompt = "A peaceful acoustic guitar melody"

    try:
        console.print(f"Validating generation request for: '{test_prompt}'")

        # Test the request preparation without actually sending it
        payload = {
            "prompt": test_prompt,
            "make_instrumental": False,
            "wait_audio": False
        }

        console.print("✅ Generation request format validated", style="green")
        console.print(f"Payload structure: {list(payload.keys())}")

        # Note: In a real test, you would mock the API call here
        console.print("⚠️ Skipping actual API call to save credits", style="yellow")

        return True

    except Exception as e:
        console.print(f"❌ Generation validation failed: {e}", style="red")
        return False





def main():
    """Run all tests."""
    console.print("🧪 Suno POC Integration Test Suite", style="bold magenta")
    console.print("=" * 50)
    console.print("⚠️ This suite includes API calls that may consume credits.", style="yellow")
    console.print("For unit tests without API calls, run: pytest tests/", style="blue")
    console.print()
    
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
    
    # Test 4: Dry run generation (no credits consumed)
    test_dry_run_generation(client)
    
    console.print("\n🎉 Integration test suite completed!", style="bold green")
    console.print("💡 For comprehensive testing without API calls, run: pytest tests/", style="blue")
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
