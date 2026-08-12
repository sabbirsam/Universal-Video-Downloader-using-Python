#!/usr/bin/env python3
"""
Universal Video Downloader - Main Launcher
Comprehensive video downloading solution with full platform support
"""

import os
import sys
import json
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = {
        'requests': 'requests',
        'yt_dlp': 'yt-dlp', 
        'pywdevine': 'pywdevine (optional, for DRM content)'
    }
    
    missing_packages = []
    
    for package, display_name in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            if package == 'pywdevine':
                print(f"⚠️  {display_name} not installed - DRM features will be disabled")
            else:
                missing_packages.append(display_name)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def check_tools():
    """Check if required tools are available"""
    tools_dir = Path("tools")
    required_tools = {
        "ffmpeg.exe": "FFmpeg",
        "mp4decrypt.exe": "mp4decrypt",
        "N_m3u8DL-RE.exe": "N_m3u8DL-RE"
    }
    
    missing_tools = []
    
    for tool_file, tool_name in required_tools.items():
        tool_path = tools_dir / tool_file
        if not tool_path.exists():
            missing_tools.append(tool_name)
    
    if missing_tools:
        print("⚠️  Missing tools:")
        for tool in missing_tools:
            print(f"   - {tool}")
        print("\nRun setup to download missing tools:")
        print("   python setup_tools.py")
        return False
    
    return True

