#!/usr/bin/env python3
"""
Toffee Video Downloader - Integrated with Universal Video Downloader
Enhanced version with full Toffee platform support
"""

import requests
import xml.etree.ElementTree as ET
import subprocess
import os
import re
import json
from pathlib import Path
from video_downloader import VideoDownloader

class ToffeeDownloader:
    """Specialized Toffee downloader with enhanced features"""
    
    def __init__(self):
        self.base_downloader = VideoDownloader()
        self.api_base = "https://api.toffee.com/v1"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "accept": "*/*",
            "content-type": "application/json"
        }
    
    def extract_title_from_mpd(self, mpd_url):
        """Enhanced title extraction from MPD file"""
        try:
            response = requests.get(mpd_url, headers=self.headers)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            
            # Try multiple methods to extract title
            title_sources = [
                root.get('title'),
                root.findtext('.//title'),
                root.findtext('.//{urn:mpeg:dash:schema:mpd:2011}title'),
                root.get('id'),
                'Unknown_Toffee_Video'
            ]
            
            for title in title_sources:
                if title and title.strip():
                    return title.strip()
            
            return 'Unknown_Toffee_Video'
            
        except Exception as e:
            print(f"❌ Error extracting title: {e}")
            return 'Unknown_Toffee_Video'
    
    def analyze_mpd_streams(self, mpd_url):
        """Comprehensive MPD stream analysis"""
        try:
            response = requests.get(mpd_url, headers=self.headers)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            
            print("🔍 Analyzing MPD streams...")
            
            video_streams = []
            audio_streams = []
            subtitle_streams = []
            
            # Handle different namespace scenarios
            namespaces = {
                'mpd': 'urn:mpeg:dash:schema:mpd:2011',
                'cenc': 'urn:mpeg:cenc:2013'
            }
            
            # Find adaptation sets
            adaptation_sets = root.findall('.//AdaptationSet') or root.findall('.//{urn:mpeg:dash:schema:mpd:2011}AdaptationSet')
            
            for adaptation in adaptation_sets:
                content_type = adaptation.get('contentType', '').lower()
                mime_type = adaptation.get('mimeType', '').lower()
                
                # Determine stream type
                if content_type == 'video' or 'video' in mime_type:
                    for rep in adaptation.findall('.//Representation') or adaptation.findall('.//{urn:mpeg:dash:schema:mpd:2011}Representation'):
                        video_stream = {
                            'id': rep.get('id'),
                            'bandwidth': int(rep.get('bandwidth', 0)),
                            'width': int(rep.get('width', 0)) if rep.get('width') else 0,
                            'height': int(rep.get('height', 0)) if rep.get('height') else 0,
                            'codecs': rep.get('codecs', 'Unknown'),
                            'fps': rep.get('frameRate', 'Unknown')
                        }
                        video_streams.append(video_stream)
                
                elif content_type == 'audio' or 'audio' in mime_type:
                    for rep in adaptation.findall('.//Representation') or adaptation.findall('.//{urn:mpeg:dash:schema:mpd:2011}Representation'):
                        audio_stream = {
                            'id': rep.get('id'),
                            'bandwidth': int(rep.get('bandwidth', 0)),
                            'codecs': rep.get('codecs', 'Unknown'),
                            'sample_rate': rep.get('audioSamplingRate', 'Unknown'),
                            'channels': adaptation.get('lang', 'Unknown')
                        }
                        audio_streams.append(audio_stream)
                
                elif content_type == 'text' or 'subtitle' in mime_type.lower():
                    subtitle_stream = {
                        'lang': adaptation.get('lang', 'Unknown'),
                        'mime_type': mime_type
                    }
                    subtitle_streams.append(subtitle_stream)
            
            return {
                'video': sorted(video_streams, key=lambda x: x['bandwidth'], reverse=True),
                'audio': sorted(audio_streams, key=lambda x: x['bandwidth'], reverse=True),
                'subtitles': subtitle_streams,
                'title': self.extract_title_from_mpd(mpd_url)
            }
            
        except Exception as e:
            print(f"❌ Error analyzing MPD: {e}")
            return None
    
    def display_stream_info(self, stream_info):
        """Display comprehensive stream information"""
        if not stream_info:
            print("❌ No stream information available")
            return
        
        print(f"\n📹 Title: {stream_info['title']}")
        
        print("\n🎥 Video Streams:")
        for i, stream in enumerate(stream_info['video'], 1):
            resolution = f"{stream['width']}x{stream['height']}" if stream['width'] and stream['height'] else "Unknown"
            bandwidth_mbps = stream['bandwidth'] / 1000000 if stream['bandwidth'] else 0
            print(f"  {i}. {resolution} - {bandwidth_mbps:.1f} Mbps - {stream['codecs']} - {stream['fps']} fps")
        
        print("\n🔊 Audio Streams:")
        for i, stream in enumerate(stream_info['audio'], 1):
            bandwidth_kbps = stream['bandwidth'] / 1000 if stream['bandwidth'] else 0
            print(f"  {i}. {bandwidth_kbps:.0f} kbps - {stream['codecs']} - {stream['sample_rate']} Hz")
        
        if stream_info['subtitles']:
            print("\n📝 Subtitle Streams:")
            for i, stream in enumerate(stream_info['subtitles'], 1):
                print(f"  {i}. {stream['lang']} - {stream['mime_type']}")
    
    def interactive_mpd_download(self, mpd_url):
        """Interactive MPD download with stream selection"""
        print(f"🍬 Processing Toffee MPD: {mpd_url}")
        
        # Analyze streams
        stream_info = self.analyze_mpd_streams(mpd_url)
        if not stream_info:
            return False
        
        # Display stream information
        self.display_stream_info(stream_info)
        
        # Get user preferences
        print("\n⚙️  Download Options:")
        print("1. Best quality (automatic)")
        print("2. Select specific quality")
        print("3. Audio only")
        print("4. Custom FFmpeg download")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            return self.download_best_quality(mpd_url, stream_info)
        elif choice == "2":
            return self.download_selected_quality(mpd_url, stream_info)
        elif choice == "3":
            return self.download_audio_only(mpd_url, stream_info)
        elif choice == "4":
            return self.download_custom_ffmpeg(mpd_url, stream_info)
        else:
            print("❌ Invalid choice")
            return False
    
    def download_best_quality(self, mpd_url, stream_info):
        """Download best quality automatically"""
        output_name = f"toffee_{stream_info['title']}"
        output_name = re.sub(r'[^\w\-_\.]', '_', output_name)
        
        return self.base_downloader.download_dash_mpd(mpd_url, output_name)
    
    def download_selected_quality(self, mpd_url, stream_info):
        """Download with user-selected quality"""
        video_streams = stream_info['video']
        
        if not video_streams:
            print("❌ No video streams available")
            return False
        
        print("\nSelect video quality:")
        for i, stream in enumerate(video_streams, 1):
            resolution = f"{stream['width']}x{stream['height']}" if stream['width'] and stream['height'] else "Unknown"
            bandwidth_mbps = stream['bandwidth'] / 1000000 if stream['bandwidth'] else 0
            print(f"  {i}. {resolution} - {bandwidth_mbps:.1f} Mbps")
        
        try:
            selection = int(input(f"\nEnter choice (1-{len(video_streams)}): ").strip())
            if 1 <= selection <= len(video_streams):
                selected_stream = video_streams[selection - 1]
                
                # Use FFmpeg with specific stream selection
                output_name = f"toffee_{stream_info['title']}_{selected_stream['width']}x{selected_stream['height']}"
                output_name = re.sub(r'[^\w\-_\.]', '_', output_name)
                
                return self.download_with_stream_selection(mpd_url, selected_stream, output_name)
            else:
                print("❌ Invalid selection")
                return False
        except ValueError:
            print("❌ Please enter a valid number")
            return False
    
    def download_audio_only(self, mpd_url, stream_info):
        """Download audio only"""
        output_name = f"toffee_audio_{stream_info['title']}"
        output_name = re.sub(r'[^\w\-_\.]', '_', output_name)
        
        ffmpeg_path = self.base_downloader.ffmpeg_path
        if not ffmpeg_path.exists():
            print("❌ FFmpeg not found")
            return False
        
        output_file = self.base_downloader.downloads_dir / f"{output_name}.m4a"
        
        cmd = [
            str(ffmpeg_path),
            "-i", mpd_url,
            "-vn",  # No video
            "-c:a", "copy",
            "-f", "mp4",
            str(output_file)
        ]
        
        try:
            print("🎵 Downloading audio only...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Audio download completed: {output_file}")
                return True
            else:
                print(f"❌ Audio download failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Audio download error: {e}")
            return False
    
    def download_with_stream_selection(self, mpd_url, selected_stream, output_name):
        """Download with specific stream selection"""
        ffmpeg_path = self.base_downloader.ffmpeg_path
        if not ffmpeg_path.exists():
            print("❌ FFmpeg not found")
            return False
        
        output_file = self.base_downloader.downloads_dir / f"{output_name}.mp4"
        
        cmd = [
            str(ffmpeg_path),
            "-i", mpd_url,
            "-c", "copy",
            "-f", "mp4",
            str(output_file)
        ]
        
        try:
            print(f"📥 Downloading selected quality...")
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
    
    def download_custom_ffmpeg(self, mpd_url, stream_info):
        """Custom FFmpeg download with user-specified parameters"""
        print("\n🔧 Custom FFmpeg Download")
        print("Enter custom FFmpeg parameters (or press Enter for defaults):")
        
        custom_params = input("FFmpeg params: ").strip()
        output_name = input("Output filename (without extension): ").strip() or f"toffee_custom_{stream_info['title']}"
        output_name = re.sub(r'[^\w\-_\.]', '_', output_name)
        
        ffmpeg_path = self.base_downloader.ffmpeg_path
        if not ffmpeg_path.exists():
            print("❌ FFmpeg not found")
            return False
        
        output_file = self.base_downloader.downloads_dir / f"{output_name}.mp4"
        
        cmd = [str(ffmpeg_path), "-i", mpd_url]
        
        if custom_params:
            cmd.extend(custom_params.split())
        else:
            cmd.extend(["-c", "copy", "-f", "mp4"])
        
        cmd.append(str(output_file))
        
        try:
            print(f"🔧 Running custom FFmpeg command...")
            print(f"Command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Custom download completed: {output_file}")
                return True
            else:
                print(f"❌ Custom download failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Custom download error: {e}")
            return False

def main():
    """Main function for standalone Toffee downloader"""
    print("🍬 Toffee Video Downloader - Enhanced Edition")
    print("=" * 50)
    
    downloader = ToffeeDownloader()
    
    while True:
        print("\nOptions:")
        print("1. Download from MPD URL")
        print("2. Download from Toffee video URL")
        print("3. Analyze MPD streams only")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            mpd_url = input("Enter MPD URL: ").strip()
            downloader.interactive_mpd_download(mpd_url)
        
        elif choice == "2":
            video_url = input("Enter Toffee video URL: ").strip()
            auth_token = input("Enter auth token (optional): ").strip() or None
            quality = input("Enter quality preference [best]: ").strip() or "best"
            downloader.base_downloader.download_toffee(video_url, auth_token, quality)
        
        elif choice == "3":
            mpd_url = input("Enter MPD URL: ").strip()
            stream_info = downloader.analyze_mpd_streams(mpd_url)
            if stream_info:
                downloader.display_stream_info(stream_info)
        
        elif choice == "4":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()