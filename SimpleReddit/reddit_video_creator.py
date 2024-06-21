import praw
import pandas as pd
import os
import shutil
import cv2
from moviepy.editor import ImageSequenceClip, AudioFileClip, VideoFileClip
from tqdm import tqdm
import base64, json, requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont
'''
Params: 
1. subreddit -> subreddit that it will pull posts from
2. num_posts -> the number of posts that the function will retrieve
Returns: dataframe of the hottest posts from the subreddit
'''
def pull_posts(subreddit_name, num_posts): 

    # Initialize the Reddit instance
    reddit = praw.Reddit(client_id='VkuHzBrorLCQGKh3gOnKdA',
                        client_secret='MmXgUMTPjtJtKJqyGUhkqaPyIC3NgA',
                        user_agent='Platform:YTshorts:1.0 by Weston Walker')

    # Specify the subreddit you want to scrape
    subreddit = reddit.subreddit(subreddit_name)

    # Initialize lists to store the data
    data = []

    # Retrieve the posts from the subreddit
    for post in subreddit.hot(limit=num_posts):  # Adjust the limit as needed
        if (len(post.selftext) > 10):
            data.append({"Title": post.title, "Body": post.selftext})

    # Create a Pandas DataFrame
    df = pd.DataFrame(data)
    return df


print(pull_posts("relationship_advice", 10).iloc[0])

FONT_SIZE = 50
FONT_COLOR = (255, 255, 255)  # White color
OUTLINE_COLOR = (0, 0, 0)  # Black color
OUTLINE_THICKNESS = 5
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 1.0
FONT_THICKNESS = 3
TEXT_COLOR = (255, 255, 255)  # White color
OUTLINE_COLOR = (0, 0, 0)  # Black color
OUTLINE_THICKNESS = 5

