from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
import re
import os
import datetime

def print_header():
    print(r"""
 __   _______ _____                                    _              
 \ \ / /_   _/  ___|                                  (_)             
  \ V /  | | \ `--.  _   _ _ __ ___  _ __ ___   __ _ _ ___  ___ _ __ 
   \ /   | |  `--. \| | | | '_ ` _ \| '_ ` _ \ / _` | / __|/ _ \ '__|
   | |   | | /\__/ /| |_| | | | | | | | | | | | (_| | \__ \  __/ |   
   \_/   \_/ \____/  \__,_|_| |_| |_|_| |_| |_|\__,_|_|___/\___|_|   
                                                                       
    ===============================================================
                        🎥 YouTube Transcript Saver
                           Made with ❤️  by SACHIN
    ===============================================================
    """)

def show_menu():
    print("\n" + "-" * 60)
    print("🎯 Main Menu".center(60))
    print("-" * 60)
    print("1. 📝 Save Video Transcript")
    print("2. 📋 View Previous Transcripts")
    print("3. ℹ️  About")
    print("4. ❌ Exit")
    print("-" * 60)

def show_about():
    print("\n" + "=" * 60)
    print("ℹ️  About".center(60))
    print("=" * 60)
    print("""
This YouTube Transcript Saver helps you to:
• Extract video transcripts from YouTube videos
• Save transcripts as text files
• Organize transcripts by video name
• View saved transcripts easily

Features:
• Simple and easy to use interface
• Support for English captions
• Automatic file naming
• Clean transcript formatting

Usage Tips:
• Make sure videos have English captions enabled
• Video title will be used as filename
• Transcripts are saved in the 'Transcripts' folder
""")
    input("\nPress Enter to continue...")

def view_previous_transcripts():
    folder = "Transcripts"
    if not os.path.exists(folder) or not os.listdir(folder):
        print("\n❌ No saved transcripts found!")
        return
        
    print("\n" + "=" * 60)
    print("📋 Saved Transcripts".center(60))
    print("=" * 60)
    
    files = sorted([f for f in os.listdir(folder) if f.endswith('.txt')], 
                  key=lambda x: os.path.getmtime(os.path.join(folder, x)), 
                  reverse=True)
    
    for i, file in enumerate(files, 1):
        print(f"\n{i}. {os.path.splitext(file)[0]}")
        print(f"   📅 {datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(folder, file))).strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\nEnter the number of the transcript to view (or press Enter to go back)")
    choice = input("Choice: ").strip()
    
    if choice.isdigit() and 1 <= int(choice) <= len(files):
        idx = int(choice) - 1
        with open(os.path.join(folder, files[idx]), 'r', encoding='utf-8') as f:
            print("\n" + "=" * 60)
            print(f.read())
            print("=" * 60)
        input("\nPress Enter to continue...")

def get_video_id(url):
    """Extract video ID from YouTube URL"""
    try:
        if 'youtube.com' in url:
            video_id = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
            if video_id:
                return video_id.group(1)
        elif 'youtu.be' in url:
            return url.split('/')[-1].split('?')[0]
    except Exception:
        return None
    return None

