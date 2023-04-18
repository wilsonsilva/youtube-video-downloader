import threading
from pytube import YouTube
import os

# Read the URLs from the input file. It should contain one URL per line.
with open('video_urls.txt', 'r') as f:
    urls = [line.strip() for line in f.readlines()]

# Number of parallel downloads to run at the same time
NUMBER_OF_PARALLEL_DOWNLOADS = 4

# Number of retries for each download
MAX_DOWNLOAD_RETRIES = 3

# Create a semaphore with a value of NUMBER_OF_PARALLEL_DOWNLOADS
semaphore = threading.Semaphore(NUMBER_OF_PARALLEL_DOWNLOADS)


def download_video(url):
    # Acquire the semaphore before starting the download
    semaphore.acquire()

    # Inform the user that the download has started
    print(f"Downloading video from {url}")

    # Create a YouTube object
    youtube = YouTube(url)

    # Retry the download up to DOWNLOAD_RETRIES times if there's an error
    remaining_download_retries = MAX_DOWNLOAD_RETRIES
    while remaining_download_retries > 0:
        try:
            # Get the first available video stream with the highest resolution
            video = youtube.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

            # Skip downloaded videos
            if os.path.exists(video.default_filename):
                print(f"Video {video.default_filename} already exists. Skipping.")
                semaphore.release()
                return

            # Download the video
            video.download()
            break
        except KeyError as e:
            print(f"Error downloading video: {url} {e}. Retrying.")
            remaining_download_retries -= 1
        except Exception as e:
            print(f"Error downloading video: {video.default_filename} {e}. Retrying.")
            remaining_download_retries -= 1

    # Release the semaphore when the download is finished or retries have been exhausted
    semaphore.release()


# Create a thread for each video
threads = []
for url in urls:
    thread = threading.Thread(target=download_video, args=(url,))
    threads.append(thread)
    thread.start()

# Wait for all threads to finish
for thread in threads:
    thread.join()
