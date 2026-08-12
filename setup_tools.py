#!/usr/bin/env python3
"""
Video Downloader Setup Script
Downloads and sets up all required tools for video downloading
"""

import os
import requests
import zipfile
import subprocess
import sys
from pathlib import Path

def create_directories():
    """Create necessary directories"""
    directories = ['tools', 'downloads', 'temp']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def download_file(url, filename):
    """Download a file with progress indication"""
    print(f"Downloading {filename}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r  Progress: {percent:.1f}%", end='', flush=True)
        
        print(f"\n✓ Downloaded: {filename}")
        return True
    except Exception as e:
        print(f"\n✗ Failed to download {filename}: {e}")
        return False

def download_ffmpeg():
    """Download FFmpeg for Windows"""
    print("\n=== Downloading FFmpeg ===")
    
    # FFmpeg Windows build URL (latest release)
    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    
    if download_file(ffmpeg_url, "temp/ffmpeg.zip"):
        print("Extracting FFmpeg...")
        with zipfile.ZipFile("temp/ffmpeg.zip", 'r') as zip_ref:
            zip_ref.extractall("temp/")
        
        # Find and move ffmpeg.exe
        for root, dirs, files in os.walk("temp/"):
            if "ffmpeg.exe" in files:
                src = os.path.join(root, "ffmpeg.exe")
                dst = "tools/ffmpeg.exe"
                os.rename(src, dst)
                print(f"✓ FFmpeg installed to: {dst}")
                break

def download_mp4decrypt():
    """Download mp4decrypt (Bento4 tools)"""
    print("\n=== Downloading mp4decrypt ===")
    
    # Bento4 Windows build URL
    bento4_url = "https://github.com/axiomatic-systems/Bento4/releases/download/v1.6.0-641/Bento4-SDK-1-6-0-641.x86_64-microsoft-win32.zip"
    
    if download_file(bento4_url, "temp/bento4.zip"):
        print("Extracting Bento4...")
        with zipfile.ZipFile("temp/bento4.zip", 'r') as zip_ref:
            zip_ref.extractall("temp/")
        
        # Find and move mp4decrypt.exe
        for root, dirs, files in os.walk("temp/"):
            if "mp4decrypt.exe" in files:
                src = os.path.join(root, "mp4decrypt.exe")
                dst = "tools/mp4decrypt.exe"
                os.rename(src, dst)
                print(f"✓ mp4decrypt installed to: {dst}")
                break

def download_n_m3u8dl_re():
    """Download N_m3u8DL-RE"""
    print("\n=== Downloading N_m3u8DL-RE ===")
    
    # N_m3u8DL-RE Windows build URL
    n_m3u8dl_url = "https://github.com/nilaoda/N_m3u8DL-RE/releases/download/v0.2.0-beta/N_m3u8DL-RE_Beta_win-x64_20231009.zip"
    
    if download_file(n_m3u8dl_url, "temp/n_m3u8dl.zip"):
        print("Extracting N_m3u8DL-RE...")
        with zipfile.ZipFile("temp/n_m3u8dl.zip", 'r') as zip_ref:
            zip_ref.extractall("temp/")
        
        # Find and move N_m3u8DL-RE.exe
        for root, dirs, files in os.walk("temp/"):
            if "N_m3u8DL-RE.exe" in files:
                src = os.path.join(root, "N_m3u8DL-RE.exe")
                dst = "tools/N_m3u8DL-RE.exe"
                os.rename(src, dst)
                print(f"✓ N_m3u8DL-RE installed to: {dst}")
                break

def install_python_dependencies():
    """Install required Python packages"""
    print("\n=== Installing Python Dependencies ===")
    
    packages = [
        "requests",
        "pywdevine",
        "yt-dlp",
        "beautifulsoup4",
        "lxml",
        "cryptography",
        "pycryptodome"
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ Installed: {package}")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install: {package}")

def cleanup():
    """Clean up temporary files"""
    print("\n=== Cleaning up ===")
    import shutil
    if os.path.exists("temp"):
        shutil.rmtree("temp")
        print("✓ Cleaned up temporary files")

def verify_installation():
    """Verify all tools are properly installed"""
    print("\n=== Verifying Installation ===")
    
    tools = {
        "tools/ffmpeg.exe": "FFmpeg",
        "tools/mp4decrypt.exe": "mp4decrypt", 
        "tools/N_m3u8DL-RE.exe": "N_m3u8DL-RE"
    }
    
    all_good = True
    for tool_path, tool_name in tools.items():
        if os.path.exists(tool_path):
            print(f"✓ {tool_name} is installed")
        else:
            print(f"✗ {tool_name} is missing")
            all_good = False
    
    if all_good:
        print("\n🎉 All tools installed successfully!")
        print("\nNext steps:")
        print("1. Run 'python video_downloader.py' to start downloading videos")
        print("2. For DRM content, make sure you have valid device credentials")
    else:
        print("\n⚠️  Some tools are missing. Please check the installation.")

if __name__ == "__main__":
    print("🚀 Video Downloader Setup")
    print("=" * 50)
    
    create_directories()
    download_ffmpeg()
    download_mp4decrypt()
    download_n_m3u8dl_re()
    install_python_dependencies()
    cleanup()
    verify_installation()
    
    print("\n✅ Setup completed!")