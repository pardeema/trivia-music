#!/usr/bin/env python3
"""
Test script for core functionality without GUI dependencies
"""

import sys
import os
import tempfile
import zipfile
import gc
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

import yt_dlp
import psutil

class CoreDownloader:
    """Core download functionality without GUI dependencies"""
    
    def __init__(self):
        self.is_running = True
        
    def download_youtube_audio(self, url: str, temp_dir: Path, index: int) -> Optional[str]:
        """Download audio from YouTube URL"""
        output_path = temp_dir / f"temp_{index}"
        
        # Multiple download strategies
        strategies = [
            # Strategy 1: Standard approach
            {
                'format': 'worstaudio[ext=m4a]/worstaudio[ext=webm]/worstaudio',
                'outtmpl': str(output_path),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '128',
                }],
                'quiet': True,
                'no_warnings': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                    'Sec-Fetch-Mode': 'navigate',
                },
                'sleep_interval': 2,
                'max_sleep_interval': 5,
                'retries': 3,
                'fragment_retries': 3,
            },
            # Strategy 2: Alternative user agent
            {
                'format': 'worstaudio/worst',
                'outtmpl': str(output_path),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '128',
                }],
                'quiet': True,
                'no_warnings': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                },
                'sleep_interval': 3,
                'max_sleep_interval': 8,
                'retries': 5,
                'fragment_retries': 5,
            }
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                print(f"Trying download strategy {i+1}...")
                with yt_dlp.YoutubeDL(strategy) as ydl:
                    info = ydl.extract_info(url, download=True)
                    
                # Find the downloaded file
                for ext in ['.mp3', '.m4a', '.webm']:
                    potential_file = str(output_path) + ext
                    if os.path.exists(potential_file):
                        return potential_file
                        
                # Check for files with different naming
                for file in temp_dir.glob(f"temp_{index}.*"):
                    if file.suffix in ['.mp3', '.m4a', '.webm']:
                        return str(file)
                        
            except Exception as e:
                print(f"Strategy {i+1} failed: {str(e)}")
                continue
                
        raise Exception("All download strategies failed")
        
    def create_audio_clip(self, input_file: str, start_time: int, output_dir: Path, index: int, duration: int = 15) -> Optional[str]:
        """Create a custom duration audio clip starting from the specified time"""
        output_file = output_dir / f"{index+1:02d}.mp3"
        
        try:
            # Try direct FFmpeg first (more memory efficient)
            import subprocess
            
            cmd = [
                'ffmpeg', '-y',  # Overwrite output file
                '-i', input_file,  # Input file
                '-ss', str(start_time),  # Start time
                '-t', str(duration),  # Duration (custom seconds)
                '-c:a', 'mp3',  # Audio codec
                '-b:a', '128k',  # Bitrate
                '-ar', '44100',  # Sample rate
                str(output_file)  # Output file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and output_file.exists():
                return str(output_file)
                
        except Exception as e:
            print(f"FFmpeg direct processing failed: {str(e)}")
            
        # Fallback to pydub
        try:
            from pydub import AudioSegment
            
            print("Using pydub fallback for audio processing...")
            audio = AudioSegment.from_file(input_file)
            
            # Convert start time from seconds to milliseconds
            start_ms = start_time * 1000
            end_ms = start_ms + (duration * 1000)  # Custom duration
            
            # Extract the clip
            clip = audio[start_ms:end_ms]
            
            # Export as MP3
            clip.export(str(output_file), format='mp3', bitrate='128k')
            
            # Clean up memory
            del audio
            del clip
            gc.collect()
            
            return str(output_file)
            
        except Exception as e:
            print(f"Pydub processing failed: {str(e)}")
            return None
            
    def create_zip_file(self, processed_files: List[Dict]) -> str:
        """Create a ZIP file containing all processed audio clips"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"music_rounds_{timestamp}.zip"
        
        # Get user's desktop
        output_dir = Path.home() / "Desktop"
        zip_path = output_dir / zip_filename
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_info in processed_files:
                file_path = file_info['file']
                title = file_info['title']
                index = file_info['index']
                
                # Create a clean filename
                clean_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                arcname = f"{index+1:02d}_{clean_title[:50]}.mp3"
                
                zipf.write(file_path, arcname)
                
        return str(zip_path)

def test_dependencies():
    """Test that all required dependencies are available"""
    print("🔍 Testing dependencies...")
    
    dependencies = [
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
        return False
    else:
        print("\n✅ All dependencies are available!")
        return True

def test_core_functionality():
    """Test the core download and processing functionality"""
    print("🧪 Testing core functionality...")
    
    # Test data
    test_links = [
        {
            'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',  # Rick Astley
            'start_time': 30,  # Start at 30 seconds
            'duration': 15,  # 15 second clip
            'title': 'Rick Astley - Never Gonna Give You Up'
        }
    ]
    
    # Create downloader
    downloader = CoreDownloader()
    
    # Test single download
    temp_dir = Path(tempfile.mkdtemp(prefix="test_"))
    try:
        print("Testing download...")
        audio_file = downloader.download_youtube_audio(
            test_links[0]['url'], 
            temp_dir, 
            0
        )
        
        if audio_file and os.path.exists(audio_file):
            print(f"✅ Download successful: {audio_file}")
            
            # Test audio clipping
            output_dir = temp_dir / "output"
            output_dir.mkdir(exist_ok=True)
            
            print("Testing audio clipping...")
            clip_file = downloader.create_audio_clip(
                audio_file,
                test_links[0]['start_time'],
                output_dir,
                0,
                test_links[0]['duration']
            )
            
            if clip_file and os.path.exists(clip_file):
                print(f"✅ Audio clipping successful: {clip_file}")
                
                # Test ZIP creation
                processed_files = [{
                    'file': clip_file,
                    'title': test_links[0]['title'],
                    'index': 0
                }]
                
                print("Testing ZIP creation...")
                zip_path = downloader.create_zip_file(processed_files)
                if os.path.exists(zip_path):
                    print(f"✅ ZIP creation successful: {zip_path}")
                    
                    # Verify ZIP contents
                    with zipfile.ZipFile(zip_path, 'r') as zipf:
                        files = zipf.namelist()
                        print(f"✅ ZIP contains {len(files)} files: {files}")
                        
                    return True
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
    
    return False

def main():
    """Main test function"""
    print("🚀 Starting core functionality tests...")
    
    # Test dependencies first
    if not test_dependencies():
        return False
    
    # Test core functionality
    if test_core_functionality():
        print("\n🎉 All tests passed! Core functionality is working.")
        return True
    else:
        print("\n❌ Core functionality tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
