#!/usr/bin/env python3
"""
Test script for the local desktop application
Tests the core functionality without the GUI
"""

import sys
import os
import tempfile
import zipfile
from pathlib import Path
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import DownloadWorker

def test_download_worker():
    """Test the DownloadWorker class directly"""
    print("🧪 Testing DownloadWorker functionality...")
    
    # Test data
    test_links = [
        {
            'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',  # Rick Astley
            'start_time': 30,  # Start at 30 seconds
            'title': 'Rick Astley - Never Gonna Give You Up'
        },
        {
            'url': 'https://www.youtube.com/watch?v=9bZkp7q19f0',  # PSY
            'start_time': 45,  # Start at 45 seconds
            'title': 'PSY - GANGNAM STYLE'
        }
    ]
    
    # Create worker
    worker = DownloadWorker(test_links)
    
    # Test download functionality
    print("Testing download functionality...")
    
    # Test single download
    temp_dir = Path(tempfile.mkdtemp(prefix="test_"))
    try:
        # Test download
        audio_file = worker.download_youtube_audio(
            test_links[0]['url'], 
            temp_dir, 
            0
        )
        
        if audio_file and os.path.exists(audio_file):
            print(f"✅ Download successful: {audio_file}")
            
            # Test audio clipping
            output_dir = temp_dir / "output"
            output_dir.mkdir(exist_ok=True)
            
            clip_file = worker.create_audio_clip(
                audio_file,
                test_links[0]['start_time'],
                output_dir,
                0
            )
            
            if clip_file and os.path.exists(clip_file):
                print(f"✅ Audio clipping successful: {clip_file}")
                
                # Test ZIP creation
                processed_files = [{
                    'file': clip_file,
                    'title': test_links[0]['title'],
                    'index': 0
                }]
                
                zip_path = worker.create_zip_file(processed_files)
                if os.path.exists(zip_path):
                    print(f"✅ ZIP creation successful: {zip_path}")
                    
                    # Verify ZIP contents
                    with zipfile.ZipFile(zip_path, 'r') as zipf:
                        files = zipf.namelist()
                        print(f"✅ ZIP contains {len(files)} files: {files}")
                else:
                    print("❌ ZIP creation failed")
            else:
                print("❌ Audio clipping failed")
        else:
            print("❌ Download failed")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        try:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass

def test_dependencies():
    """Test that all required dependencies are available"""
    print("🔍 Testing dependencies...")
    
    dependencies = [
        ('PyQt6', 'PyQt6'),
        ('yt-dlp', 'yt_dlp'),
        ('pydub', 'pydub'),
        ('psutil', 'psutil'),
    ]
    
    missing = []
    for name, module in dependencies:
        try:
            __import__(module)
            print(f"✅ {name} is available")
        except ImportError:
            print(f"❌ {name} is missing")
            missing.append(name)
    
    # Test FFmpeg
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg is available")
        else:
            print("❌ FFmpeg is not working properly")
            missing.append('FFmpeg')
    except FileNotFoundError:
        print("❌ FFmpeg is not installed")
        missing.append('FFmpeg')
    
    if missing:
        print(f"\n❌ Missing dependencies: {', '.join(missing)}")
        print("Please install missing dependencies before running the app.")
        return False
    else:
        print("\n✅ All dependencies are available!")
        return True

def main():
    """Main test function"""
    print("🚀 Starting local app tests...")
    
    # Test dependencies first
    if not test_dependencies():
        return False
    
    # Test core functionality
    test_download_worker()
    
    print("\n🎉 Tests completed!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