def display_banner():
    """Display application banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                Universal Video Downloader                    ║
║                  Comprehensive Edition                       ║
╠══════════════════════════════════════════════════════════════╣
║  📺 YouTube (Public/Private/Playlists)                      ║
║  🍬 Toffee (Regular/Premium/DRM)                            ║
║  📡 M3U8 Streams                                            ║
║  🎯 DASH/MPD Streams                                        ║
║  🔐 DRM-Protected Content                                   ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main_menu():
    """Display main menu and handle user selection"""
    while True:
        print("\n🚀 Select Downloader Mode:")
        print("1. 🎬 Universal Downloader (All platforms)")
        print("2. 📺 YouTube Downloader (Specialized)")
        print("3. 🍬 Toffee Downloader (Specialized)")
        print("4. 🔐 Toffee DRM Downloader (Advanced)")
        print("5. ⚙️  Setup & Configuration")
        print("6. 🔧 System Tools")
        print("7. 📖 Help & Documentation")
        print("8. ❌ Exit")
        
        choice = input("\nSelect option (1-8): ").strip()
        
        if choice == "1":
            launch_universal_downloader()
        elif choice == "2":
            launch_youtube_downloader()
        elif choice == "3":
            launch_toffee_downloader()
        elif choice == "4":
            launch_drm_downloader()
        elif choice == "5":
            launch_setup()
        elif choice == "6":
            launch_system_tools()
        elif choice == "7":
            show_help()
        elif choice == "8":
            print("👋 Thank you for using Universal Video Downloader!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

def launch_universal_downloader():
    """Launch the main universal downloader"""
    try:
        from video_downloader import VideoDownloader
        downloader = VideoDownloader()
        downloader.interactive_download()
    except ImportError as e:
        print(f"❌ Error importing video_downloader: {e}")
    except Exception as e:
        print(f"❌ Error launching universal downloader: {e}")

def launch_youtube_downloader():
    """Launch YouTube-specific downloader"""
    try:
        from video_downloader import VideoDownloader
        downloader = VideoDownloader()
        
        print("\n📺 YouTube Downloader Mode")
        print("=" * 30)
        
        while True:
            url = input("\nEnter YouTube URL (or 'back' to return): ").strip()
            if url.lower() == 'back':
                break
            
            quality = input("Enter quality (best/720p/1080p/audio) [best]: ").strip() or "best"
            downloader.download_youtube(url, quality, interactive=True)
            
    except ImportError as e:
        print(f"❌ Error importing video_downloader: {e}")
    except Exception as e:
        print(f"❌ Error launching YouTube downloader: {e}")

def launch_toffee_downloader():
    """Launch Toffee-specific downloader"""
    try:
        from toffee import ToffeeDownloader
        downloader = ToffeeDownloader()
        downloader.main()
    except ImportError as e:
        print(f"❌ Error importing toffee downloader: {e}")
    except Exception as e:
        print(f"❌ Error launching Toffee downloader: {e}")

def launch_drm_downloader():
    """Launch DRM-specific downloader"""
    try:
        from drmtoffee import ToffeeDRMDownloader
        downloader = ToffeeDRMDownloader()
        downloader.interactive_drm_download()
    except ImportError as e:
        print(f"❌ Error importing DRM downloader: {e}")
        print("💡 Make sure pywdevine is installed for DRM support")
    except Exception as e:
        print(f"❌ Error launching DRM downloader: {e}")

def launch_setup():
    """Launch setup and configuration"""
    print("\n⚙️  Setup & Configuration")
    print("=" * 30)
    print("1. Run initial setup (download tools)")
    print("2. Update tools")
    print("3. Configure settings")
    print("4. Check installation")
    print("5. Back to main menu")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == "1":
        os.system("python setup_tools.py")
    elif choice == "2":
        print("Running tool update...")
        os.system("python setup_tools.py")
    elif choice == "3":
        configure_settings()
    elif choice == "4":
        check_installation()
    elif choice == "5":
        return
    else:
        print("❌ Invalid choice")

def launch_system_tools():
    """Launch system tools menu"""
    print("\n🔧 System Tools")
    print("=" * 20)
    print("1. Check tool installation")
    print("2. Test network connectivity")
    print("3. Clear temporary files")
    print("4. View logs")
    print("5. Back to main menu")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == "1":
        check_tools()
        check_dependencies()
    elif choice == "2":
        test_network()
    elif choice == "3":
        clear_temp_files()
    elif choice == "4":
        view_logs()
    elif choice == "5":
        return
    else:
        print("❌ Invalid choice")

def configure_settings():
    """Configure application settings"""
    config_file = "config.json"
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ Config file not found. Creating default configuration...")
        config = create_default_config()
        save_config(config, config_file)
    
    print("\n📋 Current Configuration:")
    print(json.dumps(config, indent=2))
    
    print("\nConfiguration options:")
    print("1. Change download directory")
    print("2. Configure Toffee auth token")
    print("3. Configure YouTube settings")
    print("4. Reset to defaults")
    print("5. Back")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == "1":
        new_dir = input(f"Enter new download directory [{config['settings']['download_directory']}]: ").strip()
        if new_dir:
            config['settings']['download_directory'] = new_dir
            save_config(config, config_file)
            print("✅ Download directory updated")
    
    elif choice == "2":
        new_token = input("Enter Toffee auth token: ").strip()
        if new_token:
            config['toffee']['auth_token'] = new_token
            save_config(config, config_file)
            print("✅ Toffee auth token updated")
    
    elif choice == "3":
        print("YouTube settings configuration...")
        subtitles = input("Extract subtitles? (y/n) [y]: ").strip().lower()
        config['youtube']['extract_subtitles'] = subtitles != 'n'
        
        languages = input("Subtitle languages (comma-separated) [en,bn]: ").strip()
        if languages:
            config['youtube']['subtitle_languages'] = [lang.strip() for lang in languages.split(',')]
        
        save_config(config, config_file)
        print("✅ YouTube settings updated")
    
    elif choice == "4":
        config = create_default_config()
        save_config(config, config_file)
        print("✅ Configuration reset to defaults")

def create_default_config():
    """Create default configuration"""
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

def save_config(config, config_file):
    """Save configuration to file"""
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"❌ Failed to save config: {e}")
        return False

def check_installation():
    """Check complete installation status"""
    print("\n🔍 Checking Installation Status...")
    
    print("\n📦 Python Packages:")
    deps_ok = check_dependencies()
    
    print("\n🔧 Tools:")
    tools_ok = check_tools()
    
    print("\n📁 Directories:")
    dirs = ["downloads", "temp", "tools"]
    for directory in dirs:
        if Path(directory).exists():
            print(f"✅ {directory}/")
        else:
            print(f"❌ {directory}/ (missing)")
    
    print("\n📄 Configuration:")
    if Path("config.json").exists():
        print("✅ config.json")
    else:
        print("⚠️  config.json (will be created)")
    
    if deps_ok and tools_ok:
        print("\n🎉 Installation is complete and ready to use!")
    else:
        print("\n⚠️  Installation incomplete. Run setup to fix issues.")

def test_network():
    """Test network connectivity"""
    import requests
    
    test_urls = [
        ("YouTube", "https://www.youtube.com"),
        ("Toffee", "https://api.toffee.com"),
        ("Google", "https://www.google.com")
    ]
    
    print("\n🌐 Testing Network Connectivity:")
    
    for name, url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: OK")
            else:
                print(f"⚠️  {name}: {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Failed ({e})")

def clear_temp_files():
    """Clear temporary files"""
    import shutil
    
    temp_dirs = ["temp", "__pycache__"]
    
    for temp_dir in temp_dirs:
        temp_path = Path(temp_dir)
        if temp_path.exists():
            try:
                shutil.rmtree(temp_path)
                temp_path.mkdir(exist_ok=True)
                print(f"✅ Cleared {temp_dir}/")
            except Exception as e:
                print(f"❌ Failed to clear {temp_dir}/: {e}")
        else:
            print(f"ℹ️  {temp_dir}/ does not exist")

def view_logs():
    """View application logs"""
    print("\n📋 Application Logs:")
    print("Log viewing feature coming soon...")

def show_help():
    """Show help and documentation"""
    help_text = """
