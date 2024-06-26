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
from pydub import AudioSegment
import numpy as np 
import io 

os.environ['RUBBERBAND'] = r'C:\Users\22wes\Downloads\rubberband-3.3.0-gpl-executable-windows\rubberband-3.3.0-gpl-executable-windows\rubberband.exe'
# run each session: $env:PATH += ";C:\Users\22wes\Downloads\rubberband-3.3.0-gpl-executable-windows\rubberband-3.3.0-gpl-executable-windows"

def generate_tts_audio(script, output_path, xi_api_key):
    url = "https://api.elevenlabs.io/v1/text-to-speech/t0vOBj9vM05sKhNrB81C"
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

    # Convert to AudioSegment
    audio = AudioSegment.from_mp3(io.BytesIO(response.content))

    # Convert to numpy array for noise reduction
    samples = np.array(audio.get_array_of_samples())
    
    # Ensure the array is float32 and scaled to [-1, 1]
    samples = samples.astype(np.float32) / np.iinfo(samples.dtype).max

    # Apply noise reduction
    reduced_noise_audio = nr.reduce_noise(y=samples, sr=audio.frame_rate)

    # Scale back to int16 range
    reduced_noise_audio = (reduced_noise_audio * np.iinfo(np.int16).max).astype(np.int16)

    # Convert back to AudioSegment
    reduced_audio = AudioSegment(
        reduced_noise_audio.tobytes(),
        frame_rate=audio.frame_rate,
        sample_width=reduced_noise_audio.dtype.itemsize,
        channels=audio.channels
    )

    # Export as MP3
    reduced_audio.export(output_path, format="mp3")

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

    title = "I (22M) surprise visited girlfriend (22F) and walked in on her watching TV in bed with her guy friend. What should I do?"
    script = "Yesterday I wanted to surprise my girlfriend a day early because she was having a rough week with things. I showed up unannounced and walked in on her laying on the bed with one of her guy friends. They were both fully clothed and not cuddling in bed, but the lights were off in the room with the door slightly shut. This was upsetting to me and I am not sure what to do. She assures me that they did nothing together and she would never do anything like that. She felt really remorseful last night and was crying begging me to stay. The whole thing threw me off and really was unsettling for me. She told me that he came over to talk about the problems she was having this week and then they started watching TV after. We were supposed to call before bed 30 minutes after I showed up because she thought I was at home. She never told me she was having him over or anything and swears that she would have told me when we called to say goodnight. I am sorry if I ranted, but this is still fresh in my head. Thanks. Edit: When asked why she did it and didn’t think of me, she told me that it was because she wasn’t thinking with everything going on this week (stress, friends issues, etc). She also thought that it would have been ok because she sees him as nothing more than a friend and she “doesn’t see him like that"


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
    
    # Eleven Labs API integration with speed parameter
    speed = 1.2  # Adjust this value to change the speed (e.g., 1.2 for 20% faster)
    transcriber = VideoTranscriber(output_path, XI_API_KEY, font_path=font_path, speed=speed)
    transcriber.transcribe_video(script, title=title)
    transcriber.create_video("final_output_1.2x.mp4", title_image_path=title_image_path)