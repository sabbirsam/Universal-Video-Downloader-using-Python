# Universal Video Downloader - Comprehensive Edition

A complete, integrated video downloading solution that supports YouTube, Toffee, and other streaming platforms with full DRM support. This is a comprehensive refactor that provides a unified system for downloading any type of video content.

## 🚀 Quick Start

### 1. Prerequisites

- **Python 3.8+** - Download from [python.org](https://python.org)
- **Windows 10/11** (this setup is optimized for Windows)

### 2. One-Click Installation

#### Option A: Automatic Setup (Recommended)
```cmd
# Clone or download this project
# Open Command Prompt in the project folder
setup.bat
```

#### Option B: Manual Setup
```cmd
# Install Python dependencies
pip install pywidevine
pip install -r requirements.txt

# Download all required tools
python setup_tools.py
```

### 3. Launch the Application

#### Main Launcher (Recommended)
```cmd
python launcher.py
```

#### Direct Access to Specific Downloaders
```cmd
# Universal downloader (all platforms)
python video_downloader.py

# YouTube specialized
python -m yt_dlp "VIDEO_URL"
python -m yt_dlp [URL]

# Toffee specialized  
python toffee.py

# DRM content
python drmtoffee.py
```

## 🎯 Complete Feature Set

### ✅ Supported Platforms & Content Types
- **YouTube** 
  - Public, private, and unlisted videos
  - Playlists and channels
  - Live streams and premieres
  - Age-restricted content
  - All quality options (144p to 8K)
  - Audio-only downloads
  - Subtitle extraction (multiple languages)

- **Toffee** 
  - Regular streaming content
  - Premium/subscription content
  - Live TV channels
  - DRM-protected premium content
  - Multiple quality selection
  - Automatic auth token handling

- **Universal Stream Support**
  - M3U8 live streams and VOD
  - DASH/MPD adaptive streams
  - Direct video URLs
  - HLS streams
  - Progressive downloads

- **DRM Content** 
  - Widevine L3 protected content
  - PSSH extraction and key retrieval
  - Automatic decryption workflow
  - Multiple DRM provider support

### 🛠️ Integrated Tools & Technologies
- **FFmpeg** - Video processing, conversion, and streaming
- **mp4decrypt** - Widevine DRM content decryption
- **N_m3u8DL-RE** - Advanced M3U8/HLS downloader
- **yt-dlp** - YouTube and 1000+ site support
- **pywdevine** - Widevine CDM implementation
- **Custom APIs** - Platform-specific integrations

## 📖 Comprehensive Usage Guide

### 🎬 Main Launcher Interface

The integrated launcher provides access to all functionality:

```cmd
python launcher.py
```

**Main Menu Options:**
1. **Universal Downloader** - All platforms in one interface
2. **YouTube Downloader** - Specialized YouTube features
3. **Toffee Downloader** - Enhanced Toffee support
4. **DRM Downloader** - Advanced DRM content handling
5. **Setup & Configuration** - System configuration
6. **System Tools** - Maintenance and diagnostics

### 📺 YouTube Downloads

#### Interactive Mode
```python
from video_downloader import VideoDownloader

downloader = VideoDownloader()
# Launches interactive menu with quality selection
downloader.download_youtube("https://youtube.com/watch?v=VIDEO_ID", interactive=True)
```

#### Programmatic Usage
```python
# Best quality
downloader.download_youtube("VIDEO_URL", "best")

# Specific quality
downloader.download_youtube("VIDEO_URL", "1080p")

# Audio only
downloader.download_youtube("VIDEO_URL", "audio")
```

#### Advanced YouTube Features
```cmd
# Download entire playlist
python -m yt_dlp "https://youtube.com/playlist?list=PLAYLIST_ID"

# Private video with cookies
python -m yt_dlp --cookies cookies.txt "PRIVATE_VIDEO_URL"

# Custom format selection
python -m yt_dlp -f "bestvideo[height<=1080]+bestaudio" "VIDEO_URL"

# Extract subtitles in multiple languages
python -m yt_dlp --write-subs --sub-langs en,bn,hi "VIDEO_URL"
```

### 🍬 Toffee Downloads

#### Enhanced Toffee Interface
```python
from toffee import ToffeeDownloader

toffee = ToffeeDownloader()
# Interactive MPD analysis and download
toffee.interactive_mpd_download("MPD_URL")
```

#### Regular Content
```python
from video_downloader import VideoDownloader

downloader = VideoDownloader()
downloader.download_toffee("https://toffee.com/live/123456", quality="best")
```

#### Premium/DRM Content
```python
# With authentication
downloader.download_toffee("TOFFEE_URL", auth_token="YOUR_TOKEN", quality="1080p")
```

### 🔐 DRM Content Workflow

#### Complete DRM Download
```python
from drmtoffee import ToffeeDRMDownloader

drm_downloader = ToffeeDRMDownloader()
drm_downloader.download_drm_content("DRM_PROTECTED_URL", "AUTH_TOKEN")
```

#### Manual DRM Process
```python
# 1. Extract PSSH
pssh = drm_downloader.get_pssh_from_mpd("MPD_URL")

# 2. Get decryption keys
keys = drm_downloader.extract_decryption_keys(pssh, video_info)

# 3. Download and decrypt
drm_downloader.download_encrypted_content("MPD_URL", "encrypted.mp4")
drm_downloader.decrypt_content("encrypted.mp4", keys, "decrypted.mp4")
```

### 📡 Stream Downloads

#### M3U8 Streams
```python
# Basic M3U8 download
downloader.download_m3u8("https://example.com/stream.m3u8", "stream_name")

# With custom headers
headers = {"Authorization": "Bearer TOKEN"}
# Headers support coming in next update
```

#### DASH/MPD Streams
```python
# Comprehensive DASH analysis
from toffee import ToffeeDownloader

toffee = ToffeeDownloader()
stream_info = toffee.analyze_mpd_streams("MPD_URL")
toffee.display_stream_info(stream_info)
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