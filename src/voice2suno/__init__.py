"""Voice2Suno - JBL Bluetooth speaker voice-to-music generator."""

from .config import config
from .suno_client import SunoClient

__version__ = "0.1.0"
__all__ = ["config", "SunoClient"]