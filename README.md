# JBL-Suno-DJ 🎵

A cross-platform Python tool that uses JBL Bluetooth speakers to listen for spoken prompts, transcribes them with Whisper, generates songs via Suno AI proxy API, and plays the resulting MP3 back through the speaker hands-free.

## 🚀 Suno POC (Proof of Concept)

This repository currently includes a **Proof of Concept** for connecting to Suno AI and generating music from text prompts.

### Features

- 🎵 Generate music using Suno AI's latest models (Chirp v3.5)
- 📝 Support for both description-based and custom lyrics generation
- 🎼 Instrumental and vocal options
- 📥 Automatic song download and management
- 💳 Credits monitoring
- 🖥️ Rich CLI interface with progress indicators
- ⚙️ Easy configuration management

## 📋 Prerequisites

1. **Suno AI Account**: Sign up at [suno.ai](https://app.suno.ai/)
2. **Python 3.12+**: Make sure you have Python installed
3. **Poetry**: For dependency management (or use pip)

## 🔧 Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd jbl-suno-dj
```

### 2. Install dependencies

Using Poetry (recommended):
```bash
poetry install
```

Or using pip:
```bash
pip install -r requirements.txt
```

### 3. Get your Suno AI Cookie

1. Go to [https://app.suno.ai/](https://app.suno.ai/)
2. Open Developer Tools (F12)
3. Go to the **Network** tab
4. Look for requests containing `_clerk_js_version` parameter
5. Copy the entire **Cookie** header value

### 4. Configure environment

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your Suno cookie:
```env
SUNO_COOKIE=your_cookie_here
```

## 🎵 Usage

### Interactive Mode

Run the POC application:
```bash
python3 suno_poc.py
```

Or with Poetry:
```bash
poetry run python3 suno_poc.py
```

### Command Line Mode

Generate music directly from command line:
```bash
# Simple description
python3 suno_poc.py --prompt "A peaceful acoustic guitar melody"

# Custom lyrics
python3 suno_poc.py --prompt "Verse 1: Walking down the street..." --custom --title "My Song"

# Instrumental version
python3 suno_poc.py --prompt "Upbeat electronic dance music" --instrumental
```

### Setup Mode

Configure your Suno cookie interactively:
```bash
python3 suno_poc.py --setup
```

### Check Credits

View your remaining Suno AI credits:
```bash
python3 suno_poc.py --credits
```

## 🧪 Testing

### Unit Tests (No API calls)
Run the comprehensive test suite without consuming credits:
```bash
poetry run pytest tests/
```

### Integration Tests (May consume credits)
Run integration tests that make actual API calls:
```bash
python3 test_suno_poc.py
```

## 📁 Project Structure

```
jbl-suno-dj/
├── src/voice2suno/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── suno_client.py     # Suno AI client wrapper
│   └── poc_app.py         # CLI application
├── tests/                 # Unit tests (no API calls)
│   ├── __init__.py
│   ├── test_config.py     # Configuration tests
│   ├── test_suno_client.py # Client tests with mocks
│   └── test_poc_app.py    # CLI application tests
├── suno_poc.py            # Entry point script
├── test_suno_poc.py       # Integration tests (API calls)
├── pyproject.toml         # Poetry dependencies
└── README.md
```

## 🎛️ Configuration Options

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `SUNO_COOKIE` | Your Suno AI authentication cookie | Required |
| `SUNO_MODEL_VERSION` | Model to use (chirp-v3-5, chirp-v3-0, chirp-v2-0) | chirp-v3-5 |
| `OUTPUT_DIR` | Directory for generated songs | ./generated_songs |
| `DOWNLOADS_DIR` | Directory for downloaded files | ./downloads |
| `DEBUG` | Enable debug logging | false |
| `WAIT_AUDIO` | Wait for audio generation to complete | true |

## 🎼 Available Models

- **chirp-v3-5**: Newest model, better song structure, max 4 minutes
- **chirp-v3-0**: Broad, versatile, max 2 minutes
- **chirp-v2-0**: Vintage Suno model, max 1.3 minutes

## 💡 Examples

### Description Mode
```bash
python3 suno_poc.py --prompt "A melancholic piano ballad about lost love"
```

### Custom Lyrics Mode
```bash
python3 suno_poc.py --prompt "Verse 1: In the quiet of the night..." --custom --title "Midnight Thoughts"
```

### With Style Tags
```bash
python3 suno_poc.py --prompt "Happy birthday song" --tags "cheerful, acoustic, folk"
```

## 🔍 Troubleshooting

### Common Issues

1. **"Suno cookie is required"**
   - Make sure you've set the `SUNO_COOKIE` environment variable
   - Verify your cookie is still valid (they expire periodically)

2. **"Failed to initialize Suno client"**
   - Check your internet connection
   - Verify your cookie is correct and not expired

3. **"Generation failed"**
   - Check if you have sufficient credits
   - Try a simpler prompt
   - Verify your account is in good standing

### Getting Help

- Run unit tests: `poetry run pytest tests/`
- Run integration tests: `python3 test_suno_poc.py`
- Enable debug mode: Set `DEBUG=true` in your `.env` file
- Check your credits: `python3 suno_poc.py --credits`

## 📝 Notes

- Each song generation consumes 5 credits (10 total for a pair)
- Songs are generated in pairs by default
- Generation can take 1-3 minutes depending on the model
- Downloaded songs are saved as MP3 files

## 🚧 Future Development

This POC will be integrated into the full JBL-Suno-DJ system with:
- Voice input via JBL Bluetooth speakers
- Whisper speech-to-text transcription
- Automatic playback through connected speakers
- Hands-free operation

## 📄 License

MIT License - see LICENSE file for details.