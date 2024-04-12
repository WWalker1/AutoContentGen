from gtts import gTTS
from moviepy.editor import *
from reddit_scraping import pull_posts
import random
import pandas as pd
from typing import List

def generate_tts_audio(script, output_path):
    tts = gTTS(text=script, lang='en')
    tts.save(output_path)
    return AudioFileClip(output_path)

def load_video_clip(video_path, audio_duration):
    video = VideoFileClip(video_path)
    start_time = random.uniform(0, video.duration - audio_duration)
    end_time = start_time + audio_duration
    return video.subclip(start_time, end_time)

def create_text_clips(phrases, durations, font='Arial', font_size=50, color='white'):
    text_clips = []
    for phrase, duration in zip(phrases, durations):
        text_clip = TextClip(phrase, fontsize=font_size, font=font, color=color)
        text_clip = text_clip.set_duration(duration)
        text_clips.append(text_clip)
    return text_clips

def animate_text_clips(text_clips, audio_duration, screen_size):
    animated_clips = []
    current_time = 0
    for clip in text_clips:
        animated_clip = clip.set_start(current_time).set_pos('center')
        animated_clips.append(animated_clip)
        current_time += clip.duration
    return animated_clips

def combine_video_and_text(video_clip, audio_clip, text_clips):
    video_with_text = CompositeVideoClip([video_clip] + text_clips)
    video_with_text = video_with_text.set_duration(audio_clip.duration)
    video_with_text = video_with_text.set_audio(audio_clip)
    return video_with_text

def export_final_video(final_clip, output_path):
    final_clip.write_videofile(output_path, fps=24, codec='libx264')

def split_into_phrases(words, max_words_per_phrase):
    phrases = []
    current_phrase = []
    for word in words:
        current_phrase.append(word)
        if len(current_phrase) == max_words_per_phrase:
            phrases.append(' '.join(current_phrase))
            current_phrase = []
    if current_phrase:
        phrases.append(' '.join(current_phrase))
    return phrases

def estimate_phrase_durations(phrases, audio_duration, words_per_minute=200):
    total_words = sum(len(phrase.split()) for phrase in phrases)
    words_per_second = words_per_minute / 60
    duration_per_word = 1 / words_per_second
    phrase_durations = [len(phrase.split()) * duration_per_word for phrase in phrases]
    total_duration = sum(phrase_durations)
    scale_factor = audio_duration / total_duration
    scaled_durations = [duration * scale_factor for duration in phrase_durations]
    return scaled_durations

# Main script
if __name__ == '__main__':
    subreddit = "relationship_advice"
    posts: pd.DataFrame = pull_posts(subreddit, 10)

    #script = posts.iloc[2]["Body"]
    script = "this is an example script. And. I hope that the video plays in time with the words"
    video_path = "Minecraft_speedrun_background.mp4"
    output_path = "output_video.mp4"
    max_words_per_phrase = 3

    words = script.split()
    phrases = split_into_phrases(words, max_words_per_phrase)
    audio_path = "tts_audio.mp3"
    audio_clip = generate_tts_audio(script, audio_path)
    video_clip = load_video_clip(video_path, audio_clip.duration)

    phrase_durations = estimate_phrase_durations(phrases, audio_clip.duration)
    text_clips = create_text_clips(phrases, phrase_durations)
    animated_clips = animate_text_clips(text_clips, audio_clip.duration, video_clip.size)

    final_clip = combine_video_and_text(video_clip, audio_clip, animated_clips)
    export_final_video(final_clip, output_path)