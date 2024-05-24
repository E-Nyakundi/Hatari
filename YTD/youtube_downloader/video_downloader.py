import os
import logging
import re
import requests
from pytube import Playlist, YouTube
from concurrent.futures import ThreadPoolExecutor
from datetime import time

logging.basicConfig(level=logging.INFO)

class VideoDownloader:
    def __init__(self, resume=False, audio_only=False, max_retries=5):
        self.resume = resume
        self.audio_only = audio_only
        self.max_retries = max_retries

    def sanitize_filename(self, title):
        sanitized_title = re.sub(r'[<>:"/\\|?*]', '', title)
        max_filename_length = 255
        if len(sanitized_title) > max_filename_length:
            sanitized_title = sanitized_title[:max_filename_length]
        return sanitized_title

    def download_video(self, video_url, selected_quality=None):
        try:
            video = YouTube(video_url)
            if selected_quality:
                video_stream = video.streams.filter(res=selected_quality).first()
            elif self.audio_only:
                video_stream = video.streams.filter(abr=selected_quality).first()
            else:
                video_stream = video.streams.get_highest_resolution()

        except Exception as e:
            logging.error(f"Error occurred while creating YouTube object for URL: {video_url}")
            logging.error(f"Error message: {str(e)}")
            return

        if video_stream is None:
            logging.warning(f"No compatible video stream found for video: {video.title}.")
            return

        logging.info(f"Downloading: {video.title}")

        sanitized_title = self.sanitize_filename(video.title)

        retries = 0
        while retries <= self.max_retries:
            try:
                response = requests.head(video_url)
                if response.status_code == 410:
                    logging.warning(f"Video: {video.title} is no longer available (410 Gone). Skipping download.")
                    return

                # Define download path
                download_path = os.path.join(os.path.expanduser('~'), 'Downloads')
                output_filename = os.path.join(download_path, sanitized_title)

                if self.resume and os.path.isfile(output_filename):
                    logging.info(f"Video '{video.title}' already exists in the output directory. Skipping download.")
                    return

                video_stream.download(output_path=download_path, filename=sanitized_title + ".mp4", skip_existing=self.resume)
                return output_filename

            except Exception as e:
                logging.error(f"Error occurred while downloading: {video.title}")
                logging.error(f"Error message: {str(e)}")

                retries += 1
                logging.info(f"Retrying download for video: {video.title} (Retry {retries}/{self.max_retries})")
                delay = 5 * retries
                time.sleep(delay)

        if retries > self.max_retries:
            logging.warning(f"Max retries reached for video: {video.title}. Skipping download.")
            return None

    def download_playlist(self, playlist_url, selected_quality=None):
        try:
            playlist = Playlist(playlist_url)
            playlist._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")

            logging.info(f"Number of videos in playlist: {len(playlist.video_urls)}")

            downloaded_files = []

            with ThreadPoolExecutor() as executor:
                futures = []
                for video_url in playlist.video_urls:
                    future = executor.submit(self.download_video, video_url, selected_quality)
                    futures.append(future)

                for future in futures:
                    result = future.result()
                    if result:
                        downloaded_files.append(result)

            logging.info("Playlist download completed.")
            return downloaded_files

        except Exception as e:
            logging.error(f"Error occurred while processing playlist: {playlist_url}")
            logging.error(f"Error message: {str(e)}")
            return None
        
class VideoDetailsFetcher:
    @staticmethod
    def get_video_details(video_url):
        video = YouTube(video_url)
        return {
            'title': video.title,
            'thumbnail_url': video.thumbnail_url,
            'description': video.description,
            'metadata': video.metadata,
            'streams': video.streams,
        }

    @staticmethod
    def get_playlist_details(playlist_url):
        try:
            playlist = Playlist(playlist_url)
            if not playlist.video_urls:  # Check if there are any videos in the playlist
                print('No video URLs found in the playlist.')
                return None

            first_video_url = playlist.video_urls[0]
            first_video = YouTube(first_video_url)

            playlist_details = {
                'title': playlist.title,
                'thumbnail_url': first_video.thumbnail_url,
                'description': playlist.description,
                'metadata': first_video.metadata,
                'videos': []
            }
            try:
                print(playlist_details)
            except Exception as e:
                print(f"Error occurred while printing playlist details: {str(e)}")
                
            for s_video in playlist.video_urls:
                try:
                    video = YouTube(s_video)
                except Exception as e:
                    print(f"Error occurred while creating YouTube object for URL: {s_video}")
                    print(f"Error message: {str(e)}")
                    continue
                video_details = {
                    'title': video.title,
                    'thumbnail_url': video.thumbnail_url,
                    'description': video.description,
                    'metadata': video.metadata,
                    'streams': video.streams,
                }
                try:
                    playlist_details['videos'].append(video_details)
                except Exception as e:
                    print(f"Error occurred while appending video details: {str(e)}")
            return playlist_details

        except Exception as e:
            logging.error(f"Error occurred while getting playlist details: {str(e)}")
            return None




