import cv2
import numpy as np
from moviepy.editor import ImageClip, TextClip, CompositeVideoClip, AudioFileClip, VideoFileClip
import requests
import os
from PIL import Image, ImageDraw

class TitleGenerator:
       def __init__(self, template_path, xi_api_key, font_size=60, text_color=(255, 255, 255), outline_color=(0, 0, 0), outline_width=5):
           self.template = Image.open(template_path)
           self.font_size = font_size
           self.text_color = text_color
           self.outline_color = outline_color
           self.outline_width = outline_width
           self.xi_api_key = xi_api_key

       def create_title_image(self, title, output_path, max_width=None):
           draw = ImageDraw.Draw(self.template)
           if max_width is None:
               max_width = self.template.width - 100  # Leave some padding

           lines = []
           words = title.split()
           current_line = words[0]
           for word in words[1:]:
               test_line = current_line + " " + word
               line_width = draw.textlength(test_line, font=None, size=self.font_size)
               if line_width <= max_width:
                   current_line = test_line
               else:
                   lines.append(current_line)
                   current_line = word
           lines.append(current_line)

           total_height = len(lines) * (self.font_size + 20)  # 20 is line spacing
           y = (self.template.height - total_height) // 2

           for line in lines:
               line_width = draw.textlength(line, font=None, size=self.font_size)
               x = (self.template.width - line_width) // 2

               # Draw outline
               for dx, dy in [(j, i) for i in range(-self.outline_width, self.outline_width+1) for j in range(-self.outline_width, self.outline_width+1)]:
                   draw.text((x+dx, y+dy), line, font=None, fill=self.outline_color, size=self.font_size)

               # Draw text
               draw.text((x, y), line, font=None, fill=self.text_color, size=self.font_size)
               y += self.font_size + 20

           self.template.save(output_path)
           return output_path

       def generate_title_video(self, title, output_path):
           temp_path = "temp_title.png"
           self.create_title_image(title, temp_path)
           
           audio_path = "temp_title_audio.mp3"
           audio = self.audio_generator.generate_audio(title, audio_path)
           
           video = VideoFileClip(temp_path).set_duration(audio.duration)
           video = video.set_audio(audio)
           video.write_videofile(output_path, codec='libx264')
           
           os.remove(temp_path)
           os.remove(audio_path)
           
           return audio