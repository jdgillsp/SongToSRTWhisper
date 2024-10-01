# SongToSRTWhisper

SongToSRTWhisper is a simple transcription tool that converts audio files into subtitle files (SRT format) using the OpenAI Whisper API. The tool is built with a graphical user interface (GUI) using Python's Tkinter and can handle various audio formats, including MP3, WAV, M4A, OGG, and WEBM. If the audio file is larger than 25 MB, it will be automatically compressed to fit Whisper's API limits.

## Features

- **Transcribe Audio to SRT**: Converts your audio files to SRT subtitle format using the OpenAI Whisper API.
- **Supported Audio Formats**: Works with MP3, WAV, M4A, OGG, WEBM, and more.
- **Automatic Compression**: Compresses audio files larger than 25 MB to meet the size restrictions of Whisper.
- **Real-Time Feedback**: Displays progress and error messages in the GUI.
- **Customizable Output**: Users can choose where to save the SRT files.
- **Multithreaded Processing**: Transcription runs in the background to keep the UI responsive.

## Requirements

- Python 3.x
- The following Python libraries:
  - `pydub`
  - `requests`
  - `tkinter` (part of Python standard library)
 
## Installation

1. Clone the repository:
   git clone https://github.com/yourusername/SongToSRTWhisper.git


2. Install dependencies -> pip install pydub requests

3. Ensure you have set up OpenAI API key in your environment variables:
   export OPENAI_API_KEY="your_openai_api_key"

