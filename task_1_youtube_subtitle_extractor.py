import os
import re
from googleapiclient.discovery import build
from datetime import timedelta
 # Installs the yt-dlp package.
import yt_dlp


API_KEY = "AIzaSyBtRMQnNQ3XwlCbS1i4td5r3qDd40WeA10"
CHANNEL_ID = "UC_HK0fs_YyxhvkkiPoL_w6A"

# Initialize YouTube API
youtube = build("youtube", "v3", developerKey=API_KEY)

# Function to get video IDs from a YouTube channel
def get_video_ids(channel_id):
    video_ids = []
    next_page_token = None

    while True:
        # Fetch playlist items (uploads)
        response = youtube.search().list(
            part="id",
            channelId=channel_id,
            maxResults=50,
            pageToken=next_page_token,
            type="video"
        ).execute()

        # Collect video IDs
        for item in response.get("items", []):
            video_ids.append(item["id"]["videoId"])

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return video_ids

# Function to convert ISO 8601 duration to seconds
def parse_duration(duration):
    match = re.match(
        r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?",
        duration
    )
    if not match:
        return 0

    hours, minutes, seconds = match.groups()
    delta = timedelta(
        hours=int(hours) if hours else 0,
        minutes=int(minutes) if minutes else 0,
        seconds=int(seconds) if seconds else 0,
    )
    return int(delta.total_seconds())

# Function to filter videos longer than 5 minutes
def get_video_durations(video_ids):
    long_videos = []
    for i in range(0, len(video_ids), 50):
        # Fetch video details
        response = youtube.videos().list(
            part="contentDetails",
            id=",".join(video_ids[i:i+50])
        ).execute()

        for item in response["items"]:
            duration = item["contentDetails"]["duration"]

            # Convert ISO 8601 duration to seconds
            seconds = parse_duration(duration)
            if seconds > 300:  # 300 seconds = 5 minutes
                long_videos.append(f"https://www.youtube.com/watch?v={item['id']}")

    return long_videos

# Function to download subtitles
def download_subtitles(video_urls, download_folder):
    os.makedirs(download_folder, exist_ok=True)

    # Create yt-dlp options for subtitles
    ydl_opts = {
        'writeautomaticsub': True,  # Download auto-generated subtitles if available
        'writesubtitles': True,     # Download subtitles if available
        'subtitleslangs': ['en'],   # Download subtitles in English
        'skip_download': True,      # Skip the video download, only download subtitles
        'outtmpl': f'{download_folder}/%(id)s.%(ext)s'  # Save subtitles with video ID as filename
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for url in video_urls:
            try:
                print(f"Downloading subtitles for {url}...")
                ydl.download([url])
            except Exception as e:
                print(f"Error downloading subtitles for {url}: {e}")

# Main flow
def main():
    # Get video IDs from the channel
    video_ids = get_video_ids(CHANNEL_ID)
    print(f"Found {len(video_ids)} videos on the channel.")

    # Filter out videos longer than 5 minutes
    long_videos = get_video_durations(video_ids)
    print(f"Found {len(long_videos)} videos longer than 5 minutes.")

    # Specify the folder to save subtitles locally
    download_folder = "/content/drive/MyDrive/Downloads/subtitles"

    # Download subtitles for videos longer than 5 minutes
    download_subtitles(long_videos, download_folder)
    print(f"Subtitles downloaded to {download_folder}")

# Run the script
main()






import os

# Directory where .vtt files are saved
vtt_folder = "/content/drive/MyDrive/Downloads/subtitles"
# New folder to store .txt files
txt_folder = "/content/drive/MyDrive/Downloads/text_subtitles"
os.makedirs(txt_folder, exist_ok=True)

# Function to convert .vtt to .txt
def convert_vtt_to_txt(vtt_folder, txt_folder):
    # Iterate over all .vtt files in the vtt_folder
    for filename in os.listdir(vtt_folder):
        if filename.endswith(".vtt"):
            vtt_path = os.path.join(vtt_folder, filename)

            # Read the .vtt file content
            with open(vtt_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            # Extract subtitle text (ignoring timestamps and metadata)
            subtitle_text = []
            for line in lines:
                if "-->" not in line:  # Ignore timestamps
                    subtitle_text.append(line.strip())

            # Combine all text and save to a .txt file
            txt_filename = filename.replace(".vtt", ".txt")
            txt_path = os.path.join(txt_folder, txt_filename)

            with open(txt_path, "w", encoding="utf-8") as file:
                file.write("\n".join(subtitle_text))

            print(f"Converted {filename} to {txt_filename}")

# Run the conversion
convert_vtt_to_txt(vtt_folder, txt_folder)
print(f"Subtitles converted to text and saved in {txt_folder}")





import shutil
from google.colab import files

# Path to the folder to download
folder_to_download = "/content/drive/MyDrive/Downloads/subtitles"
# Path to the output zip file
zip_path = "/content/subtitles.zip"

# Zip the folder
shutil.make_archive(zip_path.replace(".zip", ""), 'zip', folder_to_download)

# Download the zip file
files.download(zip_path)

print(f"The folder has been zipped and is ready for download: {zip_path}")
