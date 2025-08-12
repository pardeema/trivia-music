#!/usr/bin/env python3
"""
Universal build script for Music Rounds Creator
Creates standalone executables for both macOS and Windows
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_requirements():
    """Check if we have the required tools"""
    print("🔍 Checking build requirements...")
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ main.py not found. Please run this script from the project directory")
        return False
    
    print("✅ Project files found")
    return True

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

def build_for_platform():
    """Build for the current platform"""
    current_platform = platform.system().lower()
    
    if current_platform == "darwin":
        print("🍎 Building for macOS...")
        return subprocess.run([sys.executable, "build_macos.py"], check=True)
    elif current_platform == "windows":
        print("🪟 Building for Windows...")
        return subprocess.run([sys.executable, "build_windows.py"], check=True)
    else:
        print(f"❌ Unsupported platform: {current_platform}")
        return False

def main():
    """Main build process"""
    print("🚀 Music Rounds Creator - Universal Build Script")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        return False
    
    # Install PyInstaller
    if not install_pyinstaller():
        return False
    
    # Build for current platform
    try:
        build_for_platform()
        print("\n🎉 Build completed successfully!")
        print("\n📦 Distribution packages created:")
        
        # List created files
        dist_files = list(Path(".").glob("MusicRoundsCreator_*.zip"))
        if dist_files:
            for file in dist_files:
                print(f"   - {file.name}")
        else:
            print("   - Check the 'dist' directory for the executable")
        
        print("\n📋 Next steps:")
        print("   1. Test the executable on a clean system")
        print("   2. Share the ZIP file with your users")
        print("   3. Update the README with download links")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
