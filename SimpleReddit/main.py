from gtts import gTTS
from moviepy.editor import *
import random
from reddit_video_creator import pull_posts
from reddit_video_creator import VideoTranscriber
import requests

def generate_tts_audio(script, output_path, xi_api_key):
    url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": xi_api_key
    }
    data = {
        "text": script,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(response.content)

    return AudioFileClip(output_path)

def load_video_clip(video_path, audio_duration):
       video = VideoFileClip(video_path)
       video_duration = min(video.duration, audio_duration)
       start_time = random.uniform(0, max(0, video.duration - video_duration))
       end_time = start_time + video_duration
       return video.subclip(start_time, end_time)

def export_final_video(final_clip, output_path):
    # Trim the video to match the audio duration
    audio_duration = final_clip.audio.duration
    video_duration = final_clip.duration
    if video_duration > audio_duration:
        final_clip = final_clip.subclip(0, audio_duration)
    
    final_clip.write_videofile(output_path, fps=24, codec='libx264')


# Main script
if __name__ == '__main__':
    subreddit = "relationship_advice"
    num_posts = 10
    posts = pull_posts(subreddit, num_posts)

    print("Select a post to generate a video:")
    for i, post in enumerate(posts.itertuples(index=False), start=1):
        print(f"{i}. {post.Title}")

    while True:
        try:
            selection = int(input("Enter the number of the post you want to use: "))
            if 1 <= selection <= num_posts:
                break
            else:
                print(f"Please enter a number between 1 and {num_posts}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    selected_post = posts.iloc[selection - 1]
    '''TODO: still working on getting the title included
    title = selected_post.Title
    script = f"{title}\n\n{selected_post.Body}"
    script = f"{title} Hi there. Just doing some testing to save time"
    print(script)
    '''
    script = selected_post.Body
    script = "lotrs. of. periods. to see if the same. issue. is present. here...ok. cool, and, now done."

    video_path = "background_videos/parkour.mp4"
    output_path = "output_video.mp4"

    XI_API_KEY = "a56e9c8f7a8ffe64d28b0069fc30ca22"
    
    audio_path = "tts_audio.mp3"
    audio_clip = generate_tts_audio(script, audio_path, XI_API_KEY)
    video_clip = load_video_clip(video_path, audio_clip.duration)

    video_with_audio = video_clip.set_audio(audio_clip)
    export_final_video(video_with_audio, output_path)

    # Eleven Labs API integration
    transcriber = VideoTranscriber(output_path, XI_API_KEY)
    transcriber.transcribe_video(script)
    transcriber.create_video("final_output.mp4")