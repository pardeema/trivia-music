# Music Rounds Creator

**Current Version**: 1.1 (Latest)

A desktop application for creating music rounds from YouTube links. Perfect for trivia hosts, music educators, and anyone who needs to create audio clips from specific timestamps in YouTube videos.

## Features

- 🎵 **Custom Duration Audio Clips**: Automatically downloads and clips 12-20 second segments from YouTube videos (default 15 seconds)
- ⏰ **Timestamp Support**: Works with URLs containing timestamps (`t=83`) or prompts for manual entry
- 📝 **Batch Processing**: Add multiple YouTube links and process them all at once
- 🎯 **Smart URL Handling**: Converts `youtube.com` URLs to `youtu.be` format for better compatibility
- 📦 **ZIP Output**: Creates organized ZIP files with numbered tracks and descriptive filenames
- 🛑 **Stop/Cancel**: Built-in stop button to cancel processing at any time
- 🌙 **Dark Mode**: Modern dark theme interface
- 📊 **Progress Tracking**: Real-time progress updates and detailed logging

## Screenshots
1. Get your YT URL -- either at the top of the browser or share and get timestamp
<img style="width: 50%;" alt="Copy YT URL with timestamp" src="https://github.com/user-attachments/assets/92a0560d-5464-4843-994d-65f773b6a26d" />

2. In the app, paste the URL with the timestamp
<img style="width: 50%;" alt="Add YT URL with Timestamp" src="https://github.com/user-attachments/assets/71883b9d-42c2-4474-bc65-6a9827dd605a" />

3. If you don't use the timestamp feature in the YT link you will be prompted to say where you want the audio clip to start
<img style="width: 50%;" alt="Add YT URL without timestamp" src="https://github.com/user-attachments/assets/c1c56c83-a333-4d72-9685-07f6e37d815d" />

4. You can edit the duration of the returned audio clip. The recommended default is 15seconds, but you can go between 12 and 20s.
<img style="width: 50%;" alt="links-added-change-clip-length" src="https://github.com/user-attachments/assets/445d826a-21a1-4a6b-9360-23afff2cbd1c" />

5. Once you run it, confirmation will pop up indicating success of where the zip file lives.
<img style="width: 50%;" alt="rounds-downloaded" src="https://github.com/user-attachments/assets/a8b84ea8-6763-4fbb-835f-1b5efc47b3bd" />


## System Requirements

- **Python 3.9 or higher** (Python 3.10+ recommended)
- **FFmpeg** (required for audio processing)
- **Internet connection** (for downloading YouTube content)

## Installation

### Option 1: Standalone Executable (Recommended) 🎯

**For most users - no technical setup required!**

Download the appropriate executable for your system:

#### **Windows (Latest)**
- **Download**: [MusicRoundsCreator_Windows_20250813_094944.zip](https://files.kewpielabs.com/MusicRoundsCreator_Windows_20250813_094944.zip)
- **MD5 Hash**: `5BE4701FE57FFE58B03111EC6365AA89`
- **Size**: 129MB

#### **macOS (Latest)**
- **Download**: [MusicRoundsCreator_macOS_20250812_222817.zip](https://files.kewpielabs.com/MusicRoundsCreator_macOS_20250812_222817.zip)
- **MD5 Hash**: `c9b80a514943974222f7ecd144d53f24`
- **Size**: 60MB

**Installation Steps:**
1. Download the ZIP file for your platform using the link above
2. Extract the ZIP file to a folder of your choice
3. Double-click the executable to run
4. **macOS**: If blocked by security:
   - **Option 1**: Right-click the app and select "Open" from the context menu
   - **Option 2**: Go to System Preferences → Privacy & Security → Security section → Click "Open Anyway" next to MusicRoundsCreator
5. **Windows**: If SmartScreen blocks it, click "More info" then "Run anyway"

**File Integrity Verification:**
To verify the downloaded file hasn't been corrupted, you can check the MD5 hash:

**Windows:**
```powershell
Get-FileHash -Algorithm MD5 "MusicRoundsCreator_Windows_20250812_120053.zip"
```

**macOS/Linux:**
```bash
md5 MusicRoundsCreator_macOS_20250812_111433.zip
```

The hash should match the one listed above for your platform.

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
5. Edit the clip duration (12-20 seconds) using the spinbox next to each link if needed

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
4. Edit the clip duration (12-20 seconds) using the spinbox next to each link if needed

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
- **Individual Duration Control**: Each track has its own duration spinbox (12-20 seconds)
- **Remove Individual Tracks**: Click the "×" button next to any track to remove it
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
- **Clip Duration**: 12-20 seconds per track (user configurable, default 15)
- **File Size**: ~190-320KB per track (varies with duration, much smaller than full videos)
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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The MIT License is one of the most permissive open source licenses, allowing:
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use
- ✅ No warranty requirements

**Note**: This project uses FFmpeg (LGPL/GPL) and yt-dlp (Unlicense) as dependencies. The MIT license applies to this project's code, while the dependencies maintain their respective licenses.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section above
- Ensure all prerequisites are installed

## Changelog

### Version 1.1 (Latest)
- **Fixed Windows PyQt6 DLL loading issues** - Switched to PyQt5 for better compatibility
- **Improved font scaling** - Responsive fonts that scale properly with window resizing
- **Enhanced platform compatibility** - macOS uses PyQt6, Windows uses PyQt5
- **Better user experience** - Improved readability and responsive design
- **Updated documentation** - Added developer notes and troubleshooting information

### Version 1.0
- Initial release
- 15-second audio clip creation
- YouTube timestamp support
- Batch processing
- Dark mode interface
- ZIP output with descriptive filenames
- Stop/cancel functionality
- Numbered track list
