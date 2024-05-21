import praw
import pandas as pd
import whisper
import os
import shutil
import cv2
from moviepy.editor import ImageSequenceClip, AudioFileClip, VideoFileClip
from tqdm import tqdm

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
    def __init__(self, model_path, video_path):
        self.model = whisper.load_model(model_path)
        self.video_path = video_path
        self.audio_path = ''
        self.text_array = []
        self.fps = 0
        self.char_width = 0

    def transcribe_video(self):
        print('Transcribing video')
        result = self.model.transcribe(self.audio_path)
        text = result["segments"][0]["text"]
        textsize = cv2.getTextSize(text, FONT, FONT_SCALE, FONT_THICKNESS)[0]
        cap = cv2.VideoCapture(self.video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        asp = 16/9
        ret, frame = cap.read()
        width = frame[:, int(int(width - 1 / asp * height) / 2):width - int((width - 1 / asp * height) / 2)].shape[1]
        width = width - (width * 0.1)
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.char_width = int(textsize[0] / len(text))
        
        for j in tqdm(result["segments"]):
            lines = []
            text = j["text"]
            end = j["end"]
            start = j["start"]
            total_frames = int((end - start) * self.fps)
            start = start * self.fps
            total_chars = len(text)
            words = text.split(" ")
            i = 0
            
            while i < len(words):
                words[i] = words[i].strip()
                if words[i] == "":
                    i += 1
                    continue
                length_in_pixels = (len(words[i]) + 1) * self.char_width
                remaining_pixels = width - length_in_pixels
                line = words[i] 
                
                while remaining_pixels > 0:
                    i += 1 
                    if i >= len(words):
                        break
                    length_in_pixels = (len(words[i]) + 1) * self.char_width
                    remaining_pixels -= length_in_pixels
                    if remaining_pixels < 0:
                        continue
                    else:
                        line += " " + words[i]
                
                line_array = [line, int(start) + 15, int(len(line) / total_chars * total_frames) + int(start) + 15]
                start = int(len(line) / total_chars * total_frames) + int(start)
                lines.append(line_array)
                self.text_array.append(line_array)
    
        cap.release()
        print('Transcription complete')

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
        
        clip = ImageSequenceClip([os.path.join(image_folder, image) for image in images], fps=self.fps)
        audio = AudioFileClip(self.audio_path)
        clip = clip.set_audio(audio)
        clip.write_videofile(output_video_path)
        shutil.rmtree(image_folder)
        os.remove(os.path.join(os.path.dirname(self.video_path), "audio.mp3"))