def get_video_info(url):
    """Get basic video information"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', 'Unknown Title'),
                'author': info.get('uploader', 'Unknown Author')
            }
    except Exception as e:
        print("\n❌ Error: Could not fetch video information.")
        return None

def get_transcript(video_id):
    """Get video transcript with language selection"""
    try:
        # Get list of available transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        print("\n📃 Available transcripts:")
        available_languages = []
        
        # Try to list all available transcripts
        try:
            for transcript in transcript_list:
                lang_code = transcript.language_code
                lang_name = transcript.language
                is_generated = transcript.is_generated
                # Only show English and Hindi options
                if lang_code in ['en', 'hi']:
                    available_languages.append((lang_code, lang_name, is_generated))
                    print(f"  • {lang_name} ({lang_code}) {'🤖 (Auto-generated)' if is_generated else '✨ (Manual)'}")
        except Exception as e:
            print("  • Could not list all transcripts")
            return None

        if not available_languages:
            print("\n❌ No English or Hindi captions available for this video.")
            return None

        # Ask user to select language
        print("\nSelect language:")
        for i, (code, name, _) in enumerate(available_languages, 1):
            print(f"{i}. {name} ({code})")
        
        while True:
            choice = input("\nEnter number (or press Enter to go back): ").strip()
            if not choice:
                return None
            if choice.isdigit() and 1 <= int(choice) <= len(available_languages):
                selected_lang = available_languages[int(choice)-1][0]
                break
            print("❌ Invalid choice. Please try again.")

        try:
            # Try direct transcript fetch first
            try:
                transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=[selected_lang])
                print(f"\n✅ Using {dict(available_languages)[selected_lang]} transcript!")
            except Exception:
                # If direct fetch fails, try with transcript object
                transcript = transcript_list.find_transcript([selected_lang])
                if transcript:
                    print(f"\n✅ Using {transcript.language} transcript!")
                    # For auto-generated transcripts, try getting translated version
                    if transcript.is_generated and selected_lang != 'en':
                        try:
                            transcript = transcript.translate('en')  # Translate to English first
                            transcript = transcript.translate(selected_lang)  # Then to target language
                        except Exception:
                            pass
                    transcript_data = transcript.fetch()
                else:
                    print(f"\n❌ Could not get transcript in selected language.")
                    return None

            # Process transcript data
            transcript_text = []
            for entry in transcript_data:
                if isinstance(entry, dict):
                    if 'text' in entry:
                        transcript_text.append(entry['text'].strip())
                elif hasattr(entry, 'text'):
                    transcript_text.append(entry.text.strip())
                
            if not transcript_text:
                print("\n❌ No text found in transcript.")
                return None
                
            return ' '.join(text for text in transcript_text if text)

        except Exception as e:
            print(f"\n❌ Error processing transcript: {str(e)}")
            if "Translation failed" in str(e):
                print("💡 Tip: Could not translate the transcript. Try another language.")
            elif "Transcript unavailable" in str(e):
                print("💡 Tip: This transcript might not be available anymore.")
            return None

    except Exception as e:
        print(f"\n❌ Error accessing transcripts: {str(e)}")
        if "Subtitles are disabled for this video" in str(e):
            print("💡 Tip: This video doesn't have any captions/subtitles enabled.")
        elif "Video unavailable" in str(e):
            print("💡 Tip: Make sure the video is publicly available and not private/deleted.")
        else:
            print("💡 Tip: Try another video that has captions/subtitles enabled.")
        return None

def save_transcript(title, transcript, url, language):
    """Save the transcript to a text file"""
    try:
        # Clean the title to make it filesystem-friendly
        clean_title = re.sub(r'[<>:"/\\|?*]', '_', title)
        
        # Create Transcripts folder if it doesn't exist
        if not os.path.exists("Transcripts"):
            os.makedirs("Transcripts")
        
        # Save file with language code
        filename = os.path.join("Transcripts", f"{clean_title}_{language}.txt")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("YouTube Video Transcript\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Title: {title}\n")
            f.write(f"URL: {url}\n")
            f.write(f"Language: {language}\n")
            f.write(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("\n" + "=" * 60 + "\n")
            f.write("TRANSCRIPT\n")
            f.write("=" * 60 + "\n\n")
            f.write(transcript)
        
        return filename
    except Exception as e:
        print(f"\n❌ Error saving file: {str(e)}")
        return None

def process_video():
    while True:
        print("\n" + "-" * 60)
        url = input("🔗 Enter YouTube URL (or press Enter to go back): ").strip()
        
        if not url:
            return
            
        video_id = get_video_id(url)
        if not video_id:
            print("\n❌ Invalid YouTube URL! Please enter a valid YouTube URL.")
            continue
            
        print("\n⏳ Getting video information...")
        video_info = get_video_info(url)
        if not video_info:
            continue
            
        print(f"\n📺 Processing: {video_info['title']}")
        print(f"👤 Channel: {video_info['author']}")
        
        print("\n⏳ Checking for available transcripts...")
        transcript = get_transcript(video_id)
        
        if transcript is None:
            continue

        # Get the selected language from transcript list
        selected_lang = None
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            for t in transcript_list:
                if t.language_code in ['en', 'hi']:
                    selected_lang = t.language_code
                    break
        except:
            selected_lang = 'en'  # default to English if can't determine

        filename = save_transcript(video_info['title'], transcript, url, selected_lang)
        if filename:
            print(f"\n✅ Transcript saved successfully!")
            print(f"📄 File location: {os.path.abspath(filename)}")
            
            print("\nWould you like to view the transcript now? (y/n)")
            if input().lower().startswith('y'):
                with open(filename, 'r', encoding='utf-8') as f:
                    print("\n" + "=" * 60)
                    print(f.read())
                    print("=" * 60)
                input("\nPress Enter to continue...")
        return

def main():
    print_header()
    
    while True:
        show_menu()
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            process_video()
        elif choice == '2':
            view_previous_transcripts()
        elif choice == '3':
            show_about()
        elif choice == '4':
            print("\n👋 Thank you for using YouTube Transcript Saver!")
            break
        else:
            print("\n❌ Invalid choice! Please try again.")

if __name__ == "__main__":
    main() 