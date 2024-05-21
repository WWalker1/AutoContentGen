from gtts import gTTS
from moviepy.editor import *
import random
from reddit_video_creator import pull_posts
from reddit_video_creator import VideoTranscriber

def generate_tts_audio(script, output_path):
    tts = gTTS(text=script, lang='en')
    tts.save(output_path)
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
    posts = pull_posts(subreddit, 10)

    #script = posts.iloc[2]["Body"]
    script = "here is a great script that will be used for testing. I'll put -- a pause -- and a ... terrifying word to test fully. Cool! all done now."
    video_path = "video.mp4"
    output_path = "output_video.mp4"

    audio_path = "tts_audio.mp3"
    audio_clip = generate_tts_audio(script, audio_path)
    video_clip = load_video_clip(video_path, audio_clip.duration)

    video_with_audio = video_clip.set_audio(audio_clip)
    export_final_video(video_with_audio, output_path)

    # Whisper force alignment
    model_path = "base"
    transcriber = VideoTranscriber(model_path, output_path)
    transcriber.extract_audio()
    transcriber.transcribe_video()
    transcriber.create_video("final_output.mp4")