📖 Universal Video Downloader - Help & Documentation

🎯 QUICK START:
1. Run setup: python setup_tools.py
2. Launch: python launcher.py
3. Select your platform and start downloading!

🔧 SUPPORTED PLATFORMS:
• YouTube: All videos including private/unlisted, playlists
• Toffee: Regular and premium content, DRM-protected videos
• M3U8: Live streams and VOD content
• DASH/MPD: Adaptive streaming content

🔐 DRM CONTENT:
For DRM-protected content, you need:
1. Install pywdevine: pip install pywdevine
2. Obtain Widevine device credentials (device.json)
3. Configure auth tokens for the platform

⚙️  CONFIGURATION:
• Edit config.json for global settings
• Use the settings menu for interactive configuration
• Set auth tokens for premium content access

🆘 TROUBLESHOOTING:
• Run system check: Option 6 → Check installation
• Update tools: python setup_tools.py
• Clear temp files: Option 6 → Clear temporary files
• Check network: Option 6 → Test connectivity

📁 FILE STRUCTURE:
• downloads/ - Downloaded videos
• tools/ - FFmpeg, mp4decrypt, N_m3u8DL-RE
• temp/ - Temporary files
• config.json - Configuration
• device.json - DRM device credentials

🔗 USEFUL COMMANDS:
• Direct YouTube: python -m yt_dlp [URL]
• Check tools: python setup_tools.py
• Universal mode: python video_downloader.py
• DRM mode: python drmtoffee.py

For more help, check README.md or the source code comments.
    """
    
    print(help_text)
    input("\nPress Enter to continue...")

def main():
    """Main application entry point"""
    display_banner()
    
    # Quick system check
    print("🔍 Performing quick system check...")
    
    deps_ok = check_dependencies()
    tools_ok = check_tools()
    
    if not deps_ok:
        print("\n❌ Missing dependencies. Please install required packages first.")
        print("Run: pip install -r requirements.txt")
        return
    
    if not tools_ok:
        print("\n⚠️  Some tools are missing. Consider running setup.")
        choice = input("Continue anyway? (y/n): ").strip().lower()
        if choice != 'y':
            return
    
    print("✅ System check completed!")
    
    # Launch main menu
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Application interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check your setup and try again.")

if __name__ == "__main__":
    main()