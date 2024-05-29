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
    start_time = random.uniform(0, video.duration - audio_duration)
    end_time = start_time + audio_duration
    return video.subclip(start_time, end_time)

def export_final_video(final_clip, output_path):
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
    script = "I never expected to come home early from work and find my boyfriend in bed with my best friend. Hi everyone, I need some serious advice. A few days ago, I decided to surprise my boyfriend by coming home early from work. We've been together for three years, and I was thinking about taking our relationship to the next level. But as soon as I walked through the door, I heard laughter coming from our bedroom. My heart sank when I opened the door and found my boyfriend in bed with my best friend. I felt like my world had crumbled. They both looked at me, completely shocked, and I could barely process what was happening. I ran out of the house, not knowing what to do. Now, I’m stuck in this whirlwind of emotions. I feel betrayed by two people I trusted the most. I haven’t spoken to either of them since, but they've been blowing up my phone with apologies. Should I hear them out, or is it better to just cut them off completely and move on with my life? I feel so lost and hurt right now. Any advice would be greatly appreciated."

    video_path = "parkour.mp4"
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