class VideoTranscriber:
    def __init__(self, video_path, xi_api_key, font_path=None):
        self.video_path = video_path
        self.audio_path = os.path.join(os.path.dirname(self.video_path), "tts_audio.mp3")
        self.text_array = []
        self.title_text_array = []
        self.fps = 0
        self.xi_api_key = xi_api_key
        self.font = ImageFont.truetype(font_path, FONT_SIZE) if font_path and os.path.exists(font_path) else None

    def transcribe_video(self, script, title=None):
        print('Generating audio with Eleven Labs API')
        full_script = title + ". " + script if title else script

        url = f"https://api.elevenlabs.io/v1/text-to-speech/UeoNuANTaFCbgahlkXH8/with-timestamps"
        headers = {
            "Content-Type": "application/json",
            "xi-api-key": self.xi_api_key
        }
        data = {
            "text": full_script,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            } 
        }

        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()

        response_dict = response.json()
        audio_bytes = base64.b64decode(response_dict["audio_base64"])
        with open(self.audio_path, 'wb') as f:
            f.write(audio_bytes)

        words = response_dict['alignment']['characters']
        start_times = response_dict['alignment']['character_start_times_seconds']
        end_times = response_dict['alignment']['character_end_times_seconds']

        video = cv2.VideoCapture(self.video_path)
        self.fps = video.get(cv2.CAP_PROP_FPS)
        video.release()

        title_end_index = len(title) + 1 if title else 0  # +1 for the period
        self.title_text_array = self.process_text(words[:title_end_index], start_times[:title_end_index], end_times[:title_end_index])
        self.text_array = self.process_text(words[title_end_index:], start_times[title_end_index:], end_times[title_end_index:])
        print('Audio generation complete')

    def process_text(self, words, start_times, end_times):
        text_array = []
        current_word = ""
        start_time = 0
        for i in range(len(words)):
            if words[i] == " ":
                if current_word:
                    end_time = end_times[i]
                    text_array.append([current_word.strip(), int(start_time * self.fps), int(end_time * self.fps)])
                    current_word = ""
            else:
                if not current_word:
                    start_time = start_times[i]
                current_word += words[i]

        if current_word:
            end_time = end_times[-1]
            text_array.append([current_word.strip(), int(start_time * self.fps), int(end_time * self.fps)])
        return text_array

    def draw_text_with_outline(self, frame, text, x, y):
        img_pil = Image.fromarray(frame)
        draw = ImageDraw.Draw(img_pil)

        # Draw outline
        for offset in range(-OUTLINE_THICKNESS, OUTLINE_THICKNESS + 1):
            for offset2 in range(-OUTLINE_THICKNESS, OUTLINE_THICKNESS + 1):
                draw.text((x + offset, y + offset2), text, font=self.font, fill=OUTLINE_COLOR)

        # Draw text
        draw.text((x, y), text, font=self.font, fill=FONT_COLOR)

        return np.array(img_pil)

    def extract_frames(self, output_folder, title_image_path=None):
        print('Extracting frames')
        cap = cv2.VideoCapture(self.video_path)
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        N_frames = 0

        title_image = None
        if title_image_path and os.path.exists(title_image_path):
            # Read the image with PIL to preserve alpha channel
            title_image = Image.open(title_image_path).convert('RGBA')
            # Resize title image to fit the frame with a small margin
            img_width, img_height = title_image.size
            aspect_ratio = img_width / img_height
            margin = 50  # pixels of margin on each side
            if aspect_ratio > frame_width / frame_height:
                new_width = frame_width - 2 * margin
                new_height = int(new_width / aspect_ratio)
            else:
                new_height = frame_height - 2 * margin
                new_width = int(new_height * aspect_ratio)
            title_image = title_image.resize((new_width, new_height), Image.LANCZOS)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if title_image is not None and N_frames <= self.title_text_array[-1][2]:
                # Convert frame to PIL Image
                frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

                # Center the title image on the frame
                y_offset = (frame_height - title_image.size[1]) // 2
                x_offset = (frame_width - title_image.size[0]) // 2

                # Paste the title image onto the frame, using the alpha channel as mask
                frame_pil.paste(title_image, (x_offset, y_offset), title_image)

                # Convert back to OpenCV format
                frame = cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)
            else:
                for i in self.text_array:
                    if N_frames >= i[1] and N_frames <= i[2]:
                        text = i[0]
                        if self.font:
                            bbox = self.font.getbbox(text)
                            text_width = bbox[2] - bbox[0]
                            text_height = bbox[3] - bbox[1]
                        else:
                            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE, FONT_THICKNESS)[0]
                            text_width, text_height = text_size

                        text_x = int((frame_width - text_width) / 2)
                        text_y = int(frame_height / 2 + text_height / 2)

                        if self.font:
                            frame = self.draw_text_with_outline(frame, text, text_x, text_y)
                        else:
                            for j in range(OUTLINE_THICKNESS):
                                cv2.putText(frame, text, (text_x-j, text_y), cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE, OUTLINE_COLOR, FONT_THICKNESS)
                                cv2.putText(frame, text, (text_x+j, text_y), cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE, OUTLINE_COLOR, FONT_THICKNESS)
                                cv2.putText(frame, text, (text_x, text_y-j), cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE, OUTLINE_COLOR, FONT_THICKNESS)
                                cv2.putText(frame, text, (text_x, text_y+j), cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE, OUTLINE_COLOR, FONT_THICKNESS)

                            cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE, TEXT_COLOR, FONT_THICKNESS)
                        break

            cv2.imwrite(os.path.join(output_folder, str(N_frames) + ".jpg"), frame)
            N_frames += 1

        cap.release()
        print('Frames extracted')
        

    def create_video(self, output_video_path, title_image_path=None):
        print('Creating video')
        image_folder = os.path.join(os.path.dirname(self.video_path), "frames") 
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)
        
        self.extract_frames(image_folder, title_image_path)
        
        images = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]
        images.sort(key=lambda x: int(x.split(".")[0]))
        
        original_video = VideoFileClip(self.video_path)
        original_fps = original_video.fps
        
        clip = ImageSequenceClip([os.path.join(image_folder, image) for image in images], fps=original_fps)
        audio = AudioFileClip(self.audio_path)
        
        video_duration = audio.duration
        clip = clip.subclip(0, video_duration)
        
        clip = clip.set_audio(audio)
        clip.write_videofile(output_video_path, fps=original_fps)

        if os.path.exists(image_folder):
            shutil.rmtree(image_folder)
            print(f"Folder '{image_folder}' has been deleted successfully.")
        else:
            print(f"Folder '{image_folder}' does not exist.")
