import yt_dlp
import yt_dlp
from pathlib import Path

# Create the downloads folder if it doesn't exist
download_folder = Path("downloads")
download_folder.mkdir(exist_ok=True)

download_options = {
    "format": "bestaudio/best",
    "outtmpl": str(download_folder / "%(title)s.%(ext)s"),
    "noplaylist": True,
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "192",
    }],
}

print("===============================")
print("Welcome to Yt2mp3 Converter!")
print("Convert supported video URLs to MP3 audio.")
print("===============================")

video_url = input("Please enter the video URL: ").strip()

if not video_url:
    print("You did not enter a URL. Please try again.")
else:
    print("Your URL has been received. Processing...")

    try:
        with yt_dlp.YoutubeDL(download_options) as ydl:
            ydl.download([video_url])

        print("Download complete! Check the 'downloads' folder.")

    except Exception as error:
        print(f"Something went wrong: {error}")
