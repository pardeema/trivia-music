#!/usr/bin/env python3
"""
Music Rounds Creator - Desktop Application
A local desktop app for trivia authors to create audio rounds from YouTube links.
"""

import sys
import os
import json
import tempfile
import zipfile
import gc
import time
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urlparse, parse_qs

import yt_dlp
import sys

# Use PyQt6 on macOS, PyQt5 on Windows for compatibility
if sys.platform == "darwin":  # macOS
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QLineEdit, QPushButton, QTextEdit, QProgressBar,
        QFileDialog, QMessageBox, QGroupBox, QSpinBox, QCheckBox,
        QSplitter, QFrame, QScrollArea, QGridLayout, QSizePolicy,
        QInputDialog
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
    from PyQt6.QtGui import QFont, QIcon, QPixmap
else:  # Windows and Linux
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QLineEdit, QPushButton, QTextEdit, QProgressBar,
        QFileDialog, QMessageBox, QGroupBox, QSpinBox, QCheckBox,
        QSplitter, QFrame, QScrollArea, QGridLayout, QSizePolicy,
        QInputDialog
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
    from PyQt5.QtGui import QFont, QIcon, QPixmap
import psutil


def parse_timestamp(timestamp_str: str) -> Optional[int]:
    """Parse timestamp string in format '83' or '1:23' and return seconds"""
    if not timestamp_str:
        return None
        
    timestamp_str = timestamp_str.strip()
    
    # Handle format like "1:23" (minutes:seconds)
    if ':' in timestamp_str:
        parts = timestamp_str.split(':')
        if len(parts) == 2:
            try:
                minutes = int(parts[0])
                seconds = int(parts[1])
                return minutes * 60 + seconds
            except ValueError:
                return None
        elif len(parts) == 3:
            # Handle format like "1:23:45" (hours:minutes:seconds)
            try:
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = int(parts[2])
                return hours * 3600 + minutes * 60 + seconds
            except ValueError:
                return None
    
    # Handle format like "83" (seconds only)
    try:
        return int(timestamp_str)
    except ValueError:
        return None


def extract_timestamp_from_url(url: str) -> Optional[int]:
    """Extract timestamp from YouTube URL query parameters"""
    try:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        # Check for 't' parameter (timestamp in seconds)
        if 't' in query_params:
            timestamp_str = query_params['t'][0]
            return parse_timestamp(timestamp_str)
            
        # Check for 'time_continue' parameter (alternative timestamp format)
        if 'time_continue' in query_params:
            timestamp_str = query_params['time_continue'][0]
            return parse_timestamp(timestamp_str)
            
    except Exception:
        pass
    
    return None


