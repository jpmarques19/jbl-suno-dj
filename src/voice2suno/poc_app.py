"""Proof of Concept CLI application for Suno AI music generation."""

import sys
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.text import Text

from .config import config
from .suno_client import SunoClient

console = Console()


def display_banner():
    """Display application banner."""
    banner = Text("🎵 Suno AI Music Generator POC 🎵", style="bold magenta")
    console.print(Panel(banner, expand=False))


def display_config_status():
    """Display current configuration status."""
    table = Table(title="Configuration Status")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Status", style="yellow")
    
    # Check cookie
    cookie_status = "✅ Set" if config.suno_cookie else "❌ Missing"
    cookie_value = "***hidden***" if config.suno_cookie else "Not set"
    table.add_row("Suno Cookie", cookie_value, cookie_status)
    
    table.add_row("Model Version", config.suno_model_version, "✅ Set")
    table.add_row("Output Directory", str(config.output_dir), "✅ Set")
    table.add_row("Downloads Directory", str(config.downloads_dir), "✅ Set")
    
    console.print(table)


def setup_cookie():
    """Interactive setup for Suno cookie."""
    console.print("\n🔧 Suno Cookie Setup", style="bold blue")
    console.print("You need to get your Suno AI cookie from the browser.")
    console.print("1. Go to https://app.suno.ai/")
    console.print("2. Open Developer Tools (F12)")
    console.print("3. Go to Network tab")
    console.print("4. Look for requests with '_clerk_js_version' parameter")
    console.print("5. Copy the entire Cookie header value")
    
    if Confirm.ask("\nDo you want to enter your cookie now?"):
        cookie = Prompt.ask("Enter your Suno cookie", password=True)
        
        # Save to .env file
        env_file = Path(".env")
        if env_file.exists():
            content = env_file.read_text()
            if "SUNO_COOKIE=" in content:
                # Update existing
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith("SUNO_COOKIE="):
                        lines[i] = f"SUNO_COOKIE={cookie}"
                        break
                env_file.write_text('\n'.join(lines))
            else:
                # Append new
                env_file.write_text(content + f"\nSUNO_COOKIE={cookie}\n")
        else:
            # Create new
            env_file.write_text(f"SUNO_COOKIE={cookie}\n")
        
        console.print("✅ Cookie saved to .env file", style="green")
        console.print("Please restart the application to use the new cookie.", style="yellow")
        return True
    
    return False


def generate_music_interactive(client: SunoClient):
    """Interactive music generation."""
    console.print("\n🎵 Music Generation", style="bold blue")
    
    # Get prompt
    prompt = Prompt.ask("Enter your music prompt (description or lyrics)")
    
    # Ask for generation type
    is_custom = Confirm.ask("Is this custom lyrics? (No = description mode)")
    
    # Optional parameters
    title = Prompt.ask("Song title (optional)", default="")
    tags = Prompt.ask("Voice/style tags (optional)", default="")
    make_instrumental = Confirm.ask("Make instrumental version?", default=False)
    
    try:
        # Generate song
        clips = client.generate_song(
            prompt=prompt,
            is_custom=is_custom,
            title=title if title else None,
            tags=tags if tags else None,
            make_instrumental=make_instrumental,
            wait_audio=config.wait_audio
        )
        
        # Display results
        console.print(f"\n✅ Generated {len(clips)} song(s):", style="green")
        
        for i, clip in enumerate(clips, 1):
            table = Table(title=f"Song {i}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="white")
            
            table.add_row("ID", clip.id)
            table.add_row("Title", clip.title or "Untitled")
            table.add_row("Status", clip.status)
            table.add_row("Model", clip.model_name)
            table.add_row("Audio URL", clip.audio_url or "Pending...")
            
            console.print(table)
        
        # Ask to download
        if Confirm.ask("\nDo you want to download the generated songs?"):
            for clip in clips:
                if clip.audio_url:
                    try:
                        file_path = client.download_song(clip)
                        console.print(f"📁 Saved: {file_path}", style="green")
                    except Exception as e:
                        console.print(f"❌ Download failed: {e}", style="red")
                else:
                    console.print(f"⚠️ Song '{clip.title}' not ready for download", style="yellow")
        
        return clips
        
    except Exception as e:
        console.print(f"❌ Generation failed: {e}", style="red")
        return None


@click.command()
@click.option('--setup', is_flag=True, help='Setup Suno cookie interactively')
@click.option('--credits', is_flag=True, help='Show credits information')
@click.option('--prompt', help='Generate music with this prompt (non-interactive)')
@click.option('--custom', is_flag=True, help='Use custom lyrics mode (with --prompt)')
@click.option('--title', help='Song title (with --prompt)')
@click.option('--tags', help='Voice/style tags (with --prompt)')
@click.option('--instrumental', is_flag=True, help='Make instrumental (with --prompt)')
def main(setup, credits, prompt, custom, title, tags, instrumental):
    """Suno AI Music Generator POC - Generate music from text prompts."""
    
    display_banner()
    
    # Setup mode
    if setup:
        setup_cookie()
        return
    
    # Check configuration
    display_config_status()
    
    if not config.validate():
        missing = config.get_missing_config()
        console.print(f"\n❌ Missing configuration: {', '.join(missing)}", style="red")
        console.print("Run with --setup to configure interactively", style="yellow")
        sys.exit(1)
    
    try:
        # Initialize client
        client = SunoClient()
        
        # Credits mode
        if credits:
            client.get_credits_info()
            return
        
        # Non-interactive mode
        if prompt:
            console.print(f"\n🎵 Generating music for: '{prompt}'", style="blue")
            clips = client.generate_song(
                prompt=prompt,
                is_custom=custom,
                title=title,
                tags=tags,
                make_instrumental=instrumental
            )
            
            # Auto-download
            for clip in clips:
                if clip.audio_url:
                    file_path = client.download_song(clip)
                    console.print(f"📁 Saved: {file_path}", style="green")
            
            return
        
        # Interactive mode
        while True:
            console.print("\n" + "="*50)
            choice = Prompt.ask(
                "Choose an option",
                choices=["generate", "credits", "quit"],
                default="generate"
            )
            
            if choice == "generate":
                generate_music_interactive(client)
            elif choice == "credits":
                client.get_credits_info()
            elif choice == "quit":
                console.print("👋 Goodbye!", style="blue")
                break
    
    except KeyboardInterrupt:
        console.print("\n👋 Goodbye!", style="blue")
    except Exception as e:
        console.print(f"\n❌ Application error: {e}", style="red")
        sys.exit(1)


if __name__ == "__main__":
    main()
