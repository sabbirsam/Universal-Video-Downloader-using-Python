#!/usr/bin/env python3
"""
Toffee DRM Downloader - Comprehensive Edition
Advanced DRM-protected content downloader for Toffee platform
Integrated with Universal Video Downloader system
"""

import re
import requests
import json
import base64
import os
import subprocess
from pathlib import Path
from datetime import datetime

# Try to import DRM modules
try:
    from pywdevine import PSSH, Device, Cdm
    DRM_AVAILABLE = True
except ImportError:
    DRM_AVAILABLE = False
    print("⚠️  DRM support not available. Install pywdevine for DRM content.")

class ToffeeDRMDownloader:
    """Advanced Toffee DRM content downloader"""
    
    def __init__(self, config_path="config.json"):
        self.load_config(config_path)
        self.setup_directories()
        self.setup_headers()
        
        # Initialize DRM components
        if DRM_AVAILABLE:
            self.init_drm_handler()
        else:
            self.drm_handler = None
            print("❌ DRM functionality disabled. Install pywdevine to enable.")
    
    def load_config(self, config_path):
        """Load configuration from file"""
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Config file not found: {config_path}. Using defaults.")
            self.config = self.get_default_config()
    
    def get_default_config(self):
        """Return default configuration"""
        return {
            "toffee": {
                "api_base_url": "https://api.toffee.com/v1",
                "license_url": "https://license.toffee.com/v1/license",
                "auth_token": "",
                "device_path": "device.json"
            },
            "settings": {
                "download_directory": "downloads",
                "temp_directory": "temp",
                "tools_directory": "tools"
            }
        }
    
    def setup_directories(self):
        """Setup required directories"""
        self.downloads_dir = Path(self.config["settings"]["download_directory"])
        self.temp_dir = Path(self.config["settings"]["temp_directory"])
        self.tools_dir = Path(self.config["settings"]["tools_directory"])
        
        for directory in [self.downloads_dir, self.temp_dir, self.tools_dir]:
            directory.mkdir(exist_ok=True)
        
        # Tool paths
        self.ffmpeg_path = self.tools_dir / "ffmpeg.exe"
        self.mp4decrypt_path = self.tools_dir / "mp4decrypt.exe"
    
    def setup_headers(self):
        """Setup HTTP headers for API requests"""
        self.api_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "accept": "*/*",
            "content-type": "application/json"
        }
        
        # Add auth token if available
        if self.config["toffee"]["auth_token"]:
            self.api_headers["authorization"] = f"Bearer {self.config['toffee']['auth_token']}"
        
        self.license_headers = self.api_headers.copy()
    
    def init_drm_handler(self):
        """Initialize DRM handler"""
        try:
            device_path = self.config["toffee"]["device_path"]
            if not os.path.exists(device_path):
                print(f"⚠️  Device file not found: {device_path}")
                self.create_sample_device(device_path)
            
            self.device_path = device_path
            print("✅ DRM handler initialized")
        except Exception as e:
            print(f"❌ DRM handler initialization failed: {e}")
            self.drm_handler = None
    
    def create_sample_device(self, device_path):
        """Create sample device configuration"""
        sample_device = {
            "device_id": "sample_device_toffee_001",
            "device_private_key": "REPLACE_WITH_ACTUAL_PRIVATE_KEY",
            "device_client_id_blob": "REPLACE_WITH_ACTUAL_CLIENT_ID_BLOB",
            "device_vmp_blob": "REPLACE_WITH_ACTUAL_VMP_BLOB"
        }
        
        with open(device_path, 'w') as f:
            json.dump(sample_device, f, indent=2)
        
        print(f"📄 Sample device configuration created: {device_path}")
        print("⚠️  IMPORTANT: Replace sample values with actual Widevine device credentials!")
    
    def extract_video_id(self, video_url):
        """Extract video ID from various Toffee URL formats"""
        patterns = [
            r'/live/(\d+)',
            r'/video/(\d+)',
            r'/watch/(\d+)',
            r'/content/(\d+)',
            r'toffee\.com/.*?(\d+)',
            r'id=(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, video_url)
            if match:
                return match.group(1)
        
        print("❌ Could not extract video ID from URL")
        return None
    
    def get_video_info(self, video_id):
        """Get comprehensive video information from Toffee API"""
        endpoints = [
            f"{self.config['toffee']['api_base_url']}/videos/{video_id}/details",
            f"{self.config['toffee']['api_base_url']}/content/{video_id}",
            f"{self.config['toffee']['api_base_url']}/live/{video_id}",
            f"{self.config['toffee']['api_base_url']}/vod/{video_id}"
        ]
        
        for endpoint in endpoints:
            try:
                print(f"🔍 Trying endpoint: {endpoint}")
                response = requests.get(endpoint, headers=self.api_headers)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Successfully retrieved data from: {endpoint}")
                    return self.parse_video_data(data, video_id)
                else:
                    print(f"⚠️  Endpoint returned {response.status_code}: {endpoint}")
                    
            except Exception as e:
                print(f"❌ Error with endpoint {endpoint}: {e}")
                continue
        
        print("❌ Could not retrieve video information from any endpoint")
        return None
    
    def parse_video_data(self, data, video_id):
        """Parse video data from API response"""
        video_data = data.get('data', {})
        
        # Extract streams
        streams = video_data.get('streams', [])
        
        # Determine if DRM protected
        is_drm_protected = False
        dash_stream = None
        
        for stream in streams:
            stream_url = stream.get('url', '')
            if stream.get('format', '').upper() == 'DASH' or '.mpd' in stream_url:
                dash_stream = stream
                # Check for DRM indicators
                if any(indicator in stream_url.lower() for indicator in ['drm', 'widevine', 'cenc']):
                    is_drm_protected = True
        
        return {
            'id': video_id,
            'title': video_data.get('title', f'Toffee_Video_{video_id}'),
            'description': video_data.get('description', ''),
            'duration': video_data.get('duration', 0),
            'type': video_data.get('type', 'video'),
            'streams': streams,
            'dash_stream': dash_stream,
            'is_drm_protected': is_drm_protected,
            'raw_data': data
        }
    
    def get_pssh_from_mpd(self, mpd_url):
        """Extract PSSH from MPD manifest with enhanced detection"""
        print(f"🔍 Extracting PSSH from MPD: {mpd_url}")
        
        try:
            response = requests.get(mpd_url, headers=self.api_headers)
            response.raise_for_status()
            mpd_content = response.text
            
            # Multiple PSSH extraction patterns
            pssh_patterns = [
                r'<cenc:pssh[^>]*>(.*?)</cenc:pssh>',
                r'<pssh[^>]*>(.*?)</pssh>',
                r'"pssh":\s*"([^"]+)"',
                r'<ContentProtection[^>]*schemeIdUri="urn:uuid:edef8ba9-79d6-4ace-a3c8-27dcd51d21ed"[^>]*>.*?<cenc:pssh[^>]*>(.*?)</cenc:pssh>',
                r'<ms:pro[^>]*>(.*?)</ms:pro>',  # Microsoft PlayReady
            ]
            
            for i, pattern in enumerate(pssh_patterns, 1):
                matches = re.findall(pattern, mpd_content, re.IGNORECASE | re.DOTALL)
                if matches:
                    pssh_b64 = matches[0].strip()
                    print(f"🔑 Found PSSH (pattern {i}): {pssh_b64[:50]}...")
                    
                    # Validate PSSH
                    if self.validate_pssh(pssh_b64):
                        return pssh_b64
                    else:
                        print(f"⚠️  Invalid PSSH found with pattern {i}, trying next...")
                        continue
            
            print("❌ No valid PSSH found in MPD")
            return None
            
        except Exception as e:
            print(f"❌ Error extracting PSSH: {e}")
            return None
    
    def validate_pssh(self, pssh_b64):
        """Validate PSSH format"""
        try:
            pssh_data = base64.b64decode(pssh_b64)
            # Basic validation - PSSH should start with specific bytes
            if len(pssh_data) > 12 and pssh_data[4:8] == b'pssh':
                return True
            return False
        except Exception:
            return False
    
    def extract_decryption_keys(self, pssh_b64, video_info):
        """Extract decryption keys using Widevine CDM"""
        if not DRM_AVAILABLE:
            print("❌ DRM support not available")
            return None
        
        print("🔐 Extracting decryption keys...")
        
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
                "request": base64.b64encode(challenge).decode(),
                "content_id": video_info['id'],
                "drm_token": self.config["toffee"]["auth_token"]
            }
            
            # Send license request
            license_url = self.config["toffee"]["license_url"]
            print(f"📡 Sending license request to: {license_url}")
            
            response = requests.post(license_url, headers=self.license_headers, json=payload)
            response.raise_for_status()
            
            # Process license response
            license_response = response.json()
            license_data = license_response.get("data", {}).get("payload")
            
            if not license_data:
                # Try direct response
                license_data = response.content
            else:
                license_data = base64.b64decode(license_data)
            
            # Extract keys
            keys = cdm.parse_license(license_data)
            
            print(f"🔓 Successfully extracted {len(keys)} decryption keys:")
            for i, key in enumerate(keys, 1):
                key_type = key.get('type', 'Unknown')
                kid = key.get('kid', 'Unknown')
                k = key.get('k', 'Unknown')
                print(f"  {i}. Type: {key_type}, KID: {kid[:16]}..., Key: {k[:16]}...")
            
            return keys
            
        except Exception as e:
            print(f"❌ Error extracting decryption keys: {e}")
            return None
    
    def download_encrypted_content(self, mpd_url, output_file):
        """Download encrypted DASH content"""
        if not self.ffmpeg_path.exists():
            print("❌ FFmpeg not found. Please run setup first.")
            return False
        
        print("📥 Downloading encrypted content...")
        
        cmd = [
            str(self.ffmpeg_path),
            "-i", mpd_url,
            "-c", "copy",
            "-f", "mp4",
            str(output_file)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Encrypted content downloaded: {output_file}")
                return True
            else:
                print(f"❌ Download failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Download error: {e}")
            return False
    
    def decrypt_content(self, encrypted_file, keys, output_file):
        """Decrypt content using mp4decrypt"""
        if not self.mp4decrypt_path.exists():
            print("❌ mp4decrypt not found. Please run setup first.")
            return False
        
        print("🔓 Decrypting content...")
        
        # Build mp4decrypt command
        cmd = [str(self.mp4decrypt_path)]
        
        # Add decryption keys
        for key in keys:
            if key.get('type') == 'CONTENT':
                kid = key.get('kid', '').replace('-', '')
                k = key.get('k', '').replace('-', '')
                cmd.extend(['--key', f"{kid}:{k}"])
        
        cmd.extend([str(encrypted_file), str(output_file)])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Content decrypted successfully: {output_file}")
                return True
            else:
                print(f"❌ Decryption failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Decryption error: {e}")
            return False
    
    def download_drm_content(self, video_url, auth_token=None):
        """Complete DRM content download workflow"""
        print(f"🔐 Starting DRM content download: {video_url}")
        
        # Set auth token if provided
        if auth_token:
            self.api_headers["authorization"] = f"Bearer {auth_token}"
            self.license_headers["authorization"] = f"Bearer {auth_token}"
            self.config["toffee"]["auth_token"] = auth_token
        
        # Extract video ID
        video_id = self.extract_video_id(video_url)
        if not video_id:
            return False
        
        # Get video information
        video_info = self.get_video_info(video_id)
        if not video_info:
            return False
        
        print(f"📹 Title: {video_info['title']}")
        print(f"🎬 Type: {video_info['type']}")
        print(f"🔐 DRM Protected: {video_info['is_drm_protected']}")
        
        if not video_info['is_drm_protected']:
            print("ℹ️  Content is not DRM protected. Use regular download method.")
            return False
        
        if not video_info['dash_stream']:
            print("❌ No DASH stream found for DRM content")
            return False
        
        mpd_url = video_info['dash_stream']['url']
        print(f"📡 MPD URL: {mpd_url}")
        
        # Extract PSSH
        pssh = self.get_pssh_from_mpd(mpd_url)
        if not pssh:
            return False
        
        # Extract decryption keys
        keys = self.extract_decryption_keys(pssh, video_info)
        if not keys:
            return False
        
        # Generate output filenames
        safe_title = re.sub(r'[^\w\-_\.]', '_', video_info['title'])
        encrypted_file = self.temp_dir / f"{safe_title}_encrypted.mp4"
        decrypted_file = self.downloads_dir / f"{safe_title}_decrypted.mp4"
        
        # Download encrypted content
        if not self.download_encrypted_content(mpd_url, encrypted_file):
            return False
        
        # Decrypt content
        if not self.decrypt_content(encrypted_file, keys, decrypted_file):
            return False
        
        # Clean up encrypted file
        try:
            encrypted_file.unlink()
            print("🧹 Cleaned up temporary encrypted file")
        except Exception:
            pass
        
        print(f"🎉 DRM content download completed successfully!")
        print(f"📁 Output file: {decrypted_file}")
        return True
    
    def interactive_drm_download(self):
        """Interactive DRM download interface"""
        print("🔐 Toffee DRM Content Downloader")
        print("=" * 50)
        
        if not DRM_AVAILABLE:
            print("❌ DRM support not available. Install pywdevine first.")
            return
        
        while True:
            print("\nOptions:")
            print("1. Download DRM-protected video")
            print("2. Extract PSSH from MPD URL")
            print("3. Test license server")
            print("4. Setup device credentials")
            print("5. Configure auth token")
            print("6. Exit")
            
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == "1":
                video_url = input("Enter Toffee video URL: ").strip()
                auth_token = input("Enter auth token (optional): ").strip() or None
                self.download_drm_content(video_url, auth_token)
            
            elif choice == "2":
                mpd_url = input("Enter MPD URL: ").strip()
                pssh = self.get_pssh_from_mpd(mpd_url)
                if pssh:
                    print(f"✅ PSSH extracted successfully: {pssh}")
            
            elif choice == "3":
                print("🧪 License server test not implemented yet")
            
            elif choice == "4":
                device_path = input(f"Device file path [{self.device_path}]: ").strip() or self.device_path
                self.create_sample_device(device_path)
            
            elif choice == "5":
                new_token = input("Enter new auth token: ").strip()
                if new_token:
                    self.config["toffee"]["auth_token"] = new_token
                    self.setup_headers()
                    print("✅ Auth token updated")
            
            elif choice == "6":
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice")

def main():
    """Main function for standalone DRM downloader"""
    downloader = ToffeeDRMDownloader()
    downloader.interactive_drm_download()

if __name__ == "__main__":
    main()