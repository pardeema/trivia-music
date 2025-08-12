# Music Rounds Creator

A desktop application for creating music rounds from YouTube links. Perfect for trivia hosts, music educators, and anyone who needs to create audio clips from specific timestamps in YouTube videos.

## Features

- 🎵 **15-Second Audio Clips**: Automatically downloads and clips 15-second segments from YouTube videos
- ⏰ **Timestamp Support**: Works with URLs containing timestamps (`t=83`) or prompts for manual entry
- 📝 **Batch Processing**: Add multiple YouTube links and process them all at once
- 🎯 **Smart URL Handling**: Converts `youtube.com` URLs to `youtu.be` format for better compatibility
- 📦 **ZIP Output**: Creates organized ZIP files with numbered tracks and descriptive filenames
- 🛑 **Stop/Cancel**: Built-in stop button to cancel processing at any time
- 🌙 **Dark Mode**: Modern dark theme interface
- 📊 **Progress Tracking**: Real-time progress updates and detailed logging

## Screenshots

The application features a clean, modern interface with:
- **Left Panel**: URL input and numbered list of tracks to process
- **Right Panel**: Output directory selection and detailed processing logs
- **Bottom**: Process and Stop buttons with progress tracking

## System Requirements

- **Python 3.9 or higher** (Python 3.10+ recommended)
- **FFmpeg** (required for audio processing)
- **Internet connection** (for downloading YouTube content)

## Installation

### Option 1: Standalone Executable (Recommended) 🎯

**For most users - no technical setup required!**

Download the appropriate executable for your system:

- **macOS**: `MusicRoundsCreator_macOS_YYYYMMDD_HHMMSS.zip`
- **Windows**: `MusicRoundsCreator_Windows_YYYYMMDD_HHMMSS.zip`

**Installation Steps:**
1. Download the ZIP file for your platform
2. Extract the ZIP file to a folder of your choice
3. Double-click the executable to run
4. **macOS**: If blocked by security:
   - **Option 1**: Right-click the app and select "Open" from the context menu
   - **Option 2**: Go to System Preferences → Privacy & Security → Security section → Click "Open Anyway" next to MusicRoundsCreator
5. **Windows**: If SmartScreen blocks it, click "More info" then "Run anyway"

**Requirements:**
- **macOS**: macOS 10.14 (Mojave) or later
- **Windows**: Windows 10 or later
- **No additional software required** - everything is bundled!

### Option 2: Developer Installation

For developers who want to modify the code or build their own executables.

#### Prerequisites

##### 1. Install Python

**macOS:**
```bash
# Using Homebrew (recommended)
brew install python

# Or download from python.org
# Visit https://www.python.org/downloads/macos/
```

**Windows:**
```bash
# Download from python.org
# Visit https://www.python.org/downloads/windows/
# Make sure to check "Add Python to PATH" during installation
```

##### 2. Install FFmpeg

**macOS:**
```bash
# Using Homebrew (recommended)
brew install ffmpeg

# Or using MacPorts
sudo port install ffmpeg
```

**Windows:**
```bash
# Using Chocolatey (recommended)
choco install ffmpeg

# Or download from https://ffmpeg.org/download.html
# Extract to C:\ffmpeg and add to PATH
```

#### Application Installation

##### Option A: Clone and Run

1. **Clone the repository:**
```bash
git clone https://github.com/pardeema/trivia-music.git
cd trivia-music
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
python main.py
```

##### Option B: Download and Run

1. **Download the repository:**
   - Click the green "Code" button on GitHub
   - Select "Download ZIP"
   - Extract the ZIP file to your desired location

2. **Open terminal/command prompt:**
   - Navigate to the extracted folder
   - Install dependencies: `pip install -r requirements.txt`
   - Run: `python main.py`

#### Building Standalone Executables

To create your own standalone executables:

```bash
# Build for current platform
python build_all.py

# Or build specifically for each platform
python build_macos.py    # macOS only
python build_windows.py  # Windows only
```

**Important Notes for Developers:**

- **macOS**: Uses PyQt6 for better compatibility with PyInstaller
- **Windows**: Uses PyQt5 to avoid DLL loading issues with PyInstaller
- **Dependencies**: The `requirements.txt` automatically installs the correct PyQt version for your platform
- **FFmpeg**: Build scripts automatically download and include FFmpeg binaries

