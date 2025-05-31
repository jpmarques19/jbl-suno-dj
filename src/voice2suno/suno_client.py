"""Suno AI client for music generation."""

import time
from pathlib import Path
from typing import List, Optional, Union
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

try:
    from suno import Suno, ModelVersions, Clip
except ImportError:
    raise ImportError(
        "SunoAI library not found. Please install it with: pip install SunoAI"
    )

from .config import config

console = Console()


class SunoClient:
    """Client for interacting with Suno AI music generation API."""
    
    def __init__(self, cookie: Optional[str] = None, model_version: Optional[str] = None):
        """
        Initialize Suno client.
        
        Args:
            cookie: Suno AI authentication cookie
            model_version: Model version to use for generation
        """
        self.cookie = cookie or config.suno_cookie
        self.model_version = model_version or config.suno_model_version
        
        if not self.cookie:
            raise ValueError("Suno cookie is required. Set SUNO_COOKIE environment variable.")
        
        # Initialize Suno client
        try:
            self.client = Suno(
                cookie=self.cookie,
                model_version=self.model_version
            )
            console.print(f"✅ Suno client initialized with model: {self.model_version}", style="green")
        except Exception as e:
            console.print(f"❌ Failed to initialize Suno client: {e}", style="red")
            raise
    
    def generate_song(
        self,
        prompt: str,
        is_custom: bool = False,
        tags: Optional[str] = None,
        title: Optional[str] = None,
        make_instrumental: bool = False,
        wait_audio: bool = True
    ) -> List[Clip]:
        """
        Generate a song using Suno AI.
        
        Args:
            prompt: Description or lyrics for the song
            is_custom: Whether to use custom lyrics (True) or description (False)
            tags: Voice type or characteristics
            title: Title for the generated music
            make_instrumental: Generate instrumental version
            wait_audio: Wait for audio URLs to be ready
            
        Returns:
            List of generated Clip objects
        """
        console.print(f"🎵 Generating song with prompt: '{prompt[:50]}...'", style="blue")
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TimeElapsedColumn(),
                console=console,
                transient=True
            ) as progress:
                task = progress.add_task("Generating music...", total=None)
                
                clips = self.client.generate(
                    prompt=prompt,
                    is_custom=is_custom,
                    tags=tags,
                    title=title,
                    make_instrumental=make_instrumental,
                    wait_audio=wait_audio,
                    model_version=self.model_version
                )
                
                progress.update(task, completed=True)
            
            console.print(f"✅ Generated {len(clips)} song(s)", style="green")
            return clips
            
        except Exception as e:
            console.print(f"❌ Failed to generate song: {e}", style="red")
            raise
    
    def download_song(self, song: Union[str, Clip], download_path: Optional[Path] = None) -> str:
        """
        Download a generated song.
        
        Args:
            song: Song ID or Clip object
            download_path: Directory to save the song
            
        Returns:
            Path to downloaded file
        """
        if download_path is None:
            download_path = config.downloads_dir
        
        try:
            console.print(f"📥 Downloading song...", style="blue")
            
            file_path = self.client.download(
                song=song,
                path=str(download_path)
            )
            
            console.print(f"✅ Song downloaded to: {file_path}", style="green")
            return file_path
            
        except Exception as e:
            console.print(f"❌ Failed to download song: {e}", style="red")
            raise
    
    def get_song_info(self, song_id: str) -> Clip:
        """
        Get information about a specific song.
        
        Args:
            song_id: ID of the song
            
        Returns:
            Clip object with song information
        """
        try:
            songs = self.client.get_songs(song_ids=song_id)
            if songs:
                return songs[0]
            else:
                raise ValueError(f"Song with ID {song_id} not found")
        except Exception as e:
            console.print(f"❌ Failed to get song info: {e}", style="red")
            raise
    
    def get_credits_info(self):
        """Get current credits information."""
        try:
            credits = self.client.get_credits()
            console.print(f"💳 Credits remaining: {credits.credits_left}/{credits.monthly_limit}", style="cyan")
            return credits
        except Exception as e:
            console.print(f"❌ Failed to get credits info: {e}", style="red")
            raise
    
    def wait_for_completion(self, clips: List[Clip], max_wait_time: int = 300) -> List[Clip]:
        """
        Wait for song generation to complete.
        
        Args:
            clips: List of clips to wait for
            max_wait_time: Maximum time to wait in seconds
            
        Returns:
            Updated list of clips with audio URLs
        """
        console.print("⏳ Waiting for song generation to complete...", style="yellow")
        
        start_time = time.time()
        completed_clips = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Waiting for completion...", total=len(clips))
            
            while len(completed_clips) < len(clips) and (time.time() - start_time) < max_wait_time:
                for clip in clips:
                    if clip not in completed_clips:
                        try:
                            updated_clip = self.get_song_info(clip.id)
                            if updated_clip.audio_url and updated_clip.status == "complete":
                                completed_clips.append(updated_clip)
                                progress.advance(task)
                                console.print(f"✅ Song '{updated_clip.title}' completed", style="green")
                        except Exception:
                            pass  # Continue waiting
                
                if len(completed_clips) < len(clips):
                    time.sleep(5)  # Wait 5 seconds before checking again
        
        if len(completed_clips) < len(clips):
            console.print(f"⚠️ Only {len(completed_clips)}/{len(clips)} songs completed within timeout", style="yellow")
        
        return completed_clips
