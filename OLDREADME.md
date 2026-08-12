# Universal Video Downloader

A comprehensive video downloading tool that supports YouTube, Toffee, and other streaming platforms with DRM support.

## 🚀 Quick Start

### 1. Prerequisites

- **Python 3.8+** - Download from [python.org](https://python.org)
- **Windows 10/11** (this setup is for Windows)

### 2. Installation

#### Option A: Automatic Setup (Recommended)
```cmd
# Clone or download this project
# Open Command Prompt in the project folder
setup.bat
```

#### Option B: Manual Setup
```cmd
# Install Python dependencies
pip install -r requirements.txt

# Download tools
python setup_tools.py
```

### 3. Usage

#### Interactive Mode
```cmd
python video_downloader.py
```

#### Direct YouTube Download
```cmd
# Best quality
python -m yt_dlp "https://youtube.com/watch?v=VIDEO_ID"

# Specific quality
python -m yt_dlp -f "best[height<=720]" "https://youtube.com/watch?v=VIDEO_ID"
```

## 📋 Features

### ✅ Supported Platforms
- **YouTube** - All videos including private/unlisted
- **Toffee** - Regular and premium content
- **M3U8 Streams** - Live and VOD streams
- **DASH/MPD** - Adaptive streaming content
- **DRM Content** - Widevine protected videos (with proper credentials)

### 🛠️ Tools Included
- **FFmpeg** - Video processing and conversion
- **mp4decrypt** - DRM content decryption
- **N_m3u8DL-RE** - Advanced M3U8 downloader
- **yt-dlp** - YouTube and general video downloader

## 📖 Detailed Usage

### YouTube Downloads

#### Basic Usage
```python
from video_downloader import VideoDownloader

downloader = VideoDownloader()
downloader.download_youtube("https://youtube.com/watch?v=VIDEO_ID")
```

#### Quality Options
- `best` - Highest available quality
- `worst` - Lowest available quality  
- `720p` - 720p resolution
- `1080p` - 1080p resolution
- `bestvideo+bestaudio` - Best video + best audio

#### Advanced YouTube Features
```cmd
# Download playlist
python -m yt_dlp "https://youtube.com/playlist?list=PLAYLIST_ID"

# Download with subtitles
python -m yt_dlp --write-subs --sub-langs en,bn "VIDEO_URL"

# Audio only
python -m yt_dlp -f "bestaudio" "VIDEO_URL"
```

### Toffee Downloads

#### Regular Content
```python
downloader.download_toffee_drm("https://toffee.com/live/123456")
```

#### Premium/DRM Content
1. Get your auth token from Toffee website
2. Configure device credentials (see DRM section)
3. Use the DRM handler:

```python
from drm_handler import DRMHandler

handler = DRMHandler()
handler.process_drm_content(mpd_url, license_url, headers)
```

### M3U8 Streams
```python
# Direct M3U8 URL
downloader.download_m3u8("https://example.com/stream.m3u8", "my_stream")
```

### DASH/MPD Streams
```python
# Direct MPD URL
downloader.download_dash_mpd("https://example.com/manifest.mpd", "my_video")
```

## 🔐 DRM Content Setup

### 1. Device Credentials
For DRM content, you need Widevine device credentials:

```cmd
python drm_handler.py
# Select option 1 to create sample device config
# Replace with actual credentials in device.json
```

### 2. Device.json Format
```json
{
  "device_id": "your_device_id",
  "device_private_key": "your_private_key",
  "device_client_id_blob": "your_client_id_blob",
  "device_vmp_blob": "your_vmp_blob"
}
```

### 3. Getting Credentials
- Use tools like **dumper** or **frida** to extract from Android devices
- Legal requirement: Only use your own device credentials
- Alternative: Use CDM-Project or similar services (check legality)

## ⚙️ Configuration

Edit `config.json` to customize settings:

```json
{
  "settings": {
    "download_directory": "downloads",
    "default_video_quality": "best"
  },
  "toffee": {
    "auth_token": "YOUR_TOKEN_HERE"
  },
  "youtube": {
    "extract_subtitles": true,
    "subtitle_languages": ["en", "bn"]
  }
}
```

## 🔧 Troubleshooting

### Common Issues

#### "FFmpeg not found"
```cmd
# Re-run setup
python setup_tools.py
```

#### "DRM support not available"
```cmd
pip install pywdevine
```

#### YouTube download fails
```cmd
# Update yt-dlp
pip install --upgrade yt-dlp
```

#### Toffee auth issues
1. Get fresh auth token from browser
2. Update `config.json` with new token
3. Check if VPN is required

### Tool Verification
```cmd
# Check if tools are installed
tools\ffmpeg.exe -version
tools\mp4decrypt.exe
tools\N_m3u8DL-RE.exe --help
```

## 📁 Project Structure

```
video-downloader/
├── video_downloader.py    # Main downloader
├── drm_handler.py         # DRM processing
├── setup_tools.py         # Tool installer
├── config.json           # Configuration
├── requirements.txt      # Python dependencies
├── setup.bat            # Windows setup script
├── tools/               # Downloaded tools
│   ├── ffmpeg.exe
│   ├── mp4decrypt.exe
│   └── N_m3u8DL-RE.exe
├── downloads/           # Downloaded videos
└── device.json         # DRM device credentials
```

## 🎯 Advanced Usage

### Batch Downloads
```python
urls = [
    "https://youtube.com/watch?v=VIDEO1",
    "https://youtube.com/watch?v=VIDEO2",
    "https://toffee.com/live/123456"
]

for url in urls:
    platform = downloader.detect_platform(url)
    if platform == "youtube":
        downloader.download_youtube(url)
    elif platform == "toffee":
        downloader.download_toffee_drm(url)
```

### Custom Quality Selection
```python
# YouTube with custom format
ydl_opts = {
    'format': 'bestvideo[height<=1080]+bestaudio/best',
    'outtmpl': 'downloads/%(title)s.%(ext)s'
}
```

### Subtitle Extraction
```python
# Enable subtitle download
ydl_opts = {
    'writesubtitles': True,
    'writeautomaticsub': True,
    'subtitleslangs': ['en', 'bn', 'hi']
}
```

## ⚖️ Legal Notice

- Only download content you have permission to download
- Respect copyright laws and platform terms of service
- DRM circumvention may be illegal in some jurisdictions
- Use responsibly and ethically

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📞 Support

For issues and questions:
1. Check troubleshooting section
2. Verify all tools are installed correctly
3. Update dependencies: `pip install --upgrade -r requirements.txt`
4. Check tool versions and compatibility

## 🔄 Updates

To update the downloader:
```cmd
# Update Python packages
pip install --upgrade -r requirements.txt

# Re-download tools if needed
python setup_tools.py
```

---

**Happy downloading! 🎬**