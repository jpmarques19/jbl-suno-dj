"""Tests for Suno client module."""

import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest
import requests

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from voice2suno.suno_client import SunoClient, SongClip


class TestSongClip:
    """Test SongClip data class."""
    
    def test_song_clip_creation(self):
        """Test creating a SongClip from API data."""
        data = {
            'id': 'test-123',
            'title': 'Test Song',
            'status': 'complete',
            'model_name': 'chirp-v3-5',
            'audio_url': 'https://example.com/song.mp3'
        }
        
        clip = SongClip.from_dict(data)
        
        assert clip.id == 'test-123'
        assert clip.title == 'Test Song'
        assert clip.status == 'complete'
        assert clip.model_name == 'chirp-v3-5'
        assert clip.audio_url == 'https://example.com/song.mp3'


class TestSunoClient:
    """Test SunoClient functionality."""
    
    @patch('voice2suno.suno_client.config')
    def test_client_initialization(self, mock_config):
        """Test client initialization."""
        mock_config.suno_cookie = 'test_cookie'
        mock_config.suno_model_version = 'chirp-v3-5'

        client = SunoClient()
        assert client.cookie == 'test_cookie'
        assert 'Cookie' in client.headers
    
    @patch('voice2suno.suno_client.config')
    def test_client_initialization_no_cookie(self, mock_config):
        """Test client initialization fails without cookie."""
        mock_config.suno_cookie = None

        with pytest.raises(ValueError, match="Suno cookie is required"):
            SunoClient()
    
    @patch('voice2suno.suno_client.config')
    def test_get_credits_info_success(self, mock_config):
        """Test getting credits information."""
        mock_config.suno_cookie = 'test_cookie'
        mock_config.suno_model_version = 'chirp-v3-5'

        with patch.object(requests.Session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'credits_left': 50,
                'period': 'monthly',
                'monthly_limit': 500,
                'monthly_usage': 450
            }
            mock_get.return_value = mock_response

            client = SunoClient()
            credits = client.get_credits_info()

            assert credits['credits_left'] == 50
    
    @patch('voice2suno.suno_client.config')
    def test_generate_song_success(self, mock_config):
        """Test successful song generation."""
        mock_config.suno_cookie = 'test_cookie'
        mock_config.suno_model_version = 'chirp-v3-5'

        with patch.object(requests.Session, 'post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'clips': [
                    {
                        'id': 'song-1',
                        'title': 'Generated Song 1',
                        'status': 'streaming',
                        'model_name': 'chirp-v3-5',
                        'audio_url': None
                    },
                    {
                        'id': 'song-2',
                        'title': 'Generated Song 2',
                        'status': 'streaming',
                        'model_name': 'chirp-v3-5',
                        'audio_url': None
                    }
                ]
            }
            mock_post.return_value = mock_response

            client = SunoClient()
            clips = client.generate_song(
                prompt="A happy song",
                is_custom=False,
                wait_audio=False
            )

            assert len(clips) == 2
            assert clips[0].id == 'song-1'
            assert clips[1].id == 'song-2'
    
    @patch('voice2suno.suno_client.config')
    def test_download_song_success(self, mock_config):
        """Test successful song download."""
        mock_config.suno_cookie = 'test_cookie'
        mock_config.suno_model_version = 'chirp-v3-5'
        mock_config.downloads_dir = Path('/tmp')

        with patch.object(requests.Session, 'get') as mock_get:
            # Mock the download response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b'fake mp3 content'
            mock_response.headers = {'content-type': 'audio/mpeg'}
            mock_get.return_value = mock_response

            client = SunoClient()
            clip = SongClip(
                id='test-123',
                title='Test Song',
                status='complete',
                model_name='chirp-v3-5',
                audio_url='https://example.com/song.mp3'
            )

            with patch('pathlib.Path.write_bytes') as mock_write:
                file_path = client.download_song(clip)

                assert 'Test_Song' in str(file_path)
                assert str(file_path).endswith('.mp3')
                mock_write.assert_called_once_with(b'fake mp3 content')
    
    @patch('voice2suno.suno_client.config')
    def test_download_song_no_url(self, mock_config):
        """Test download fails when no audio URL."""
        mock_config.suno_cookie = 'test_cookie'
        mock_config.suno_model_version = 'chirp-v3-5'

        client = SunoClient()
        clip = SongClip(
            id='test-123',
            title='Test Song',
            status='streaming',
            model_name='chirp-v3-5',
            audio_url=None
        )

        with pytest.raises(ValueError, match="No audio URL available"):
            client.download_song(clip)
