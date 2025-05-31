"""Tests for POC application module."""

from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest
from click.testing import CliRunner

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from voice2suno.poc_app import main
from voice2suno.suno_client import SongClip


class TestPOCApp:
    """Test POC application functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    @patch('voice2suno.poc_app.config')
    @patch('voice2suno.poc_app.SunoClient')
    def test_credits_command(self, mock_client_class, mock_config):
        """Test credits command."""
        # Mock config properties
        mock_config.suno_cookie = 'test_cookie'
        mock_config.suno_model_version = 'chirp-v3-5'
        mock_config.output_dir = Path('./generated_songs')
        mock_config.downloads_dir = Path('./downloads')
        mock_config.validate.return_value = True
        mock_config.get_missing_config.return_value = []

        mock_client = Mock()
        mock_client.get_credits_info.return_value = {
            'credits_left': 50,
            'monthly_limit': 500
        }
        mock_client_class.return_value = mock_client

        result = self.runner.invoke(main, ['--credits'])

        assert result.exit_code == 0
        mock_client.get_credits_info.assert_called_once()
    
    @patch('voice2suno.poc_app.config')
    @patch('voice2suno.poc_app.SunoClient')
    def test_prompt_command(self, mock_client_class, mock_config):
        """Test non-interactive prompt command."""
        mock_config.suno_cookie = 'test_cookie'
        mock_config.validate.return_value = True
        mock_config.get_missing_config.return_value = []

        mock_client = Mock()
        mock_clips = [
            SongClip(
                id='test-1',
                title='Test Song',
                status='complete',
                model_name='chirp-v3-5',
                audio_url='https://example.com/song.mp3'
            )
        ]
        mock_client.generate_song.return_value = mock_clips
        mock_client.download_song.return_value = Path('/tmp/test_song.mp3')
        mock_client_class.return_value = mock_client

        result = self.runner.invoke(main, [
            '--prompt', 'A happy song',
            '--title', 'My Test Song'
        ])

        assert result.exit_code == 0
        mock_client.generate_song.assert_called_once()
        mock_client.download_song.assert_called_once()
    
    def test_setup_command(self):
        """Test setup command."""
        with patch('voice2suno.poc_app.setup_cookie') as mock_setup:
            mock_setup.return_value = True
            
            result = self.runner.invoke(main, ['--setup'])
            
            assert result.exit_code == 0
            mock_setup.assert_called_once()
    
    @patch('voice2suno.poc_app.config')
    def test_missing_cookie_configuration(self, mock_config):
        """Test app fails gracefully with missing cookie."""
        mock_config.suno_cookie = None
        mock_config.validate.return_value = False
        mock_config.get_missing_config.return_value = ['SUNO_COOKIE']

        result = self.runner.invoke(main, ['--credits'])

        assert result.exit_code == 1
        assert 'Missing configuration' in result.output
    
    @patch('voice2suno.poc_app.config')
    @patch('voice2suno.poc_app.SunoClient')
    def test_instrumental_flag(self, mock_client_class, mock_config):
        """Test instrumental flag is passed correctly."""
        mock_config.suno_cookie = 'test_cookie'
        mock_config.validate.return_value = True
        mock_config.get_missing_config.return_value = []

        mock_client = Mock()
        mock_client.generate_song.return_value = []
        mock_client_class.return_value = mock_client

        result = self.runner.invoke(main, [
            '--prompt', 'A happy song',
            '--instrumental'
        ])

        assert result.exit_code == 0
        mock_client.generate_song.assert_called_once()
        call_args = mock_client.generate_song.call_args
        assert call_args[1]['make_instrumental'] is True
    
    @patch('voice2suno.poc_app.config')
    @patch('voice2suno.poc_app.SunoClient')
    def test_custom_lyrics_flag(self, mock_client_class, mock_config):
        """Test custom lyrics flag is passed correctly."""
        mock_config.suno_cookie = 'test_cookie'
        mock_config.validate.return_value = True
        mock_config.get_missing_config.return_value = []

        mock_client = Mock()
        mock_client.generate_song.return_value = []
        mock_client_class.return_value = mock_client

        result = self.runner.invoke(main, [
            '--prompt', 'Verse 1: Happy lyrics...',
            '--custom'
        ])

        assert result.exit_code == 0
        mock_client.generate_song.assert_called_once()
        call_args = mock_client.generate_song.call_args
        assert call_args[1]['is_custom'] is True
