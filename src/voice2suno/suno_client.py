"""Suno AI client for music generation."""

import time
import requests
from pathlib import Path
from typing import List, Optional, Union, Dict, Any
from dataclasses import dataclass
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from .config import config

console = Console()


@dataclass
class SongClip:
    """Represents a generated song clip."""
    id: str
    title: Optional[str] = None
    status: str = "pending"
    model_name: str = "chirp-v3-5"
    audio_url: Optional[str] = None
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    lyric: Optional[str] = None
    prompt: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SongClip':
        """Create SongClip from API response data."""
        return cls(
            id=data.get('id', ''),
            title=data.get('title'),
            status=data.get('status', 'pending'),
            model_name=data.get('model_name', 'chirp-v3-5'),
            audio_url=data.get('audio_url'),
            video_url=data.get('video_url'),
            image_url=data.get('image_url'),
            lyric=data.get('lyric'),
            prompt=data.get('prompt')
        )


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

        # Set up HTTP session with headers
        self.session = requests.Session()
        self.headers = {
            "Cookie": self.cookie,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://app.suno.ai/",
            "Origin": "https://app.suno.ai"
        }
        self.session.headers.update(self.headers)

        # API endpoints
        self.base_url = "https://studio-api.suno.ai"

        console.print(f"✅ Suno client initialized with model: {self.model_version}", style="green")
    
    def generate_song(
        self,
        prompt: str,
        is_custom: bool = False,
        tags: Optional[str] = None,
        title: Optional[str] = None,
        make_instrumental: bool = False,
        wait_audio: bool = True
    ) -> List[SongClip]:
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
            List of generated SongClip objects
        """
        console.print(f"🎵 Generating song with prompt: '{prompt[:50]}...'", style="blue")

        try:
            # Prepare payload for Suno API
            payload = {
                "prompt": prompt,
                "make_instrumental": make_instrumental,
                "wait_audio": wait_audio
            }

            if is_custom:
                payload["tags"] = tags or ""
                payload["title"] = title or ""

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TimeElapsedColumn(),
                console=console,
                transient=True
            ) as progress:
                task = progress.add_task("Generating music...", total=None)

                # Make API request
                response = self.session.post(
                    f"{self.base_url}/api/generate/v2/",
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()

                data = response.json()
                progress.update(task, completed=True)

            # Parse response into SongClip objects
            clips = []
            if 'clips' in data:
                for clip_data in data['clips']:
                    clips.append(SongClip.from_dict(clip_data))

            console.print(f"✅ Generated {len(clips)} song(s)", style="green")
            return clips

        except Exception as e:
            console.print(f"❌ Failed to generate song: {e}", style="red")
            raise
    
    def download_song(self, song: Union[str, SongClip], download_path: Optional[Path] = None) -> Path:
        """
        Download a generated song.

        Args:
            song: Song ID or SongClip object
            download_path: Directory to save the song

        Returns:
            Path to downloaded file
        """
        if download_path is None:
            download_path = config.downloads_dir

        # Get audio URL
        if isinstance(song, SongClip):
            audio_url = song.audio_url
            title = song.title or f"song_{song.id}"
        else:
            raise ValueError("Song must be a SongClip object with audio_url")

        if not audio_url:
            raise ValueError("No audio URL available for download")

        try:
            console.print(f"📥 Downloading song: {title}", style="blue")

            # Download the audio file
            response = self.session.get(audio_url, timeout=60)
            response.raise_for_status()

            # Create safe filename
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_')
            filename = f"{safe_title}.mp3"
            file_path = download_path / filename

            # Save the file
            file_path.write_bytes(response.content)

            console.print(f"✅ Song downloaded to: {file_path}", style="green")
            return file_path

        except Exception as e:
            console.print(f"❌ Failed to download song: {e}", style="red")
            raise
    
    def get_song_info(self, song_id: str) -> SongClip:
        """
        Get information about a specific song.

        Args:
            song_id: ID of the song

        Returns:
            SongClip object with song information
        """
        try:
            response = self.session.get(f"{self.base_url}/api/feed/?ids={song_id}")
            response.raise_for_status()
            data = response.json()

            if data and len(data) > 0:
                return SongClip.from_dict(data[0])
            else:
                raise ValueError(f"Song with ID {song_id} not found")
        except Exception as e:
            console.print(f"❌ Failed to get song info: {e}", style="red")
            raise

    def get_credits_info(self) -> Dict[str, Any]:
        """Get current credits information."""
        try:
            response = self.session.get(f"{self.base_url}/api/billing/info/")
            response.raise_for_status()
            credits = response.json()

            console.print(f"💳 Credits remaining: {credits.get('credits_left', 'unknown')}", style="cyan")
            return credits
        except Exception as e:
            console.print(f"❌ Failed to get credits info: {e}", style="red")
            raise
    
    def wait_for_completion(self, clips: List[SongClip], max_wait_time: int = 300) -> List[SongClip]:
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
