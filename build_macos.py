#!/usr/bin/env python3
"""
Build script for macOS
Creates a standalone .app bundle with all dependencies included
"""

import os
import sys
import subprocess
import shutil
import urllib.request
import zipfile
from pathlib import Path

def download_ffmpeg_macos():
    """Download FFmpeg static build for macOS"""
    print("📦 Downloading FFmpeg for macOS...")
    
    # FFmpeg static build URL for macOS
    ffmpeg_url = "https://evermeet.cx/ffmpeg/getrelease/zip"
    ffmpeg_zip = "ffmpeg_macos.zip"
    
    try:
        # Download FFmpeg
        print("Downloading FFmpeg static build...")
        urllib.request.urlretrieve(ffmpeg_url, ffmpeg_zip)
        
        # Extract FFmpeg
        print("Extracting FFmpeg...")
        with zipfile.ZipFile(ffmpeg_zip, 'r') as zip_ref:
            zip_ref.extractall("ffmpeg_temp")
        
        # Find ffmpeg binary
        ffmpeg_bin = None
        for root, dirs, files in os.walk("ffmpeg_temp"):
            if "ffmpeg" in files and not files[files.index("ffmpeg")].endswith('.dylib'):
                ffmpeg_bin = os.path.join(root, "ffmpeg")
                break
        
        if ffmpeg_bin:
            # Copy to current directory
            shutil.copy2(ffmpeg_bin, "ffmpeg")
            # Make executable
            os.chmod("ffmpeg", 0o755)
            print("✅ FFmpeg downloaded and extracted successfully")
            
            # Clean up
            shutil.rmtree("ffmpeg_temp", ignore_errors=True)
            os.remove(ffmpeg_zip)
            return True
        else:
            print("❌ Could not find ffmpeg binary in downloaded archive")
            return False
            
    except Exception as e:
        print(f"❌ Failed to download FFmpeg: {e}")
        return False

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("✅ PyInstaller is already installed")
        return True
    except ImportError:
        print("📦 Installing PyInstaller...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
            print("✅ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install PyInstaller: {e}")
            return False

def build_app():
    """Build the macOS app bundle"""
    print("🔨 Building macOS app bundle...")
    
    # Ensure we have FFmpeg
    if not Path("ffmpeg").exists():
        if not download_ffmpeg_macos():
            return False
    
    # PyInstaller command for macOS
    cmd = [
        'pyinstaller',
        '--onefile',  # Use onefile for simplicity
        '--name=MusicRoundsCreator',
        '--add-binary=ffmpeg:ffmpeg',  # Include FFmpeg binary
        '--hidden-import=PyQt6',
        '--hidden-import=yt_dlp',
        '--hidden-import=pydub',
        '--hidden-import=psutil',
        '--hidden-import=urllib3',
        '--hidden-import=requests',
        '--collect-all=yt_dlp',
        '--collect-all=pydub',
        'main.py'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ App bundle created successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def create_installer():
    """Create a DMG-like installer package"""
    print("📦 Creating installer package...")
    
    try:
        import zipfile
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_name = f"MusicRoundsCreator_macOS_{timestamp}.zip"
        
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add the executable
            exe_path = Path('dist/MusicRoundsCreator')
            if exe_path.exists():
                zipf.write(exe_path, exe_path.name)
            
            # Add README
            readme_content = """Music Rounds Creator - macOS

Installation:
1. Extract this ZIP file to a folder of your choice
2. Double-click MusicRoundsCreator to run the application
3. If macOS blocks the app:
   - **Option 1**: Right-click and select "Open" from the context menu
   - **Option 2**: Go to System Preferences → Privacy & Security → Security section → Click "Open Anyway" next to MusicRoundsCreator

Requirements:
- macOS 10.14 (Mojave) or later
- No additional software required (all dependencies included)

Usage:
1. Enter YouTube URLs and start times
2. Click "Create Music Round"
3. Find your ZIP file on the Desktop

For support, contact the developer.
"""
            
            zipf.writestr("README.txt", readme_content)
        
        print(f"✅ Created installer: {zip_name}")
        return True
    except Exception as e:
        print(f"❌ Failed to create installer: {e}")
        return False

def main():
    """Main build process"""
    print("🚀 Starting macOS build process...")
    
    # Check if we're on macOS
    if sys.platform != "darwin":
        print("❌ This script is for macOS only")
        return False
    
    # Install PyInstaller
    if not install_pyinstaller():
        return False
    
    # Build the app
    if not build_app():
        return False
    
    # Create installer
    create_installer()
    
    print("🎉 Build process completed!")
    print("📁 Your app is in the 'dist' directory")
    print("📦 Installer package created in current directory")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
