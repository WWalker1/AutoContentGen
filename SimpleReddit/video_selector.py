import os
import random
from moviepy.editor import VideoFileClip

class VideoSelector:
    def __init__(self, video_folder):
        self.video_folder = video_folder
        self.video_files = [f for f in os.listdir(video_folder) if f.endswith(('.mp4', '.avi', '.mov'))]

    def select_video(self, min_duration):
        suitable_videos = []
        for video_file in self.video_files:
            video_path = os.path.join(self.video_folder, video_file)
            video = VideoFileClip(video_path)
            if video.duration >= min_duration:
                suitable_videos.append(video_path)
            video.close()

        if not suitable_videos:
            raise ValueError(f"No videos in {self.video_folder} are long enough (min {min_duration} seconds)")

        return random.choice(suitable_videos)

    def trim_video(self, video_path, target_duration):
        video = VideoFileClip(video_path)
        if video.duration <= target_duration:
            return video
        else:
            start_time = random.uniform(0, video.duration - target_duration)
            end_time = start_time + target_duration
            return video.subclip(start_time, end_time)