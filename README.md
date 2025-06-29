# YouTube Video Summarizer

This tool creates text summaries from YouTube videos using their transcripts. It uses AI-powered summarization to generate concise summaries and saves them as text files.

## Features

- Extracts transcripts from YouTube videos
- Generates AI-powered summaries
- Saves summaries to text files
- Supports both youtube.com and youtu.be URLs
- Handles long videos by processing transcript in chunks

## Installation

1. Make sure you have Python 3.7+ installed
2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the script:
```bash
python yt_summarizer.py
```

2. Enter a YouTube URL when prompted
3. The summary will be saved in the `summaries` folder with the video title as the filename

## Notes

- The video must have closed captions/subtitles available
- Internet connection is required
- First-time use will download the AI model (approximately 1.2GB)
- Summary length is optimized for readability

## Error Handling

The tool handles various errors gracefully:
- Invalid URLs
- Missing transcripts
- Network issues
- File system errors 