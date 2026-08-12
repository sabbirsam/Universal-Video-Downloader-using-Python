#!/usr/bin/env python3
"""
Universal Video Downloader - Comprehensive Edition
Supports YouTube, Toffee, and other streaming platforms
Handles both regular and DRM-protected content with full integration
"""

import os
import re
import json
import base64
import requests
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import time
import threading
from datetime import datetime

# Core video downloading
import yt_dlp

# Try to import DRM-related modules (optional)
try:
    from pywdevine import PSSH, Device, Cdm
    DRM_AVAILABLE = True
except ImportError:
    DRM_AVAILABLE = False
    print("⚠️  DRM support not available. Install pywdevine for DRM content.")

class VideoDownloader:
    def __init__(self, config_path="config.json"):
        # Load configuration
        self.config = self.load_config(config_path)
        
        # Setup directories
        self.tools_dir = Path(self.config["settings"]["tools_directory"])
        self.downloads_dir = Path(self.config["settings"]["download_directory"])
        self.temp_dir = Path(self.config["settings"]["temp_directory"])
        
        for directory in [self.tools_dir, self.downloads_dir, self.temp_dir]:
            directory.mkdir(exist_ok=True)
        
        # Tool paths
        self.ffmpeg_path = self.tools_dir / "ffmpeg.exe"
        self.mp4decrypt_path = self.tools_dir / "mp4decrypt.exe"
        self.n_m3u8dl_path = self.tools_dir / "N_m3u8DL-RE.exe"
        
        # Headers for API requests
        self.api_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "accept": "*/*",
            "content-type": "application/json"
        }
        
        # Initialize DRM handler if available
        self.drm_handler = None
        if DRM_AVAILABLE:
            try:
                self.drm_handler = DRMHandler(self.config["toffee"]["device_path"])
            except Exception as e:
                print(f"⚠️  DRM handler initialization failed: {e}")
    
    def load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Config file not found: {config_path}. Using defaults.")
            return self.get_default_config()
        except json.JSONDecodeError as e:
            print(f"⚠️  Invalid config file: {e}. Using defaults.")
            return self.get_default_config()
    
    def get_default_config(self):
        """Return default configuration"""
        return {
            "settings": {
                "download_directory": "downloads",
                "temp_directory": "temp", 
                "tools_directory": "tools",
                "max_concurrent_downloads": 3,
                "default_video_quality": "best",
                "default_audio_quality": "best"
            },
            "toffee": {
                "api_base_url": "https://api.toffee.com/v1",
                "license_url": "https://license.toffee.com/v1/license",
                "auth_token": "",
                "device_path": "device.json"
            },
            "youtube": {
                "extract_subtitles": True,
                "subtitle_languages": ["en", "bn"],
                "extract_thumbnails": True,
                "write_info_json": True
            },
            "ffmpeg": {
                "video_codec": "copy",
                "audio_codec": "copy", 
                "output_format": "mp4"
            }
        }
    
    def detect_platform(self, url):
        """Detect which platform the URL belongs to"""
        if "youtube.com" in url or "youtu.be" in url:
            return "youtube"
        elif "toffee.com" in url:
            return "toffee"
        elif ".m3u8" in url:
            return "m3u8"
        elif ".mpd" in url:
            return "dash"
        else:
            return "unknown"
    
    def download_youtube(self, url, quality="best", interactive=True):
        """Enhanced YouTube video downloader with comprehensive support"""
        print(f"🎬 Processing YouTube video: {url}")
        
        # Configure yt-dlp options based on config
        ydl_opts = {
            'format': self.get_youtube_format_string(quality),
            'outtmpl': str(self.downloads_dir / '%(uploader)s - %(title)s [%(id)s].%(ext)s'),
            'writesubtitles': self.config["youtube"]["extract_subtitles"],
            'writeautomaticsub': self.config["youtube"]["extract_subtitles"],
            'subtitleslangs': self.config["youtube"]["subtitle_languages"],
            'writethumbnail': self.config["youtube"]["extract_thumbnails"],
            'writeinfojson': self.config["youtube"]["write_info_json"],
            'ignoreerrors': True,
            'no_warnings': False,
            'extractaudio': False,
            'audioformat': 'mp3',
            'embed_subs': True,
            'writesubtitles': True,
        }
        
        # Add ffmpeg path if available
        if self.ffmpeg_path.exists():
            ydl_opts['ffmpeg_location'] = str(self.ffmpeg_path.parent)
        
        # Add cookies and headers for private/protected content
        ydl_opts.update({
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        })
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get video info first
                print("📡 Extracting video information...")
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    print("❌ Could not extract video information")
                    return False
                
                # Display video information
                self.display_youtube_info(info)
                
                # Handle different content types
                if info.get('_type') == 'playlist':
                    return self.download_youtube_playlist(ydl, info, interactive)
                else:
                    return self.download_youtube_single(ydl, info, interactive, quality)
                    
        except yt_dlp.DownloadError as e:
            if "Private video" in str(e):
                print("🔒 Private video detected. Trying alternative methods...")
                return self.download_youtube_private(url, quality)
            elif "Video unavailable" in str(e):
                print("📵 Video unavailable. Trying to extract direct links...")
                return self.download_youtube_unavailable(url, quality)
            else:
                print(f"❌ YouTube download error: {e}")
                return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def get_youtube_format_string(self, quality):
        """Generate format string based on quality preference"""
        if quality == "best":
            return "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        elif quality == "worst":
            return "worstvideo[ext=mp4]+worstaudio[ext=m4a]/worst[ext=mp4]/worst"
        elif quality == "audio":
            return "bestaudio[ext=m4a]/bestaudio"
        elif quality.endswith('p'):
            height = quality[:-1]
            return f"bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={height}][ext=mp4]/best"
        else:
            return f"{quality}[ext=mp4]/best[ext=mp4]/best"
    
    def display_youtube_info(self, info):
        """Display comprehensive video information"""
        print(f"\n📹 Title: {info.get('title', 'Unknown')}")
        print(f"👤 Uploader: {info.get('uploader', 'Unknown')}")
        print(f"⏱️  Duration: {self.format_duration(info.get('duration', 0))}")
        print(f"👀 Views: {info.get('view_count', 'Unknown'):,}" if info.get('view_count') else "👀 Views: Unknown")
        print(f"📅 Upload Date: {info.get('upload_date', 'Unknown')}")
        
        # Check if video is private/unlisted
        availability = info.get('availability', '')
        if 'private' in availability.lower():
            print("🔒 Status: Private")
        elif 'unlisted' in availability.lower():
            print("🔗 Status: Unlisted")
        else:
            print("🌐 Status: Public")
    
    def format_duration(self, seconds):
        """Format duration in human readable format"""
        if not seconds:
            return "Unknown"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def download_youtube_single(self, ydl, info, interactive, quality):
        """Download single YouTube video"""
        formats = info.get('formats', [])
        
        if interactive and len(formats) > 1:
            # Show format selection
            print("\n📊 Available formats:")
            video_formats = [f for f in formats if f.get('vcodec') != 'none'][-10:]  # Last 10 video formats
            
            for i, fmt in enumerate(video_formats, 1):
                resolution = fmt.get('resolution', 'Unknown')
                ext = fmt.get('ext', 'Unknown')
                filesize = fmt.get('filesize', 0)
                size_mb = f"{filesize / (1024*1024):.1f} MB" if filesize else "Unknown size"
                fps = fmt.get('fps', 'Unknown')
                vcodec = fmt.get('vcodec', 'Unknown')
                print(f"  {i}. {resolution} ({ext}) - {size_mb} - {fps}fps - {vcodec}")
            
            choice = input(f"\nChoose format (1-{len(video_formats)}) or press Enter for {quality}: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(video_formats):
                selected_format = video_formats[int(choice)-1]
                ydl.params['format'] = selected_format['format_id']
        
        # Download the video
        print("📥 Starting download...")
        try:
            ydl.download([info['webpage_url']])
            print("✅ YouTube download completed!")
            return True
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return False
    
    def download_youtube_playlist(self, ydl, info, interactive):
        """Download YouTube playlist"""
        entries = info.get('entries', [])
        playlist_title = info.get('title', 'Unknown Playlist')
        
        print(f"\n📋 Playlist: {playlist_title}")
        print(f"📊 Videos: {len(entries)}")
        
        if interactive:
            choice = input(f"Download all {len(entries)} videos? (y/n): ").strip().lower()
            if choice != 'y':
                return False
        
        # Create playlist directory
        playlist_dir = self.downloads_dir / f"Playlist - {playlist_title}"
        playlist_dir.mkdir(exist_ok=True)
        
        # Update output template for playlist
        ydl.params['outtmpl'] = str(playlist_dir / '%(playlist_index)s - %(title)s [%(id)s].%(ext)s')
        
        try:
            ydl.download([info['webpage_url']])
            print(f"✅ Playlist download completed: {len(entries)} videos")
            return True
        except Exception as e:
            print(f"❌ Playlist download failed: {e}")
            return False
    
    def download_youtube_private(self, url, quality):
        """Attempt to download private YouTube content"""
        print("🔒 Attempting private video download...")
        
        # Try with cookies if available
        cookies_file = Path("cookies.txt")
        if cookies_file.exists():
            ydl_opts = {
                'cookiefile': str(cookies_file),
                'format': self.get_youtube_format_string(quality),
                'outtmpl': str(self.downloads_dir / 'Private - %(title)s [%(id)s].%(ext)s'),
            }
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    print("✅ Private video downloaded successfully!")
                    return True
            except Exception as e:
                print(f"❌ Private video download failed: {e}")
        else:
            print("⚠️  No cookies.txt found. Cannot access private content.")
            print("💡 Export cookies from your browser to cookies.txt for private video access.")
        
        return False
    
    def download_youtube_unavailable(self, url, quality):
        """Attempt to download unavailable YouTube content using alternative methods"""
        print("📵 Attempting unavailable video download...")
        
        # Try different extractors or methods
        extractors = ['youtube', 'generic']
        
        for extractor in extractors:
            try:
                ydl_opts = {
                    'format': self.get_youtube_format_string(quality),
                    'outtmpl': str(self.downloads_dir / 'Unavailable - %(title)s [%(id)s].%(ext)s'),
                    'extractor': extractor,
                    'ignoreerrors': True
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    print(f"✅ Video downloaded using {extractor} extractor!")
                    return True
            except Exception:
                continue
        
        print("❌ Could not download unavailable video with any method")
        return False
    
    def download_m3u8(self, url, output_name=None):
        """Download M3U8 streams using N_m3u8DL-RE"""
        if not self.n_m3u8dl_path.exists():
            print("❌ N_m3u8DL-RE not found. Please run setup first.")
            return
        
        print(f"📺 Downloading M3U8 stream: {url}")
        
        if not output_name:
            output_name = "stream_download"
        
        output_path = self.downloads_dir / output_name
        
        try:
            cmd = [
                str(self.n_m3u8dl_path),
                url,
                "--save-dir", str(self.downloads_dir),
                "--save-name", output_name,
                "--thread-count", "8",
                "--download-retry-count", "3"
            ]
            
            print(f"🔧 Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ M3U8 download completed!")
            else:
                print(f"❌ M3U8 download failed: {result.stderr}")
                
        except Exception as e:
            print(f"❌ M3U8 download error: {e}")
    
    def download_dash_mpd(self, url, output_name=None):
        """Download DASH MPD streams"""
        print(f"🎯 Processing DASH MPD: {url}")
        
        try:
            # Get MPD content
            response = requests.get(url, headers=self.api_headers)
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.content)
            
            print("📋 Available streams:")
            video_streams = []
            audio_streams = []
            
            # Extract video and audio streams
            for adaptation in root.findall('.//{urn:mpeg:dash:schema:mpd:2011}AdaptationSet'):
                content_type = adaptation.get('contentType', '').lower()
                mime_type = adaptation.get('mimeType', '').lower()
                
                if content_type == 'video' or 'video' in mime_type:
                    for rep in adaptation.findall('.//{urn:mpeg:dash:schema:mpd:2011}Representation'):
                        video_streams.append({
                            'id': rep.get('id'),
                            'bandwidth': rep.get('bandwidth'),
                            'width': rep.get('width'),
                            'height': rep.get('height'),
                            'codecs': rep.get('codecs')
                        })
                
                elif content_type == 'audio' or 'audio' in mime_type:
                    for rep in adaptation.findall('.//{urn:mpeg:dash:schema:mpd:2011}Representation'):
                        audio_streams.append({
                            'id': rep.get('id'),
                            'bandwidth': rep.get('bandwidth'),
                            'codecs': rep.get('codecs')
                        })
            
            # Display streams
            print("\n🎥 Video streams:")
            for i, stream in enumerate(video_streams, 1):
                resolution = f"{stream.get('width', '?')}x{stream.get('height', '?')}"
                bandwidth = f"{int(stream.get('bandwidth', 0)) // 1000}k" if stream.get('bandwidth') else '?'
                print(f"  {i}. {resolution} - {bandwidth} - {stream.get('codecs', 'Unknown')}")
            
            print("\n🔊 Audio streams:")
            for i, stream in enumerate(audio_streams, 1):
                bandwidth = f"{int(stream.get('bandwidth', 0)) // 1000}k" if stream.get('bandwidth') else '?'
                print(f"  {i}. {bandwidth} - {stream.get('codecs', 'Unknown')}")
            
            # Use ffmpeg to download
            if self.ffmpeg_path.exists():
                output_file = self.downloads_dir / (output_name or "dash_download.mp4")
                
                cmd = [
                    str(self.ffmpeg_path),
                    "-i", url,
                    "-c", "copy",
                    "-f", "mp4",
                    str(output_file)
                ]
                
                print(f"\n🔧 Downloading with FFmpeg...")
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✅ DASH download completed!")
                else:
                    print(f"❌ DASH download failed: {result.stderr}")
            else:
                print("❌ FFmpeg not found. Please run setup first.")
                
        except Exception as e:
            print(f"❌ DASH processing error: {e}")
    
    def download_toffee(self, video_url, auth_token=None, quality="best"):
        """Download Toffee content (both regular and DRM-protected)"""
        print(f"🍬 Processing Toffee video: {video_url}")
        
        # Extract video ID from different URL patterns
        video_id = self.extract_toffee_video_id(video_url)
        if not video_id:
            print("❌ Invalid Toffee URL format")
            return False
        
        # Set auth token
        headers = self.api_headers.copy()
        if auth_token:
            headers["authorization"] = f"Bearer {auth_token}"
        elif self.config["toffee"]["auth_token"]:
            headers["authorization"] = f"Bearer {self.config['toffee']['auth_token']}"
        
        try:
            # Get video details
            video_info = self.get_toffee_video_info(video_id, headers)
            if not video_info:
                return False
            
            print(f"📹 Title: {video_info.get('title', 'Unknown')}")
            print(f"🎬 Type: {video_info.get('type', 'Unknown')}")
            
            # Check if content is DRM protected
            is_drm_protected = video_info.get('is_drm_protected', False)
            
            if is_drm_protected and DRM_AVAILABLE and self.drm_handler:
                print("🔐 DRM-protected content detected. Processing with DRM handler...")
                return self.download_toffee_drm_content(video_info, headers, quality)
            elif is_drm_protected:
                print("❌ DRM-protected content requires pywdevine. Install with: pip install pywdevine")
                return False
            else:
                print("📺 Regular content detected. Processing...")
                return self.download_toffee_regular_content(video_info, headers, quality)
                
        except Exception as e:
            print(f"❌ Toffee processing error: {e}")
            return False
    
    def extract_toffee_video_id(self, url):
        """Extract video ID from various Toffee URL formats"""
        patterns = [
            r'/live/(\d+)',
            r'/video/(\d+)', 
            r'/watch/(\d+)',
            r'toffee\.com/.*?(\d+)',
            r'id=(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_toffee_video_info(self, video_id, headers):
        """Get comprehensive video information from Toffee API"""
        endpoints = [
            f"{self.config['toffee']['api_base_url']}/videos/{video_id}/details",
            f"{self.config['toffee']['api_base_url']}/content/{video_id}",
            f"{self.config['toffee']['api_base_url']}/live/{video_id}"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract relevant information
                    video_data = data.get('data', {})
                    
                    # Determine if DRM protected
                    is_drm = False
                    streams = video_data.get('streams', [])
                    
                    for stream in streams:
                        if 'drm' in stream.get('url', '').lower() or stream.get('drm_protected'):
                            is_drm = True
                            break
                    
                    return {
                        'id': video_id,
                        'title': video_data.get('title', f'Toffee_Video_{video_id}'),
                        'type': video_data.get('type', 'video'),
                        'streams': streams,
                        'is_drm_protected': is_drm,
                        'raw_data': data
                    }
            except Exception as e:
                print(f"⚠️  Failed to get info from {endpoint}: {e}")
                continue
        
        print("❌ Could not retrieve video information from any endpoint")
        return None
    
    def download_toffee_regular_content(self, video_info, headers, quality):
        """Download regular (non-DRM) Toffee content"""
        streams = video_info.get('streams', [])
        
        # Find best stream based on quality preference
        selected_stream = self.select_toffee_stream(streams, quality)
        if not selected_stream:
            print("❌ No suitable stream found")
            return False
        
        stream_url = selected_stream.get('url')
        stream_format = selected_stream.get('format', '').upper()
        
        print(f"📡 Selected stream: {stream_format} - {selected_stream.get('quality', 'Unknown')}")
        
        # Download based on stream type
        output_name = f"toffee_{video_info['id']}_{video_info['title']}"
        output_name = re.sub(r'[^\w\-_\.]', '_', output_name)  # Sanitize filename
        
        if stream_format == 'HLS' or '.m3u8' in stream_url:
            return self.download_m3u8(stream_url, output_name)
        elif stream_format == 'DASH' or '.mpd' in stream_url:
            return self.download_dash_mpd(stream_url, output_name)
        else:
            # Direct download with ffmpeg
            return self.download_direct_stream(stream_url, output_name, headers)
    
    def download_toffee_drm_content(self, video_info, headers, quality):
        """Download DRM-protected Toffee content"""
        if not self.drm_handler:
            print("❌ DRM handler not available")
            return False
        
        streams = video_info.get('streams', [])
        
        # Find DRM-protected DASH stream
        dash_stream = None
        for stream in streams:
            if stream.get('format', '').upper() == 'DASH' and '.mpd' in stream.get('url', ''):
                dash_stream = stream
                break
        
        if not dash_stream:
            print("❌ No DASH stream found for DRM content")
            return False
        
        mpd_url = dash_stream.get('url')
        print(f"🔐 Processing DRM DASH stream: {mpd_url}")
        
        try:
            # Extract PSSH from MPD
            pssh = self.drm_handler.extract_pssh_from_mpd(mpd_url)
            if not pssh:
                print("❌ Could not extract PSSH from MPD")
                return False
            
            # Get decryption keys
            license_url = self.config['toffee']['license_url']
            keys = self.drm_handler.get_decryption_keys(pssh, license_url, headers)
            if not keys:
                print("❌ Could not obtain decryption keys")
                return False
            
            # Download encrypted content first
            output_name = f"toffee_drm_{video_info['id']}_{video_info['title']}"
            output_name = re.sub(r'[^\w\-_\.]', '_', output_name)
            
            encrypted_file = self.temp_dir / f"{output_name}_encrypted.mp4"
            decrypted_file = self.downloads_dir / f"{output_name}.mp4"
            
            # Download encrypted stream
            print("📥 Downloading encrypted content...")
            if self.download_dash_mpd_to_file(mpd_url, str(encrypted_file)):
                # Decrypt the content
                print("🔓 Decrypting content...")
                if self.drm_handler.decrypt_content(str(encrypted_file), keys, str(decrypted_file)):
                    # Clean up encrypted file
                    encrypted_file.unlink(missing_ok=True)
                    print(f"✅ DRM content downloaded and decrypted: {decrypted_file}")
                    return True
                else:
                    print("❌ Decryption failed")
                    return False
            else:
                print("❌ Failed to download encrypted content")
                return False
                
        except Exception as e:
            print(f"❌ DRM processing error: {e}")
            return False
    
    def select_toffee_stream(self, streams, quality_preference):
        """Select the best stream based on quality preference"""
        if not streams:
            return None
        
        # Sort streams by quality/bandwidth
        quality_streams = []
        for stream in streams:
            bandwidth = stream.get('bandwidth', 0)
            height = stream.get('height', 0)
            quality_score = bandwidth + (height * 1000)  # Prioritize resolution
            
            quality_streams.append({
                **stream,
                'quality_score': quality_score
            })
        
        # Sort by quality score (highest first)
        quality_streams.sort(key=lambda x: x['quality_score'], reverse=True)
        
        # Select based on preference
        if quality_preference == "best":
            return quality_streams[0] if quality_streams else None
        elif quality_preference == "worst":
            return quality_streams[-1] if quality_streams else None
        elif quality_preference.endswith('p'):
            # Try to match specific resolution
            target_height = int(quality_preference[:-1])
            for stream in quality_streams:
                if abs(stream.get('height', 0) - target_height) <= 50:  # Allow some tolerance
                    return stream
            # Fallback to best if exact match not found
            return quality_streams[0] if quality_streams else None
        else:
            return quality_streams[0] if quality_streams else None
    
    def download_direct_stream(self, url, output_name, headers=None):
        """Download direct stream URL"""
        if not self.ffmpeg_path.exists():
            print("❌ FFmpeg not found. Please run setup first.")
            return False
        
        output_file = self.downloads_dir / f"{output_name}.mp4"
        
        cmd = [str(self.ffmpeg_path), "-i", url]
        
        # Add headers if provided
        if headers:
            header_string = "\r\n".join([f"{k}: {v}" for k, v in headers.items()])
            cmd.extend(["-headers", header_string])
        
        cmd.extend([
            "-c", self.config["ffmpeg"]["video_codec"],
            "-c:a", self.config["ffmpeg"]["audio_codec"],
            "-f", self.config["ffmpeg"]["output_format"],
            str(output_file)
        ])
        
        try:
            print(f"🔧 Downloading with FFmpeg...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Download completed: {output_file}")
                return True
            else:
                print(f"❌ Download failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Download error: {e}")
            return False
    
    def download_dash_mpd_to_file(self, mpd_url, output_file):
        """Download DASH MPD to specific file"""
        if not self.ffmpeg_path.exists():
            print("❌ FFmpeg not found. Please run setup first.")
            return False
        
        cmd = [
            str(self.ffmpeg_path),
            "-i", mpd_url,
            "-c", "copy",
            "-f", "mp4",
            output_file
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def interactive_download(self):
        """Enhanced interactive download interface"""
        print("🎬 Universal Video Downloader - Comprehensive Edition")
        print("=" * 60)
        print("Supports: YouTube, Toffee, M3U8, DASH, DRM Content")
        print("=" * 60)
        
        while True:
            print("\n🚀 Main Menu:")
            print("1. 📺 YouTube Download (Public/Private/Playlists)")
            print("2. 🍬 Toffee Download (Regular/Premium/DRM)")
            print("3. 📡 M3U8 Stream Download")
            print("4. 🎯 DASH/MPD Stream Download")
            print("5. 🔐 DRM Content Tools")
            print("6. ⚙️  Settings & Configuration")
            print("7. 📊 Download History")
            print("8. 🔧 System Tools")
            print("9. ❌ Exit")
            
            choice = input("\nSelect option (1-9): ").strip()
            
            if choice == "1":
                self.youtube_menu()
            elif choice == "2":
                self.toffee_menu()
            elif choice == "3":
                self.m3u8_menu()
            elif choice == "4":
                self.dash_menu()
            elif choice == "5":
                self.drm_menu()
            elif choice == "6":
                self.settings_menu()
            elif choice == "7":
                self.history_menu()
            elif choice == "8":
                self.tools_menu()
            elif choice == "9":
                print("👋 Thank you for using Universal Video Downloader!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
    
    def youtube_menu(self):
        """YouTube download submenu"""
        print("\n📺 YouTube Download Options:")
        print("1. Single Video (Best Quality)")
        print("2. Single Video (Custom Quality)")
        print("3. Playlist Download")
        print("4. Audio Only Download")
        print("5. Private/Unlisted Video")
        print("6. Back to Main Menu")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == "1":
            url = input("Enter YouTube URL: ").strip()
            self.download_youtube(url, "best", interactive=False)
        elif choice == "2":
            url = input("Enter YouTube URL: ").strip()
            quality = input("Enter quality (720p/1080p/1440p/2160p/best/worst): ").strip() or "best"
            self.download_youtube(url, quality, interactive=True)
        elif choice == "3":
            url = input("Enter YouTube Playlist URL: ").strip()
            self.download_youtube(url, "best", interactive=True)
        elif choice == "4":
            url = input("Enter YouTube URL: ").strip()
            self.download_youtube(url, "audio", interactive=False)
        elif choice == "5":
            url = input("Enter Private/Unlisted YouTube URL: ").strip()
            quality = input("Enter quality [best]: ").strip() or "best"
            self.download_youtube_private(url, quality)
        elif choice == "6":
            return
        else:
            print("❌ Invalid choice")
    
    def toffee_menu(self):
        """Toffee download submenu"""
        print("\n🍬 Toffee Download Options:")
        print("1. Regular Content")
        print("2. Premium/DRM Content")
        print("3. Live Stream")
        print("4. Configure Auth Token")
        print("5. Back to Main Menu")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            url = input("Enter Toffee URL: ").strip()
            quality = input("Enter quality [best]: ").strip() or "best"
            self.download_toffee(url, quality=quality)
        elif choice == "2":
            url = input("Enter Toffee Premium URL: ").strip()
            auth_token = input("Enter auth token (or press Enter to use config): ").strip() or None
            quality = input("Enter quality [best]: ").strip() or "best"
            self.download_toffee(url, auth_token, quality)
        elif choice == "3":
            url = input("Enter Toffee Live Stream URL: ").strip()
            auth_token = input("Enter auth token (optional): ").strip() or None
            self.download_toffee(url, auth_token, "best")
        elif choice == "4":
            self.configure_toffee_auth()
        elif choice == "5":
            return
        else:
            print("❌ Invalid choice")
    
    def m3u8_menu(self):
        """M3U8 download submenu"""
        print("\n📡 M3U8 Stream Download:")
        url = input("Enter M3U8 URL: ").strip()
        name = input("Enter output name (optional): ").strip() or None
        headers = input("Add custom headers? (y/n): ").strip().lower() == 'y'
        
        if headers:
            print("Enter headers (format: Key: Value, one per line, empty line to finish):")
            custom_headers = {}
            while True:
                header = input().strip()
                if not header:
                    break
                if ':' in header:
                    key, value = header.split(':', 1)
                    custom_headers[key.strip()] = value.strip()
            # TODO: Implement custom headers for M3U8
        
        self.download_m3u8(url, name)
    
    def dash_menu(self):
        """DASH download submenu"""
        print("\n🎯 DASH/MPD Stream Download:")
        url = input("Enter DASH/MPD URL: ").strip()
        name = input("Enter output name (optional): ").strip() or None
        self.download_dash_mpd(url, name)
    
    def drm_menu(self):
        """DRM tools submenu"""
        if not DRM_AVAILABLE:
            print("❌ DRM support not available. Install pywdevine first.")
            input("Press Enter to continue...")
            return
        
        print("\n🔐 DRM Content Tools:")
        print("1. Setup Device Credentials")
        print("2. Extract PSSH from MPD")
        print("3. Test License Server")
        print("4. Decrypt Downloaded File")
        print("5. Full DRM Workflow")
        print("6. Back to Main Menu")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == "1":
            self.setup_drm_device()
        elif choice == "2":
            mpd_url = input("Enter MPD URL: ").strip()
            if self.drm_handler:
                self.drm_handler.extract_pssh_from_mpd(mpd_url)
        elif choice == "3":
            self.test_license_server()
        elif choice == "4":
            self.decrypt_file_menu()
        elif choice == "5":
            self.full_drm_workflow()
        elif choice == "6":
            return
        else:
            print("❌ Invalid choice")
    
    def settings_menu(self):
        """Settings and configuration menu"""
        print("\n⚙️  Settings & Configuration:")
        print("1. View Current Settings")
        print("2. Change Download Directory")
        print("3. Configure Toffee Auth Token")
        print("4. Configure YouTube Settings")
        print("5. Configure FFmpeg Settings")
        print("6. Reset to Defaults")
        print("7. Back to Main Menu")
        
        choice = input("\nSelect option (1-7): ").strip()
        
        if choice == "1":
            self.display_current_settings()
        elif choice == "2":
            self.change_download_directory()
        elif choice == "3":
            self.configure_toffee_auth()
        elif choice == "4":
            self.configure_youtube_settings()
        elif choice == "5":
            self.configure_ffmpeg_settings()
        elif choice == "6":
            self.reset_settings()
        elif choice == "7":
            return
        else:
            print("❌ Invalid choice")
    
    def history_menu(self):
        """Download history menu"""
        print("\n📊 Download History:")
        print("Feature coming soon...")
        input("Press Enter to continue...")
    
    def tools_menu(self):
        """System tools menu"""
        print("\n🔧 System Tools:")
        print("1. Check Tool Installation")
        print("2. Update Tools")
        print("3. Clear Temp Files")
        print("4. Test FFmpeg")
        print("5. Test Network Connection")
        print("6. Back to Main Menu")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == "1":
            self.check_tools()
        elif choice == "2":
            print("Run setup_tools.py to update tools")
        elif choice == "3":
            self.clear_temp_files()
        elif choice == "4":
            self.test_ffmpeg()
        elif choice == "5":
            self.test_network()
        elif choice == "6":
            return
        else:
            print("❌ Invalid choice")
    
    # Helper methods for menu functions
    def configure_toffee_auth(self):
        """Configure Toffee authentication token"""
        print("\n🔑 Configure Toffee Auth Token:")
        print("Current token:", self.config["toffee"]["auth_token"][:20] + "..." if self.config["toffee"]["auth_token"] else "Not set")
        
        new_token = input("Enter new auth token (or press Enter to keep current): ").strip()
        if new_token:
            self.config["toffee"]["auth_token"] = new_token
            self.save_config()
            print("✅ Auth token updated successfully!")
        else:
            print("ℹ️  Auth token unchanged")
    
    def display_current_settings(self):
        """Display current configuration"""
        print("\n📋 Current Settings:")
        print(json.dumps(self.config, indent=2))
        input("\nPress Enter to continue...")
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open("config.json", 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Failed to save config: {e}")
            return False
    
    def check_tools(self):
        """Check if all tools are properly installed"""
        print("\n🔍 Checking Tool Installation:")
        
        tools = {
            "FFmpeg": self.ffmpeg_path,
            "mp4decrypt": self.mp4decrypt_path,
            "N_m3u8DL-RE": self.n_m3u8dl_path
        }
        
        for tool_name, tool_path in tools.items():
            if tool_path.exists():
                print(f"✅ {tool_name}: Installed")
            else:
                print(f"❌ {tool_name}: Not found")
        
        # Check Python packages
        packages = ["yt_dlp", "requests", "pywdevine"]
        for package in packages:
            try:
                __import__(package)
                print(f"✅ {package}: Installed")
            except ImportError:
                print(f"❌ {package}: Not installed")
        
        input("\nPress Enter to continue...")
    
    def clear_temp_files(self):
        """Clear temporary files"""
        import shutil
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                self.temp_dir.mkdir(exist_ok=True)
                print("✅ Temporary files cleared")
            else:
                print("ℹ️  No temporary files to clear")
        except Exception as e:
            print(f"❌ Failed to clear temp files: {e}")
        
        input("Press Enter to continue...")
    
    def test_ffmpeg(self):
        """Test FFmpeg installation"""
        if not self.ffmpeg_path.exists():
            print("❌ FFmpeg not found")
            return
        
        try:
            result = subprocess.run([str(self.ffmpeg_path), "-version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ FFmpeg is working correctly")
                print(f"Version: {result.stdout.split()[2]}")
            else:
                print("❌ FFmpeg test failed")
        except Exception as e:
            print(f"❌ FFmpeg test error: {e}")
        
        input("Press Enter to continue...")
    
    def test_network(self):
        """Test network connectivity"""
        test_urls = [
            "https://www.youtube.com",
            "https://api.toffee.com",
            "https://www.google.com"
        ]
        
        print("\n🌐 Testing Network Connectivity:")
        for url in test_urls:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {url}: OK")
                else:
                    print(f"⚠️  {url}: {response.status_code}")
            except Exception as e:
                print(f"❌ {url}: Failed ({e})")
        
        input("\nPress Enter to continue...")
    
    def setup_drm_device(self):
        """Setup DRM device credentials"""
        if not self.drm_handler:
            print("❌ DRM handler not available")
            return
        
        device_path = Path(self.config["toffee"]["device_path"])
        if device_path.exists():
            print(f"📄 Device file exists: {device_path}")
            choice = input("Overwrite existing device file? (y/n): ").strip().lower()
            if choice != 'y':
                return
        
        self.drm_handler.create_sample_device()
        print("\n⚠️  IMPORTANT: Replace sample credentials with real device credentials!")
        print("💡 Use tools like 'dumper' or 'frida' to extract from Android devices")
        
        input("Press Enter to continue...")

class DRMHandler:
    """Integrated DRM Handler for Widevine content"""
    
    def __init__(self, device_path="device.json"):
        if not DRM_AVAILABLE:
            raise ImportError("pywdevine not available. Install with: pip install pywdevine")
        
        self.device_path = device_path
        self.tools_dir = Path("tools")
        self.mp4decrypt_path = self.tools_dir / "mp4decrypt.exe"
    
    def create_sample_device(self):
        """Create a sample device configuration"""
        sample_device = {
            "device_id": "sample_device_001",
            "device_private_key": "SAMPLE_PRIVATE_KEY_HERE",
            "device_client_id_blob": "SAMPLE_CLIENT_ID_BLOB_HERE", 
            "device_vmp_blob": "SAMPLE_VMP_BLOB_HERE"
        }
        
        with open(self.device_path, 'w') as f:
            json.dump(sample_device, f, indent=2)
        
        print(f"📄 Sample device configuration created: {self.device_path}")
        print("⚠️  Replace with actual device credentials for DRM content")
        return True
    
    def extract_pssh_from_mpd(self, mpd_url):
        """Extract PSSH from MPD manifest"""
        try:
            response = requests.get(mpd_url)
            response.raise_for_status()
            
            # Look for PSSH in different formats
            pssh_patterns = [
                r'<cenc:pssh[^>]*>(.*?)</cenc:pssh>',
                r'<pssh[^>]*>(.*?)</pssh>',
                r'"pssh":\s*"([^"]+)"',
                r'<ContentProtection[^>]*schemeIdUri="urn:uuid:edef8ba9-79d6-4ace-a3c8-27dcd51d21ed"[^>]*>.*?<cenc:pssh[^>]*>(.*?)</cenc:pssh>',
            ]
            
            for pattern in pssh_patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE | re.DOTALL)
                if matches:
                    pssh_b64 = matches[0].strip()
                    print(f"🔑 Found PSSH: {pssh_b64[:50]}...")
                    return pssh_b64
            
            print("❌ No PSSH found in MPD")
            return None
            
        except Exception as e:
            print(f"❌ Error extracting PSSH: {e}")
            return None
    
    def get_decryption_keys(self, pssh_b64, license_url, headers=None):
        """Get decryption keys from license server"""
        if not os.path.exists(self.device_path):
            print(f"❌ Device file not found: {self.device_path}")
            return None
        
        try:
            # Load device
            device = Device.load(self.device_path)
            cdm = Cdm()
            cdm.set_device(device)
            
            # Parse PSSH
            pssh = PSSH(base64.b64decode(pssh_b64))
            
            # Get license challenge
            challenge = cdm.get_license_challenge(pssh)
            
            # Prepare license request payload
            payload = {
                "request": base64.b64encode(challenge).decode()
            }
            
            # Send license request
            response = requests.post(license_url, json=payload, headers=headers or {})
            response.raise_for_status()
            
            # Parse license response
            license_data = response.json().get("data", {}).get("payload")
            if not license_data:
                # Try direct response
                license_data = response.content
            else:
                license_data = base64.b64decode(license_data)
            
            # Extract keys
            keys = cdm.parse_license(license_data)
            
            print(f"🔓 Extracted {len(keys)} decryption keys")
            for key in keys:
                print(f"  Key: {key.get('kid', 'Unknown')} -> {key.get('k', 'Unknown')}")
            
            return keys
            
        except Exception as e:
            print(f"❌ Error getting decryption keys: {e}")
            return None
    
    def decrypt_content(self, encrypted_file, keys, output_file):
        """Decrypt content using mp4decrypt"""
        if not self.mp4decrypt_path.exists():
            print("❌ mp4decrypt not found. Please run setup first.")
            return False
        
        try:
            # Build mp4decrypt command
            cmd = [str(self.mp4decrypt_path)]
            
            # Add keys
            for key in keys:
                if key.get('type') == 'CONTENT':
                    kid = key.get('kid', '').replace('-', '')
                    k = key.get('k', '').replace('-', '')
                    cmd.extend(['--key', f"{kid}:{k}"])
            
            cmd.extend([encrypted_file, output_file])
            
            print(f"🔧 Decrypting content...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Decryption completed: {output_file}")
                return True
            else:
                print(f"❌ Decryption failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Decryption error: {e}")
            return False

def main():
    """Main entry point"""
    print("🚀 Starting Universal Video Downloader...")
    
    try:
        downloader = VideoDownloader()
        downloader.interactive_download()
    except KeyboardInterrupt:
        print("\n\n👋 Download interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check your setup and try again.")

if __name__ == "__main__":
    main()