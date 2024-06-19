from gtts import gTTS
from moviepy.editor import *
import random
from reddit_video_creator import pull_posts
from reddit_video_creator import VideoTranscriber
import requests
import os 
import noisereduce as nr
import librosa
import soundfile as sf 

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

    # Apply noise reduction
    audio_data, sample_rate = librosa.load(output_path)
    reduced_noise_audio = nr.reduce_noise(y=audio_data, sr=sample_rate)

    # Save the reduced noise audio using soundfile
    sf.write(output_path, reduced_noise_audio, sample_rate)

    return AudioFileClip(output_path)

def load_video_clip(video_path, audio_duration):
       video = VideoFileClip(video_path)
       video_duration = min(video.duration, audio_duration)
       start_time = random.uniform(0, max(0, video.duration - video_duration - 5 ))  # 5 added as a buffer for the title 
       end_time = start_time + video_duration + 5 
       return video.subclip(start_time, end_time)

def export_final_video(final_clip, output_path):
    # Trim the video to match the audio duration
    audio_duration = final_clip.audio.duration
    video_duration = final_clip.duration
    
    final_clip.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac', audio_bitrate='192k')

def get_title_image_path(title, titles_folder):
    # Extract the first three words from the title
    first_three_words = " ".join(title.split()[:3])

    # Construct the title image path
    title_image_path = os.path.join(titles_folder, f"{first_three_words}.png")

    # Check if the title image file exists
    if os.path.isfile(title_image_path):
        return title_image_path
    else:
        return None

# Main script
if __name__ == '__main__':
    font_path = "fonts/Mont-HeavyDEMO.otf"  # Replace with your actual font file path
    subreddit = "relationship_advice"
    num_posts = 10
    #posts = pull_posts(subreddit, num_posts)

    print("Select a post to generate a video:")
    #for i, post in enumerate(posts.itertuples(index=False), start=1):
    #    print(f"{i}. {post.Title}")
    '''
    while True:
        try:
            selection = int(input("Enter the number of the post you want to use: "))
            if 1 <= selection <= num_posts:
                break
            else:
                print(f"Please enter a number between 1 and {num_posts}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    '''
    #selected_post = posts.iloc[selection - 1]
    #title = selected_post.Title
    #script = selected_post.Body

    title = "My Fiance's Shocking Double Life Revealed by a Stranger!"
    script = "I was living a fairytale with my fiancé until a stranger approached me at a coffee shop. She told me she knew my fiancé and that he was living a double life. At first, I didn’t believe her, but she showed me pictures and messages that proved her story. I confronted him, and he admitted everything. He had been engaged to another woman in a different city. My world fell apart. I broke off the engagement and moved out. It’s been a struggle, but I’m slowly rebuilding my life. Always be cautious and listen to warning signs."


    # Chooses the title image based on the first 3 words 
    titles_folder = "titles"
    title_image_path = get_title_image_path(title, titles_folder)

    video_path = "background_videos/parkour.mp4"
    output_path = "output_video.mp4"

    XI_API_KEY = "sk_6f0e1024ea2a95099009ae623d7a65b2795200969d95f2a1"
    
    audio_path = "tts_audio.mp3"
    full_script = title + ". " + script
    audio_clip = generate_tts_audio(full_script, audio_path, XI_API_KEY)
    video_clip = load_video_clip(video_path, audio_clip.duration)

    video_with_audio = video_clip.set_audio(audio_clip)
    export_final_video(video_with_audio, output_path)
    
    # Eleven Labs API integration
    transcriber = VideoTranscriber(output_path, XI_API_KEY, font_path=font_path)
    transcriber.transcribe_video(script, title=title)
    transcriber.create_video("final_output.mp4", title_image_path=title_image_path)