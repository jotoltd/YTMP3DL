# YouTube MP3 Downloader

A desktop GUI app to download YouTube videos as high-quality 320 kbps MP3s.

## Requirements

- Python 3.8+
- ffmpeg (required for MP3 conversion)

## Setup

```bash
# 1. Install ffmpeg (macOS)
brew install ffmpeg

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Run the app
python main.py
```

Or use the included launcher script:
```bash
bash run.sh
```

## Features

- Download single videos or paste multiple URLs (one per line)
- Best quality MP3 at 320 kbps via ffmpeg
- Embeds metadata (title, artist, album art thumbnail)
- Download queue with per-item progress bars
- Custom save directory
- Real-time log output
