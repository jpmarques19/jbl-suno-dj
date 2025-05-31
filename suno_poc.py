#!/usr/bin/env python3
"""Entry point for Suno POC application."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from voice2suno.poc_app import main

if __name__ == "__main__":
    main()