class DownloadWorker(QThread):
    """Worker thread for downloading and processing YouTube videos"""
    progress = pyqtSignal(str)
    error = pyqtSignal(str)
    finished = pyqtSignal(str)
    memory_update = pyqtSignal(float)
    
    def __init__(self, links_data: List[Dict], output_dir: str = None):
        super().__init__()
        self.links_data = links_data
        self.output_dir = output_dir
        self.is_running = True
        
    def run(self):
        try:
            # Create temporary directory for processing
            temp_dir = Path(tempfile.mkdtemp(prefix="music_rounds_"))
            output_dir = temp_dir / "output"
            output_dir.mkdir(exist_ok=True)
            
            self.progress.emit(f"Created temporary directory: {temp_dir}")
            self.progress.emit(f"Output directory: {output_dir}")
            self.progress.emit("Starting download process...")
            
            # Set a maximum processing time (10 minutes)
            start_time = time.time()
            max_processing_time = 600  # 10 minutes
            
            processed_files = []
            
            # Track processed URLs to avoid duplicates
            processed_urls = set()
            
            for i, link_data in enumerate(self.links_data):
                if not self.is_running:
                    break
                    
                # Check if we've exceeded the maximum processing time
                if time.time() - start_time > max_processing_time:
                    self.error.emit("Processing timeout: exceeded 10 minutes")
                    break
                    
                # Check if we should stop processing
                if not self.is_running:
                    self.progress.emit("Processing stopped by user")
                    break
                    
                url = link_data['url']
                start_time_seconds = link_data['start_time']
                duration = link_data.get('duration', 15)
                title = link_data.get('title', f'Track {i+1}')
                
                # Skip if we've already processed this URL
                if url in processed_urls:
                    self.progress.emit(f"Skipping duplicate URL: {title}")
                    continue
                    
                processed_urls.add(url)
                self.progress.emit(f"Processing {i+1}/{len(self.links_data)}: {title}")
                
                try:
                    # Download audio
                    self.progress.emit(f"Downloading audio for: {title}")
                    self.progress.emit(f"URL: {url}")
                    self.progress.emit(f"Start time: {start_time_seconds} seconds")
                    self.progress.emit(f"Duration: {duration} seconds")
                    result = self.download_youtube_audio(url, temp_dir, i, start_time_seconds, duration)
                    if result:
                        audio_file, video_title = result
                        self.progress.emit(f"Downloaded to: {audio_file}")
                        
                        # The downloaded file is already the 15-second clip we need
                        processed_files.append({
                            'file': audio_file,
                            'title': video_title,
                            'index': i
                        })
                        self.progress.emit(f"Added to processing list: {audio_file} with title: {video_title}")
                    else:
                        self.progress.emit(f"Failed to download audio for: {title}")
                        # Don't continue to next iteration, break the loop
                        break
                            
                except Exception as e:
                    self.error.emit(f"Error processing {title}: {str(e)}")
                    # Don't continue to next iteration, break the loop
                    break
                    
                # Memory cleanup
                gc.collect()
                memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
                self.memory_update.emit(memory_mb)
                
                # Delay between songs
                if i < len(self.links_data) - 1:
                    self.progress.emit("Waiting 2 seconds before next song...")
                    time.sleep(2)
                    
            if processed_files and self.is_running:
                # Create output file(s)
                self.progress.emit(f"Creating output with {len(processed_files)} processed files...")
                output_path = self.create_output_file(processed_files)
                self.progress.emit(f"Output created: {output_path}")
                self.finished.emit(str(output_path))
            else:
                self.error.emit("No files were successfully processed.")
                
        except Exception as e:
            self.error.emit(f"Processing failed: {str(e)}")
        finally:
            # Cleanup temp directory
            try:
                import shutil
                self.progress.emit(f"Cleaning up temporary directory: {temp_dir}")
                shutil.rmtree(temp_dir, ignore_errors=True)
                self.progress.emit(f"Temporary directory deleted: {temp_dir}")
            except Exception as e:
                self.progress.emit(f"Warning: Could not clean up temp directory {temp_dir}: {str(e)}")
                
    def stop(self):
        self.is_running = False
        
    def download_youtube_audio(self, url: str, temp_dir: Path, index: int, start_time: int, duration: int = 15) -> Optional[tuple[str, str]]:
        """Download audio from YouTube URL starting from specific time"""
        output_path = temp_dir / f"temp_{index}"
        self.progress.emit(f"Download target path: {output_path}")
        
        # Check if URL already has a timestamp
        has_url_timestamp = 't=' in url or 'time_continue=' in url
        
        # Always use explicit start time for consistent behavior
        self.progress.emit(f"Using external downloader with start_time={start_time}s for {duration}-second clip")
        strategies = [
            # Strategy 1: Use external downloader with explicit start time
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
                'sleep_interval': 0,
                'max_sleep_interval': 0,
                'retries': 0,
                'fragment_retries': 0,
                'socket_timeout': 15,
                'extractor_retries': 0,
                'ignoreerrors': True,
                # Always use external downloader with explicit start time
                'external_downloader': 'ffmpeg',
                'external_downloader_args': {
                    'ffmpeg': ['-ss', str(start_time), '-t', str(duration)]
                },
            }
        ]
        
        for i, strategy in enumerate(strategies):
            # Check if we should stop
            if not self.is_running:
                self.progress.emit("Download stopped by user")
                return None
                
            try:
                self.progress.emit(f"Trying download strategy {i+1}...")
                
                with yt_dlp.YoutubeDL(strategy) as ydl:
                    info = ydl.extract_info(url, download=True)
                    
                # Extract video title
                video_title = info.get('title', f'Track {index+1}') if info else f'Track {index+1}'
                self.progress.emit(f"Video title: {video_title}")
                    
                # Find the downloaded file
                self.progress.emit(f"Searching for downloaded file with extensions: .mp3, .m4a, .webm")
                for ext in ['.mp3', '.m4a', '.webm']:
                    potential_file = str(output_path) + ext
                    if os.path.exists(potential_file):
                        self.progress.emit(f"Found downloaded file: {potential_file}")
                        return (potential_file, video_title)
                        
                # Check for files with different naming patterns
                self.progress.emit(f"Searching for files with pattern: temp_{index}.*")
                for file in temp_dir.glob(f"temp_{index}.*"):
                    if file.suffix in ['.mp3', '.m4a', '.webm']:
                        self.progress.emit(f"Found file with different naming: {file}")
                        return (str(file), video_title)
                
                # Check for any audio files in temp directory
                self.progress.emit(f"Searching for any audio files in temp directory")
                for file in temp_dir.glob("*"):
                    if file.suffix.lower() in ['.mp3', '.m4a', '.webm', '.aac', '.ogg']:
                        self.progress.emit(f"Found audio file: {file}")
                        return (str(file), video_title)
                
                # List all files in temp directory for debugging
                self.progress.emit(f"Listing all files in temp directory for debugging:")
                for file in temp_dir.glob("*"):
                    self.progress.emit(f"  - {file.name} ({file.suffix})")
                        
                self.progress.emit(f"Strategy {i+1} completed but no file found")
                        
            except Exception as e:
                self.progress.emit(f"Strategy {i+1} failed: {str(e)}")
                # If this is the last strategy, don't continue
                if i == len(strategies) - 1:
                    self.progress.emit("All download strategies exhausted")
                    return None
                continue
                
        raise Exception("All download strategies failed")
        
    def create_audio_clip(self, input_file: str, start_time: int, output_dir: Path, index: int, duration: int = 15) -> Optional[str]:
        """Create a custom duration audio clip starting from the specified time"""
        output_file = output_dir / f"{index+1:02d}.mp3"
        self.progress.emit(f"Creating clip: {input_file} -> {output_file}")
        self.progress.emit(f"Clip parameters: start={start_time}s, duration={duration}s, format=mp3")
        
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
            
            self.progress.emit(f"Running FFmpeg command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and output_file.exists():
                self.progress.emit(f"FFmpeg successfully created clip: {output_file}")
                return str(output_file)
            else:
                self.progress.emit(f"FFmpeg failed (return code: {result.returncode})")
                if result.stderr:
                    self.progress.emit(f"FFmpeg error: {result.stderr}")
                
        except Exception as e:
            self.progress.emit(f"FFmpeg direct processing failed: {str(e)}")
            
        # Fallback to pydub
        try:
            from pydub import AudioSegment
            
            self.progress.emit("Using pydub fallback for audio processing...")
            self.progress.emit(f"Loading audio file: {input_file}")
            audio = AudioSegment.from_file(input_file)
            
            # Convert start time from seconds to milliseconds
            start_ms = start_time * 1000
            end_ms = start_ms + (15 * 1000)  # 15 seconds
            
            self.progress.emit(f"Extracting clip from {start_ms}ms to {end_ms}ms")
            # Extract the clip
            clip = audio[start_ms:end_ms]
            
            # Export as MP3
            self.progress.emit(f"Exporting clip to: {output_file}")
            clip.export(str(output_file), format='mp3', bitrate='128k')
            
            # Clean up memory
            self.progress.emit("Cleaning up pydub memory...")
            del audio
            del clip
            gc.collect()
            
            self.progress.emit(f"Pydub successfully created clip: {output_file}")
            return str(output_file)
            
        except Exception as e:
            self.progress.emit(f"Pydub processing failed: {str(e)}")
            return None
            
    def create_output_file(self, processed_files: List[Dict]) -> str:
        """Create output file(s) - ZIP for multiple files, single file for one file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Use the selected output directory from the UI
        if self.output_dir is None:
            # Fallback to desktop if no directory selected
            if sys.platform == "darwin":  # macOS
                output_dir = Path.home() / "Desktop"
            elif sys.platform == "win32":  # Windows
                output_dir = Path.home() / "Desktop"
            else:  # Linux
                output_dir = Path.home() / "Desktop"
        else:
            output_dir = Path(self.output_dir)
            
        self.progress.emit(f"Output directory: {output_dir}")
        self.progress.emit(f"Files to include: {len(processed_files)}")
        
        if len(processed_files) == 1:
            # Single file - just copy it with a clean name
            file_info = processed_files[0]
            file_path = file_info['file']
            title = file_info['title']
            
            # Create a clean filename with better formatting
            clean_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            # Replace spaces with underscores and limit length
            clean_title = clean_title.replace(' ', '_')[:40]
            output_filename = f"{clean_title}.mp3"
            output_path = output_dir / output_filename
            
            self.progress.emit(f"Copying single file: {file_path} -> {output_path}")
            
            # Copy the file
            import shutil
            shutil.copy2(file_path, output_path)
            
            self.progress.emit(f"Single file completed: {output_path}")
            return str(output_path)
        else:
            # Multiple files - create ZIP
            zip_filename = f"music_rounds_{timestamp}.zip"
            zip_path = output_dir / zip_filename
            self.progress.emit(f"Creating ZIP file: {zip_path}")
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_info in processed_files:
                    file_path = file_info['file']
                    title = file_info['title']
                    index = file_info['index']
                    
                    # Create a clean filename with better formatting
                    clean_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    # Replace spaces with underscores and limit length
                    clean_title = clean_title.replace(' ', '_')[:40]
                    arcname = f"{index+1:02d}-{clean_title}.mp3"
                    
                    self.progress.emit(f"Adding to ZIP: {file_path} -> {arcname}")
                    zipf.write(file_path, arcname)
                    
            self.progress.emit(f"ZIP file completed: {zip_path}")
            return str(zip_path)


class MusicRoundsApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.download_worker = None
        self.selected_output_dir = None
        self.current_font_size = 11  # Default font size
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Music Rounds Creator")
        self.setGeometry(100, 100, 800, 600)
        
        # Set application icon (if available)
        try:
            self.setWindowIcon(QIcon("icon.png"))
        except:
            pass
            
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(15, 10, 15, 15)
        
        # Title (compact)
        title_label = QLabel("Music Rounds Creator")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("margin-bottom: 2px;")
        main_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Create audio rounds from YouTube links")
        subtitle_font = QFont()
        subtitle_font.setPointSize(9)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #aaa; margin-bottom: 8px;")
        main_layout.addWidget(subtitle_label)
        
        # Create splitter for main content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(splitter, 1)  # Add stretch factor 1
        
        # Left panel - Input
        left_panel = self.create_input_panel()
        left_panel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        splitter.addWidget(left_panel)
        
        # Right panel - Output
        right_panel = self.create_output_panel()
        right_panel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([400, 400])
        
        # Font size control panel
        font_control_panel = QWidget()
        font_control_layout = QHBoxLayout(font_control_panel)
        font_control_layout.setContentsMargins(15, 5, 15, 5)
        font_control_layout.setSpacing(10)
        
        # Font size label
        font_label = QLabel("Font Size:")
        font_label.setStyleSheet(f"font-size: {self.current_font_size}pt; color: #e6e6e6;")
        font_control_layout.addWidget(font_label)
        
        # Font size slider
        self.font_size_slider = QSpinBox()
        self.font_size_slider.setMinimum(8)
        self.font_size_slider.setMaximum(20)
        self.font_size_slider.setValue(self.current_font_size)  # Use instance variable
        self.font_size_slider.setSuffix("pt")
        self.font_size_slider.setFixedWidth(80)
        self.font_size_slider.setStyleSheet("""
            QSpinBox {
                border: 1px solid #555;
                border-radius: 3px;
                padding: 3px 6px;
                background: #3b3b3b;
                color: #e6e6e6;
                font-size: 11px;
                selection-background-color: #0078d4;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 16px;
                border: none;
                background: #4a4a4a;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background: #5a5a5a;
            }
        """)
        self.font_size_slider.valueChanged.connect(self.change_font_size)
        font_control_layout.addWidget(self.font_size_slider)
        
        # Add stretch to push controls to the left
        font_control_layout.addStretch(1)
        
        # Add the font control panel to main layout
        main_layout.addWidget(font_control_panel)
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
    def create_input_panel(self) -> QWidget:
        """Create the input panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(8)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # YouTube URL input
        url_group = QGroupBox("YouTube URL")
        url_group.setStyleSheet(f"QGroupBox {{ font-size: {self.current_font_size}pt; font-weight: bold; margin-top: 8px; }}")
        url_layout = QVBoxLayout(url_group)
        url_layout.setSpacing(6)
        url_layout.setContentsMargins(8, 8, 8, 8)
        
        # Help text (compact)
        help_label = QLabel("Enter a YouTube URL with a timestamp (e.g., &t=83) or paste a URL and we'll prompt for the start time. You can edit the clip duration (12-20 seconds) for each link in the list below.")
        help_label.setWordWrap(True)
        help_label.setStyleSheet(f"color: #aaa; font-size: {self.current_font_size}pt; margin-bottom: 6px;")
        url_layout.addWidget(help_label)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter YouTube URL...")
        url_layout.addWidget(self.url_input)
        
        # Add button
        self.add_button = QPushButton("Add to List")
        self.add_button.clicked.connect(self.add_link)
        url_layout.addWidget(self.add_button)
        
        layout.addWidget(url_group)
        
        # Links list
        links_group = QGroupBox("Links to Process")
        links_group.setStyleSheet(f"QGroupBox {{ font-size: {self.current_font_size}pt; font-weight: bold; margin-top: 8px; }}")
        links_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        links_layout = QVBoxLayout(links_group)
        links_layout.setSpacing(6)
        links_layout.setContentsMargins(8, 8, 8, 8)
        
        # Create a scroll area for the links list
        self.links_scroll = QScrollArea()
        self.links_scroll.setWidgetResizable(True)
        self.links_scroll.setMinimumHeight(150)
        self.links_scroll.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.links_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #444;
                border-radius: 4px;
                background: #1e1e1e;
            }
            QScrollBar:vertical {
                background: #2a2a2a;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #555;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #666;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Create a widget to hold the links
        self.links_widget = QWidget()
        self.links_layout = QVBoxLayout(self.links_widget)
        self.links_layout.setSpacing(3)
        self.links_layout.setContentsMargins(8, 8, 8, 8)
        
        # Add a placeholder label
        self.links_placeholder = QLabel("Added links will appear here...")
        self.links_placeholder.setStyleSheet(f"color: #666; font-style: italic; font-size: {self.current_font_size}pt;")
        self.links_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.links_layout.addWidget(self.links_placeholder)
        
        self.links_scroll.setWidget(self.links_widget)
        links_layout.addWidget(self.links_scroll, 1)  # Add stretch factor 1
        
        # Store the link widgets
        self.link_widgets = []
        
        # Clear button
        self.clear_button = QPushButton("Clear All")
        self.clear_button.clicked.connect(self.clear_links)
        links_layout.addWidget(self.clear_button)
        
        layout.addWidget(links_group)
        
        # Process and Stop buttons
        button_layout = QHBoxLayout()
        
        self.process_button = QPushButton("Create Music Round")
        self.process_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px;
                font-size: {self.current_font_size}pt;
                font-weight: bold;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #218838;
            }}
            QPushButton:disabled {{
                background-color: #555;
                color: #888;
            }}
        """)
        self.process_button.clicked.connect(self.process_links)
        button_layout.addWidget(self.process_button)
        
        self.stop_button = QPushButton("Stop Processing")
        self.stop_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px;
                font-size: {self.current_font_size}pt;
                font-weight: bold;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #c82333;
            }}
            QPushButton:disabled {{
                background-color: #555;
                color: #888;
            }}
        """)
        self.stop_button.clicked.connect(self.stop_processing)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        layout.addLayout(button_layout)
        
        return panel
        
    def create_output_panel(self) -> QWidget:
        """Create the output panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(8)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Output group
        output_group = QGroupBox("Output")
        output_group.setStyleSheet(f"QGroupBox {{ font-size: {self.current_font_size}pt; font-weight: bold; margin-top: 8px; }}")
        output_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        output_layout = QVBoxLayout(output_group)
        output_layout.setSpacing(6)
        output_layout.setContentsMargins(8, 8, 8, 8)
        
        # Output directory
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Output Directory:"))
        
        # Set default output directory
        if sys.platform == "darwin":  # macOS
            default_dir = str(Path.home() / "Desktop")
        elif sys.platform == "win32":  # Windows
            default_dir = str(Path.home() / "Desktop")
        else:  # Linux
            default_dir = str(Path.home() / "Desktop")
            
        self.output_dir_label = QLabel(default_dir)
        self.output_dir_label.setStyleSheet("color: #aaa; font-style: italic; padding: 2px;")
        dir_layout.addWidget(self.output_dir_label)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_output_dir)
        dir_layout.addWidget(self.browse_button)
        
        output_layout.addLayout(dir_layout)
        
        # Log output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.log_output.setStyleSheet(f"""
            QTextEdit {{
                background-color: #2b2b2b;
                color: #e6e6e6;
                border: 1px solid #555;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: {self.current_font_size}pt;
            }}
        """)
        output_layout.addWidget(self.log_output, 1)  # Add stretch factor 1
        
        layout.addWidget(output_group)
        
        # Memory usage
        memory_group = QGroupBox("System Info")
        memory_layout = QVBoxLayout(memory_group)
        
        self.memory_label = QLabel("Memory Usage: --")
        memory_layout.addWidget(self.memory_label)
        
        # Update memory usage periodically
        self.memory_timer = QTimer()
        self.memory_timer.timeout.connect(self.update_memory_usage)
        self.memory_timer.start(2000)  # Update every 2 seconds
        
        layout.addWidget(memory_group)
        
        # Add stretch to make the output panel expand
        layout.addStretch(1)
        
        return panel
        
    def add_link(self):
        """Add a link to the processing list"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a YouTube URL")
            return
            
        # Validate URL
        if "youtube.com" not in url and "youtu.be" not in url:
            QMessageBox.warning(self, "Warning", "Please enter a valid YouTube URL")
            return
            
        # Try to extract timestamp from URL first
        start_time = extract_timestamp_from_url(url)
        
        if start_time is None:
            self.log_output.append(f"No timestamp found in URL: {url}")
            # No timestamp in URL, prompt user
            timestamp_str, ok = QInputDialog.getText(
                self, 
                "Enter Start Time", 
                "Enter the start time (e.g., '83' for 1:23 or '1:23'):",
                text=""
            )
            
            if not ok:
                self.log_output.append("User cancelled timestamp input")
                return  # User cancelled
                
            start_time = parse_timestamp(timestamp_str)
            if start_time is None:
                self.log_output.append(f"Invalid timestamp format: {timestamp_str}")
                QMessageBox.warning(self, "Warning", "Invalid timestamp format. Please use '83' or '1:23'")
                return
            else:
                self.log_output.append(f"Parsed timestamp '{timestamp_str}' to {start_time} seconds")
                # Convert youtube.com URLs to youtu.be format for better compatibility
                if 'youtube.com/watch?v=' in url:
                    # Extract video ID
                    video_id = url.split('watch?v=')[1].split('&')[0]
                    # Create youtu.be URL with timestamp
                    url = f"https://youtu.be/{video_id}?t={start_time}"
                    self.log_output.append(f"Converted to youtu.be format: {url}")
                else:
                    # For other formats, just add timestamp
                    if '?' in url:
                        url += f"&t={start_time}"
                    else:
                        url += f"?t={start_time}"
                    self.log_output.append(f"Modified URL to include timestamp: {url}")
                # Since we've added the timestamp to the URL, we don't need the separate start_time parameter
                # The external FFmpeg downloader will use the timestamp from the URL
        else:
            # Timestamp found in URL, use it
            self.log_output.append(f"Extracted timestamp from URL: {start_time} seconds")
            
        # Convert to minutes and seconds for display
        minutes = start_time // 60
        seconds = start_time % 60
        
        # Add link widget to the list
        self.add_link_widget(url, start_time, 15)  # Default duration is 15 seconds
            
        # Clear inputs
        self.url_input.clear()
        
        self.log_output.append(f"Added: {url} (start at {minutes:02d}:{seconds:02d}, duration: 15s)")
        
    def add_link_widget(self, url: str, start_time: int, duration: int):
        """Add a link widget to the list"""
        # Remove placeholder if this is the first link
        if self.links_placeholder.isVisible():
            self.links_placeholder.setVisible(False)
        
        # Create link widget
        link_widget = QWidget()
        link_layout = QHBoxLayout(link_widget)
        link_layout.setContentsMargins(8, 4, 8, 4)
        link_layout.setSpacing(8)
        
        # Number label
        number_label = QLabel(f"{len(self.link_widgets) + 1}.")
        number_label.setMinimumWidth(25)
        number_label.setMaximumWidth(25)
        number_label.setStyleSheet(f"font-weight: bold; color: #888; font-size: {self.current_font_size}pt;")
        link_layout.addWidget(number_label)
        
        # URL and time info
        minutes = start_time // 60
        seconds = start_time % 60
        info_label = QLabel(f"{url} | {minutes:02d}:{seconds:02d}")
        info_label.setWordWrap(True)
        info_label.setStyleSheet(f"color: #e0e0e0; font-size: {self.current_font_size}pt; background: transparent; border: none;")
        link_layout.addWidget(info_label, 1)  # Stretch factor 1
        
        # Duration spinbox
        duration_spinbox = QSpinBox()
        duration_spinbox.setMinimum(12)
        duration_spinbox.setMaximum(20)
        duration_spinbox.setValue(duration)
        duration_spinbox.setSuffix("s")
        duration_spinbox.setFixedWidth(45)
        duration_spinbox.setFixedHeight(20)
        duration_spinbox.setStyleSheet(f"""
            QSpinBox {{
                border: 1px solid #555;
                border-radius: 2px;
                padding: 1px 3px;
                background: #2a2a2a;
                color: #e0e0e0;
                font-size: {self.current_font_size}pt;
                selection-background-color: #0078d4;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 12px;
                border: none;
                background: #3a3a3a;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background: #4a4a4a;
            }}
            QSpinBox::up-arrow {{
                width: 6px;
                height: 6px;
                image: none;
                border-left: 2px solid #888;
                border-bottom: 2px solid #888;
                transform: rotate(45deg);
            }}
            QSpinBox::down-arrow {{
                width: 6px;
                height: 6px;
                image: none;
                border-left: 2px solid #888;
                border-top: 2px solid #888;
                transform: rotate(45deg);
            }}
        """)
        link_layout.addWidget(duration_spinbox)
        
        # Remove button
        remove_button = QPushButton("×")
        remove_button.setFixedSize(16, 16)
        remove_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: {self.current_font_size}pt;
            }}
            QPushButton:hover {{
                background-color: #c82333;
            }}
        """)
        remove_button.clicked.connect(lambda: self.remove_link_widget(link_widget))
        link_layout.addWidget(remove_button)
        
        # Style the link widget itself
        link_widget.setStyleSheet("""
            QWidget {
                background: #252525;
                border: 1px solid #333;
                border-radius: 3px;
                margin: 1px;
            }
        """)
        
        # Store the widget data
        link_data = {
            'widget': link_widget,
            'url': url,
            'start_time': start_time,
            'duration_spinbox': duration_spinbox,
            'number_label': number_label,
            'info_label': info_label
        }
        
        self.link_widgets.append(link_data)
        self.links_layout.addWidget(link_widget)
        
        # Update numbering
        self.update_link_numbers()
        
    def remove_link_widget(self, widget):
        """Remove a link widget from the list"""
        # Find and remove the widget data
        for i, link_data in enumerate(self.link_widgets):
            if link_data['widget'] == widget:
                self.link_widgets.pop(i)
                break
        
        # Remove the widget from the layout
        self.links_layout.removeWidget(widget)
        widget.deleteLater()
        
        # Update numbering
        self.update_link_numbers()
        
        # Show placeholder if no links left
        if not self.link_widgets:
            self.links_placeholder.setVisible(True)
            
    def update_link_numbers(self):
        """Update the numbering of all link widgets"""
        for i, link_data in enumerate(self.link_widgets):
            link_data['number_label'].setText(f"{i + 1}.")
        
    def clear_links(self):
        """Clear all links from the list"""
        # Remove all link widgets
        for link_data in self.link_widgets[:]:  # Copy the list to avoid modification during iteration
            self.remove_link_widget(link_data['widget'])
        
        # Show placeholder
        self.links_placeholder.setVisible(True)
        self.log_output.append("Cleared all links")
        
    def browse_output_dir(self):
        """Browse for output directory"""
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.selected_output_dir = dir_path
            self.output_dir_label.setText(dir_path)
            self.log_output.append(f"Output directory set to: {dir_path}")
            
    def process_links(self):
        """Process all links in the list"""
        if not self.link_widgets:
            QMessageBox.warning(self, "Warning", "Please add some links to process")
            return
            
        # Parse links from widgets
        links_data = []
        for i, link_data in enumerate(self.link_widgets):
            url = link_data['url']
            start_time = link_data['start_time']
            duration = link_data['duration_spinbox'].value()
            
            links_data.append({
                'url': url,
                'start_time': start_time,
                'duration': duration,
                'title': f'Track {i+1}'
            })
                
        if not links_data:
            QMessageBox.warning(self, "Warning", "No valid links found")
            return
            
        # Start processing
        self.start_processing(links_data)
        
    def start_processing(self, links_data: List[Dict]):
        """Start the processing thread"""
        # Disable UI
        self.process_button.setEnabled(False)
        self.add_button.setEnabled(False)
        self.clear_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Clear log
        self.log_output.clear()
        self.log_output.append("Starting processing...")
        self.log_output.append(f"Processing {len(links_data)} links...")
        
        # Log the links being processed
        for i, link_data in enumerate(links_data):
            duration = link_data.get('duration', 15)
            self.log_output.append(f"Link {i+1}: {link_data['url']} (start at {link_data['start_time']}s, duration: {duration}s)")
            # Check if this is a manually entered timestamp
            if 't=' not in link_data['url'] and 'time_continue=' not in link_data['url']:
                self.log_output.append(f"  -> This link has a manually entered timestamp")
        
        # Create and start worker thread
        output_dir = getattr(self, 'selected_output_dir', None)
        self.download_worker = DownloadWorker(links_data, output_dir)
        self.download_worker.progress.connect(self.update_progress)
        self.download_worker.error.connect(self.handle_error)
        self.download_worker.finished.connect(self.handle_success)
        self.download_worker.memory_update.connect(self.update_memory_usage)
        self.download_worker.start()
        
    def stop_processing(self):
        """Stop the processing thread"""
        if self.download_worker and self.download_worker.isRunning():
            self.log_output.append("Stopping processing...")
            self.download_worker.stop()
            
            # Wait for thread to finish with timeout
            if not self.download_worker.wait(5000):  # 5 second timeout
                self.log_output.append("Force terminating worker thread...")
                self.download_worker.terminate()
                self.download_worker.wait(2000)  # Wait 2 more seconds
                
            self.log_output.append("Processing stopped.")
            
        # Re-enable UI
        self.process_button.setEnabled(True)
        self.add_button.setEnabled(True)
        self.clear_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Processing stopped")
        
    def update_progress(self, message: str):
        """Update progress message"""
        self.log_output.append(message)
        self.status_bar.showMessage(message)
        
    def handle_error(self, error: str):
        """Handle processing error"""
        self.log_output.append(f"ERROR: {error}")
        self.status_bar.showMessage("Processing failed")
        
        # Re-enable UI
        self.process_button.setEnabled(True)
        self.add_button.setEnabled(True)
        self.clear_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        QMessageBox.critical(self, "Error", f"Processing failed:\n{error}")
        
    def handle_success(self, zip_path: str):
        """Handle successful processing"""
        self.log_output.append(f"SUCCESS: Created {zip_path}")
        self.status_bar.showMessage("Processing completed successfully")
        
        # Re-enable UI
        self.process_button.setEnabled(True)
        self.add_button.setEnabled(True)
        self.clear_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        # Show success message
        QMessageBox.information(
            self, 
            "Success", 
            f"Music round created successfully!\n\nFile saved to:\n{zip_path}"
        )
        
    def update_memory_usage(self, memory_mb: float = None):
        """Update memory usage display"""
        if memory_mb is None:
            memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
            
        self.memory_label.setText(f"Memory Usage: {memory_mb:.1f} MB")
        
    def change_font_size(self, new_size: int):
        """Change the font size throughout the application"""
        # Get the current application
        app = QApplication.instance()
        
        # Update the instance variable
        self.current_font_size = new_size
        
        # Update the global stylesheet with the new font size
        stylesheet = f"""
            QMainWindow {{
                background-color: #2b2b2b;
                color: #e6e6e6;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: {new_size}pt;
            }}
            QWidget {{
                background-color: #2b2b2b;
                color: #e6e6e6;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: {new_size}pt;
            }}
            QGroupBox {{
                border: 1px solid #555;
                border-radius: 5px;
                margin-top: 1ex;
                font-weight: bold;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: {new_size}pt;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: {new_size}pt;
            }}
            QLineEdit, QTextEdit, QSpinBox {{
                background-color: #3b3b3b;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 5px;
                color: #e6e6e6;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: {new_size}pt;
            }}
            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {{
                border: 1px solid #0078d4;
            }}
            QPushButton {{
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: {new_size}pt;
            }}
            QPushButton:hover {{
                background-color: #106ebe;
            }}
            QPushButton:pressed {{
                background-color: #005a9e;
            }}
            QPushButton:disabled {{
                background-color: #555;
                color: #888;
            }}
            QLabel {{
                color: #e6e6e6;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: {new_size}pt;
            }}
            QProgressBar {{
                border: 1px solid #555;
                border-radius: 3px;
                text-align: center;
                background-color: #3b3b3b;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: {new_size}pt;
            }}
            QProgressBar::chunk {{
                background-color: #0078d4;
                border-radius: 2px;
            }}
            QStatusBar {{
                background-color: #2b2b2b;
                color: #e6e6e6;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: {new_size}pt;
            }}
        """
        
        # Apply the updated global stylesheet
        app.setStyleSheet(stylesheet)
        
        # Update all individual widget stylesheets
        self.update_widget_font_sizes(new_size)
        
        # Update the log output to show the change
        self.log_output.append(f"Font size changed to {new_size}pt")
        
    def update_widget_font_sizes(self, new_size: int):
        """Update font sizes for all widgets with custom stylesheets"""
        # Update font size slider
        self.font_size_slider.setStyleSheet(f"""
            QSpinBox {{
                border: 1px solid #555;
                border-radius: 3px;
                padding: 3px 6px;
                background: #3b3b3b;
                color: #e6e6e6;
                font-size: {new_size}pt;
                selection-background-color: #0078d4;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 16px;
                border: none;
                background: #4a4a4a;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background: #5a5a5a;
            }}
        """)
        
        # Update group boxes
        for group in self.findChildren(QGroupBox):
            group.setStyleSheet(f"QGroupBox {{ font-size: {new_size}pt; font-weight: bold; margin-top: 8px; }}")
        
        # Update help labels and placeholders
        for label in self.findChildren(QLabel):
            current_style = label.styleSheet()
            if "font-size:" in current_style:
                # Update existing font-size declarations
                import re
                new_style = re.sub(r'font-size:\s*\d+pt', f'font-size: {new_size}pt', current_style)
                label.setStyleSheet(new_style)
        
        # Update log output
        self.log_output.setStyleSheet(f"""
            QTextEdit {{
                background-color: #2b2b2b;
                color: #e6e6e6;
                border: 1px solid #555;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: {new_size}pt;
            }}
        """)
        
        # Update process and stop buttons
        self.process_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px;
                font-size: {new_size}pt;
                font-weight: bold;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #218838;
            }}
            QPushButton:disabled {{
                background-color: #555;
                color: #888;
            }}
        """)
        
        self.stop_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px;
                font-size: {new_size}pt;
                font-weight: bold;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #c82333;
            }}
            QPushButton:disabled {{
                background-color: #555;
                color: #888;
            }}
        """)
        
        # Update links scroll area
        self.links_scroll.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid #444;
                border-radius: 4px;
                background: #1e1e1e;
            }}
            QScrollBar:vertical {{
                background: #2a2a2a;
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: #555;
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #666;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        
        # Update link widgets
        for link_data in self.link_widgets:
            # Update number label
            link_data['number_label'].setStyleSheet(f"font-weight: bold; color: #888; font-size: {new_size}pt;")
            
            # Update info label
            link_data['info_label'].setStyleSheet(f"color: #e0e0e0; font-size: {new_size}pt; background: transparent; border: none;")
            
            # Update duration spinbox
            link_data['duration_spinbox'].setStyleSheet(f"""
                QSpinBox {{
                    border: 1px solid #555;
                    border-radius: 2px;
                    padding: 1px 3px;
                    background: #2a2a2a;
                    color: #e0e0e0;
                    font-size: {new_size}pt;
                    selection-background-color: #0078d4;
                }}
                QSpinBox::up-button, QSpinBox::down-button {{
                    width: 12px;
                    border: none;
                    background: #3a3a3a;
                }}
                QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                    background: #4a4a4a;
                }}
                QSpinBox::up-arrow {{
                    width: 6px;
                    height: 6px;
                    image: none;
                    border-left: 2px solid #888;
                    border-bottom: 2px solid #888;
                    transform: rotate(45deg);
                }}
                QSpinBox::down-arrow {{
                    width: 6px;
                    height: 6px;
                    image: none;
                    border-left: 2px solid #888;
                    border-top: 2px solid #888;
                    transform: rotate(45deg);
                }}
            """)
        
    def closeEvent(self, event):
        """Handle application close"""
        if self.download_worker and self.download_worker.isRunning():
            self.download_worker.stop()
            self.download_worker.wait()
        event.accept()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Apply dark mode styling with responsive fonts for Windows
    app.setStyleSheet("""
        QMainWindow {
            background-color: #2b2b2b;
            color: #e6e6e6;
            font-family: 'Segoe UI', 'Arial', sans-serif;
        }
        QWidget {
            background-color: #2b2b2b;
            color: #e6e6e6;
            font-family: 'Segoe UI', 'Arial', sans-serif;
        }
        QGroupBox {
            border: 1px solid #555;
            border-radius: 5px;
            margin-top: 1ex;
            font-weight: bold;
            font-family: 'Segoe UI', 'Arial', sans-serif;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            font-family: 'Segoe UI', 'Arial', sans-serif;
        }
        QLineEdit, QTextEdit, QSpinBox {
            background-color: #3b3b3b;
            border: 1px solid #555;
            border-radius: 3px;
            padding: 5px;
            color: #e6e6e6;
            font-family: 'Segoe UI', 'Arial', sans-serif;
        }
        QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {
            border: 1px solid #0078d4;
        }
        QPushButton {
            background-color: #0078d4;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
            font-family: 'Segoe UI', 'Arial', sans-serif;
        }
        QPushButton:hover {
            background-color: #106ebe;
        }
        QPushButton:pressed {
            background-color: #005a9e;
        }
        QPushButton:disabled {
            background-color: #555;
            color: #888;
        }
        QLabel {
            color: #e6e6e6;
            font-family: 'Segoe UI', 'Arial', sans-serif;
        }
        QProgressBar {
            border: 1px solid #555;
            border-radius: 3px;
            text-align: center;
            background-color: #3b3b3b;
            font-family: 'Segoe UI', 'Arial', sans-serif;
        }
        QProgressBar::chunk {
            background-color: #0078d4;
            border-radius: 2px;
        }
        QStatusBar {
            background-color: #2b2b2b;
            color: #e6e6e6;
            font-family: 'Segoe UI', 'Arial', sans-serif;
        }
    """)
    
    # Create and show main window
    window = MusicRoundsApp()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
