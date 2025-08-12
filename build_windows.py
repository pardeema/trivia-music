#!/usr/bin/env python3
"""
Build script for Windows
Creates a standalone .exe with all dependencies included
"""

import os
import sys
import subprocess
import shutil
import urllib.request
import zipfile
from pathlib import Path

def download_ffmpeg_windows():
    """Download FFmpeg static build for Windows"""
    print("📦 Downloading FFmpeg for Windows...")
    
    # FFmpeg static build URL for Windows
    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    ffmpeg_zip = "ffmpeg_windows.zip"
    
    try:
        # Download FFmpeg
        print("Downloading FFmpeg static build...")
        urllib.request.urlretrieve(ffmpeg_url, ffmpeg_zip)
        
        # Extract FFmpeg
        print("Extracting FFmpeg...")
        with zipfile.ZipFile(ffmpeg_zip, 'r') as zip_ref:
            zip_ref.extractall("ffmpeg_temp")
        
        # Find ffmpeg.exe
        ffmpeg_exe = None
        for root, dirs, files in os.walk("ffmpeg_temp"):
            if "ffmpeg.exe" in files:
                ffmpeg_exe = os.path.join(root, "ffmpeg.exe")
                break
        
        if ffmpeg_exe:
            # Copy to current directory
            shutil.copy2(ffmpeg_exe, "ffmpeg.exe")
            print("✅ FFmpeg downloaded and extracted successfully")
            
            # Clean up
            shutil.rmtree("ffmpeg_temp", ignore_errors=True)
            os.remove(ffmpeg_zip)
            return True
        else:
            print("❌ Could not find ffmpeg.exe in downloaded archive")
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

def build_exe():
    """Build the Windows executable"""
    print("🔨 Building Windows executable...")
    
    # Ensure we have FFmpeg
    if not Path("ffmpeg.exe").exists():
        if not download_ffmpeg_windows():
            return False
    
    # PyInstaller command for Windows
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=MusicRoundsCreator',
        '--add-binary=ffmpeg.exe;.',  # Include FFmpeg binary
        '--hidden-import=PyQt6',
        '--hidden-import=PyQt6.QtCore',
        '--hidden-import=PyQt6.QtGui',
        '--hidden-import=PyQt6.QtWidgets',
        '--hidden-import=yt_dlp',
        '--hidden-import=pydub',
        '--hidden-import=psutil',
        '--hidden-import=urllib3',
        '--hidden-import=requests',
        '--collect-all=yt_dlp',
        '--collect-all=pydub',
        '--collect-all=PyQt6',
        '--exclude-module=tkinter',  # Exclude unnecessary modules
        '--exclude-module=matplotlib',
        '--exclude-module=numpy',
        '--exclude-module=scipy',
        'main.py'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ Executable created successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def create_installer():
    """Create a simple installer package"""
    print("📦 Creating installer package...")
    
    try:
        import zipfile
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_name = f"MusicRoundsCreator_Windows_{timestamp}.zip"
        
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add the executable
            exe_path = Path('dist/MusicRoundsCreator.exe')
            if exe_path.exists():
                zipf.write(exe_path, exe_path.name)
            
            # Add README
            readme_content = """Music Rounds Creator - Windows

Installation:
1. Extract this ZIP file to a folder of your choice
2. Double-click MusicRoundsCreator.exe to run the application
3. If Windows SmartScreen blocks the app, click "More info" then "Run anyway"

Requirements:
- Windows 10 or later
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
    print("🚀 Starting Windows build process...")
    
    # Check if we're on Windows
    if sys.platform != "win32":
        print("❌ This script is for Windows only")
        return False
    
    # Install PyInstaller
    if not install_pyinstaller():
        return False
    
    # Build the executable
    if not build_exe():
        return False
    
    # Create installer
    create_installer()
    
    print("🎉 Build process completed!")
    print("📁 Your executable is in the 'dist' directory")
    print("📦 Installer package created in current directory")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
