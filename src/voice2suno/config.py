"""Configuration management for Voice2Suno application."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for Voice2Suno application."""
    
    def __init__(self):
        """Initialize configuration with environment variables and defaults."""
        # Suno AI Configuration
        self.suno_cookie: Optional[str] = os.getenv("SUNO_COOKIE")
        self.suno_model_version: str = os.getenv("SUNO_MODEL_VERSION", "chirp-v3-5")
        
        # Output Configuration
        self.output_dir: Path = Path(os.getenv("OUTPUT_DIR", "./generated_songs"))
        self.downloads_dir: Path = Path(os.getenv("DOWNLOADS_DIR", "./downloads"))
        
        # Application Configuration
        self.debug: bool = os.getenv("DEBUG", "false").lower() == "true"
        self.wait_audio: bool = os.getenv("WAIT_AUDIO", "true").lower() == "true"
        
        # Create directories if they don't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
    
    def validate(self) -> bool:
        """Validate that required configuration is present."""
        if not self.suno_cookie:
            return False
        return True
    
    def get_missing_config(self) -> list[str]:
        """Get list of missing required configuration items."""
        missing = []
        if not self.suno_cookie:
            missing.append("SUNO_COOKIE")
        return missing


# Global configuration instance
config = Config()
