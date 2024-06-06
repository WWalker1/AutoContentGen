import os
from audio_generator import AudioGenerator
from video_selector import VideoSelector
from title_screen import TitleScreen
from subtitle_generator import SubtitleGenerator
from video_composer import VideoComposer

XI_API_KEY = "a56e9c8f7a8ffe64d28b0069fc30ca22"  # Replace with your actual API key
VIDEO_FOLDER = "background_videos"  # Replace with your video folder path
TEMPLATE_PATH = "anonymous_reddit_template.png"  # Replace with your template image path

def main():
    # Initialize components
    audio_gen = AudioGenerator(XI_API_KEY)
    video_sel = VideoSelector(VIDEO_FOLDER)
    title_screen = TitleScreen(TEMPLATE_PATH)

    subtitle_gen = SubtitleGenerator(XI_API_KEY) # has default font, but can change if needed
    composer = VideoComposer(audio_gen, video_sel, title_screen, subtitle_gen)

    # Example usage
    title = "My girlfriend wants to break up"
    content = """Now a regular sentence. This shouldn't be too bad. Let's see. extra"""

    output_path = "minecraft_dilemma.mp4"
    composer.create_video(title, content, output_path)

if __name__ == "__main__":
    main()