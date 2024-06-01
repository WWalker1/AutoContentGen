import praw
import pandas as pd
import whisper
import os
import shutil
import cv2
from moviepy.editor import ImageSequenceClip, AudioFileClip, VideoFileClip
from tqdm import tqdm
import base64, json, requests 
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



FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 1.0
FONT_THICKNESS = 3
TEXT_COLOR = (255, 255, 255)  # White color
OUTLINE_COLOR = (0, 0, 0)  # Black color
OUTLINE_THICKNESS = 5

class VideoTranscriber:
    def __init__(self, video_path, xi_api_key):
        self.video_path = video_path
        self.audio_path = os.path.join(os.path.dirname(self.video_path), "tts_audio.mp3")
        self.text_array = []
        self.fps = 0
        self.char_width = 0
        self.xi_api_key = xi_api_key

    def transcribe_video(self, script):
        print('Generating audio with Eleven Labs API')
        url = f"https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM/with-timestamps"
        headers = {
            "Content-Type": "application/json",
            "xi-api-key": self.xi_api_key
        }
        data = {
            "text": script,
            "model_id": "eleven_multilingual_v1",
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

        end_times = response_dict['alignment']['character_end_times_seconds']
        audio_duration = end_times[-1]  # Get the end time of the last character
        self.fps = len(end_times) / audio_duration
        video = cv2.VideoCapture(self.video_path)
        self.fps = video.get(cv2.CAP_PROP_FPS)
        video.release()

        self.text_array = []
        words = response_dict['alignment']['characters']
        start_times = response_dict['alignment']['character_start_times_seconds']

        current_word = ""
        start_time = 0
        for i in range(len(words)):
            if words[i] == " ":
                if current_word:
                    end_time = end_times[i]
                    self.text_array.append([current_word.strip(), int(start_time * self.fps), int(end_time * self.fps)])
                    current_word = ""
            else:
                if not current_word:
                    start_time = start_times[i]
                current_word += words[i]

        if current_word:
            end_time = end_times[-1]
            self.text_array.append([current_word.strip(), int(start_time * self.fps), int(end_time * self.fps)])

        print('Audio generation complete')

    def extract_audio(self):
        print('Extracting audio')
        audio_path = os.path.join(os.path.dirname(self.video_path), "audio.mp3")
        video = VideoFileClip(self.video_path)
        audio = video.audio 
        audio.write_audiofile(audio_path)
        self.audio_path = audio_path
        print('Audio extracted')
    
    def extract_frames(self, output_folder):
        print('Extracting frames')
        cap = cv2.VideoCapture(self.video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        asp = width / height
        N_frames = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = frame[:, int(int(width - 1 / asp * height) / 2):width - int((width - 1 / asp * height) / 2)]
            
            for i in self.text_array:
                if N_frames >= i[1] and N_frames <= i[2]:
                    text = i[0]
                    text_size, _ = cv2.getTextSize(text, FONT, FONT_SCALE, FONT_THICKNESS)
                    text_x = int((frame.shape[1] - text_size[0]) / 2)
                    text_y = int(height/2)
                    
                    # Add black outline
                    for j in range(OUTLINE_THICKNESS):
                        cv2.putText(frame, text, (text_x-j, text_y), FONT, FONT_SCALE, OUTLINE_COLOR, FONT_THICKNESS)
                        cv2.putText(frame, text, (text_x+j, text_y), FONT, FONT_SCALE, OUTLINE_COLOR, FONT_THICKNESS)
                        cv2.putText(frame, text, (text_x, text_y-j), FONT, FONT_SCALE, OUTLINE_COLOR, FONT_THICKNESS)
                        cv2.putText(frame, text, (text_x, text_y+j), FONT, FONT_SCALE, OUTLINE_COLOR, FONT_THICKNESS)
                    
                    # Add white text
                    cv2.putText(frame, text, (text_x, text_y), FONT, FONT_SCALE, TEXT_COLOR, FONT_THICKNESS)
                    break
            
            cv2.imwrite(os.path.join(output_folder, str(N_frames) + ".jpg"), frame)
            N_frames += 1
        
        cap.release()
        print('Frames extracted')

    def create_video(self, output_video_path):
        print('Creating video')
        image_folder = os.path.join(os.path.dirname(self.video_path), "frames") 
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)
        
        self.extract_frames(image_folder)
        
        images = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]
        images.sort(key=lambda x: int(x.split(".")[0]))
        
        frame = cv2.imread(os.path.join(image_folder, images[0]))
        height, width, layers = frame.shape
        
        # Get the frame rate of the original video
        original_video = VideoFileClip(self.video_path)
        original_fps = original_video.fps
        
        clip = ImageSequenceClip([os.path.join(image_folder, image) for image in images], fps=original_fps)
        audio = AudioFileClip(self.audio_path)
        
        # Trim the video to match the audio duration
        video_duration = audio.duration
        clip = clip.subclip(0, video_duration)
        
        clip = clip.set_audio(audio)
        clip.write_videofile(output_video_path, fps=original_fps)
        shutil.rmtree(image_folder)