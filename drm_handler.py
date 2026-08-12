#!/usr/bin/env python3
"""
Advanced DRM Handler for protected content
Handles Widevine DRM decryption
"""

import os
import re
import json
import base64
import requests
import subprocess
from pathlib import Path

try:
    from pywdevine import PSSH, Device, Cdm
    DRM_AVAILABLE = True
except ImportError:
    DRM_AVAILABLE = False

class DRMHandler:
    def __init__(self, device_path=None):
        if not DRM_AVAILABLE:
            raise ImportError("pywdevine not available. Install with: pip install pywdevine")
        
        self.device_path = device_path or "device.json"
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
    
    def extract_pssh_from_mpd(self, mpd_url):
        """Extract PSSH from MPD manifest"""
        try:
            response = requests.get(mpd_url)
            response.raise_for_status()
            
            # Look for PSSH in different formats
            pssh_patterns = [
                r'<cenc:pssh[^>]*>(.*?)</cenc:pssh>',
                r'<pssh[^>]*>(.*?)</pssh>',
                r'"pssh":\s*"([^"]+)"'
            ]
            
            for pattern in pssh_patterns:
                match = re.search(pattern, response.text, re.IGNORECASE)
                if match:
                    pssh_b64 = match.group(1).strip()
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
            self.create_sample_device()
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
            
            # Prepare license request
            license_request = {
                "request": base64.b64encode(challenge).decode(),
                "headers": headers or {}
            }
            
            # Send license request
            response = requests.post(
                license_url, 
                data=license_request["request"],
                headers=headers or {}
            )
            response.raise_for_status()
            
            # Parse license response
            license_data = base64.b64decode(response.content)
            keys = cdm.parse_license(license_data)
            
            print(f"🔓 Extracted {len(keys)} decryption keys")
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
            
            print(f"🔧 Decrypting: {' '.join(cmd[:3])}... [keys hidden]")
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
    
    def process_drm_content(self, mpd_url, license_url, headers=None, output_name="decrypted_content"):
        """Complete DRM processing workflow"""
        print("🔐 Starting DRM content processing...")
        
        # Step 1: Extract PSSH
        pssh = self.extract_pssh_from_mpd(mpd_url)
        if not pssh:
            return False
        
        # Step 2: Get decryption keys
        keys = self.get_decryption_keys(pssh, license_url, headers)
        if not keys:
            return False
        
        # Step 3: Download encrypted content (placeholder)
        print("📥 Download encrypted content first using your preferred method")
        print("📝 Then use decrypt_content() method with the downloaded file")
        
        return True

def main():
    """Interactive DRM handler"""
    if not DRM_AVAILABLE:
        print("❌ DRM support not available. Install pywdevine first.")
        return
    
    handler = DRMHandler()
    
    print("🔐 DRM Content Handler")
    print("=" * 30)
    
    while True:
        print("\nOptions:")
        print("1. Create sample device configuration")
        print("2. Extract PSSH from MPD URL")
        print("3. Process DRM content (full workflow)")
        print("4. Decrypt downloaded file")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            handler.create_sample_device()
            
        elif choice == "2":
            mpd_url = input("Enter MPD URL: ").strip()
            handler.extract_pssh_from_mpd(mpd_url)
            
        elif choice == "3":
            mpd_url = input("Enter MPD URL: ").strip()
            license_url = input("Enter license URL: ").strip()
            auth_token = input("Enter auth token (optional): ").strip()
            
            headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else None
            handler.process_drm_content(mpd_url, license_url, headers)
            
        elif choice == "4":
            encrypted_file = input("Enter encrypted file path: ").strip()
            output_file = input("Enter output file path: ").strip()
            print("⚠️  You need to provide decryption keys manually")
            
        elif choice == "5":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()