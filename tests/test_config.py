"""Tests for configuration module."""

import os
import tempfile
from pathlib import Path
import pytest
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from voice2suno.config import Config


class TestConfig:
    """Test configuration management."""
    
    def test_config_initialization(self):
        """Test config initialization with defaults."""
        config = Config()
        
        assert config.suno_model_version == "chirp-v3-5"
        assert config.output_dir == Path("./generated_songs")
        assert config.downloads_dir == Path("./downloads")
        assert config.debug is False
        assert config.wait_audio is True
    
    @patch.dict(os.environ, {
        'SUNO_COOKIE': 'test_cookie_123',
        'SUNO_MODEL_VERSION': 'chirp-v3-0',
        'OUTPUT_DIR': '/tmp/songs',
        'DEBUG': 'true'
    })
    def test_config_from_environment(self):
        """Test config loading from environment variables."""
        config = Config()
        
        assert config.suno_cookie == 'test_cookie_123'
        assert config.suno_model_version == 'chirp-v3-0'
        assert config.output_dir == Path('/tmp/songs')
        assert config.debug is True
    
    def test_config_validation_missing_cookie(self):
        """Test validation fails when cookie is missing."""
        config = Config()
        config.suno_cookie = None
        
        assert not config.validate()
        missing = config.get_missing_config()
        assert 'SUNO_COOKIE' in missing
    
    @patch.dict(os.environ, {'SUNO_COOKIE': 'test_cookie'})
    def test_config_validation_success(self):
        """Test validation succeeds with required config."""
        config = Config()
        
        assert config.validate()
        missing = config.get_missing_config()
        assert len(missing) == 0
    
    def test_config_directories_creation(self):
        """Test that directories are created when accessed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {
                'OUTPUT_DIR': str(Path(temp_dir) / "test_output"),
                'DOWNLOADS_DIR': str(Path(temp_dir) / "test_downloads")
            }):
                config = Config()

                # Directories should be created during initialization
                assert config.output_dir.exists()
                assert config.downloads_dir.exists()