This will create ZIP files with standalone executables that include all dependencies.

## Usage Guide

### Adding YouTube Links

#### Method 1: URLs with Timestamps
1. Copy a YouTube URL that includes a timestamp:
   ```
   https://youtu.be/VIDEO_ID?t=83
   https://youtu.be/VIDEO_ID?si=something&t=139
   ```
2. Paste the URL in the input field
3. Click "Add to List"
4. The timestamp will be automatically detected and displayed

#### Method 2: Manual Timestamp Entry
1. Paste a YouTube URL without a timestamp:
   ```
   https://youtu.be/VIDEO_ID
   https://youtube.com/watch?v=VIDEO_ID
   ```
2. Click "Add to List"
3. Enter the start time when prompted:
   - **Seconds only**: `83` (for 1:23)
   - **Minutes:Seconds**: `1:23`
   - **Hours:Minutes:Seconds**: `1:23:45`

### Processing Tracks

1. **Set Output Directory** (optional):
   - Click "Browse..." to select where ZIP files will be saved
   - Default: Desktop folder

2. **Process All Tracks**:
   - Click "Create Music Round"
   - Monitor progress in the log panel
   - Use "Stop Processing" if needed

3. **Output**:
   - ZIP file created with format: `music_rounds_YYYYMMDD_HHMMSS.zip`
   - Tracks named: `01-Artist_Song_Title.mp3`, `02-Another_Song.mp3`, etc.

### Track Management

- **Numbered List**: Tracks are automatically numbered (1, 2, 3...) as you add them
- **Clear All**: Use "Clear All" to remove all tracks and start over
- **Processing Order**: Tracks are processed in the order they appear in the list

## File Formats

### Input
- **YouTube URLs**: Any valid YouTube video URL
- **Timestamp Formats**: 
  - URL parameter: `?t=83` or `&t=139`
  - Manual entry: `83`, `1:23`, `1:23:45`

### Output
- **Audio Format**: MP3 (128kbps, 44.1kHz)
- **Clip Duration**: 15 seconds per track
- **File Size**: ~238KB per track (much smaller than full videos)
- **Archive**: ZIP file containing all processed tracks

## Troubleshooting

### Common Issues

#### "FFmpeg not found"
- **Solution**: Install FFmpeg (see Installation section)
- **Verify**: Run `ffmpeg -version` in terminal

#### "Python not found"
- **Solution**: Install Python and add to PATH
- **Verify**: Run `python --version` in terminal

#### "Download fails"
- **Solution**: Check internet connection and URL validity
- **Try**: Different YouTube URL or timestamp

#### "Processing hangs"
- **Solution**: Use "Stop Processing" button
- **Try**: Processing fewer tracks at once

#### "Permission denied"
- **macOS**: Check folder permissions
- **Windows**: Run as administrator if needed

#### "macOS Security Warning - App can't be opened"
- **Solution**: macOS blocks unsigned apps by default
- **Option 1**: Right-click the app → "Open" → "Open" in the dialog
- **Option 2**: System Preferences → Privacy & Security → Security section → "Open Anyway"
- **Why**: This happens because the app isn't code-signed by Apple (common for open-source apps)

### Performance Tips

- **Batch Size**: Process 5-10 tracks at a time for best performance
- **Internet**: Use stable internet connection
- **Storage**: Ensure sufficient disk space (~1MB per track)
- **Memory**: Close other applications if processing many tracks

## Technical Details

### Dependencies
- **PyQt6**: GUI framework
- **yt-dlp**: YouTube video downloading
- **pydub**: Audio processing (fallback)
- **FFmpeg**: Audio conversion and clipping

### Architecture
- **Multi-threaded**: Downloads run in background threads
- **External FFmpeg**: Uses FFmpeg for precise 15-second clipping
- **Smart URL handling**: Converts formats for better compatibility
- **Error handling**: Graceful failure recovery and user feedback

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. See LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section above
- Ensure all prerequisites are installed

## Changelog

### Version 1.0
- Initial release
- 15-second audio clip creation
- YouTube timestamp support
- Batch processing
- Dark mode interface
- ZIP output with descriptive filenames
- Stop/cancel functionality
- Numbered track list
