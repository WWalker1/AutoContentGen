from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip
import textwrap
from moviepy.editor import ImageClip
import os 

class TitleScreen:
       def __init__(self, template_path, max_font_size=120, text_color=(255, 255, 255), outline_color=(0, 0, 0), outline_width=5):
           self.template = Image.open(template_path)
           self.max_font_size = max_font_size
           self.text_color = text_color
           self.outline_color = outline_color
           self.outline_width = outline_width

       def create_title_image(self, title, output_path):
           draw = ImageDraw.Draw(self.template)
           max_width = self.template.width - 100  # Leave some padding
           max_height = self.template.height - 100  # Leave some padding

           words = title.split()
           font_size = self.max_font_size
           font = ImageFont.truetype("arial.ttf", font_size)

           while True:
               lines = []
               current_line = words[0]
               for word in words[1:]:
                   test_line = current_line + " " + word
                   line_width = draw.textlength(test_line, font=font)
                   if line_width <= max_width:
                       current_line = test_line
                   else:
                       lines.append(current_line)
                       current_line = word
               lines.append(current_line)

               total_height = len(lines) * (font_size + 10)  # 10 is line spacing
               if total_height <= max_height:
                   break

               font_size -= 5
               font = ImageFont.truetype("arial.ttf", font_size)

           y = (self.template.height - total_height) // 2

           for line in lines:
               line_width = draw.textlength(line, font=font)
               x = (self.template.width - line_width) // 2

               # Draw outline
               for dx, dy in [(j, i) for i in range(-self.outline_width, self.outline_width+1) for j in range(-self.outline_width, self.outline_width+1)]:
                   draw.text((x+dx, y+dy), line, font=font, fill=self.outline_color)

               # Draw text
               draw.text((x, y), line, font=font, fill=self.text_color)
               y += font_size + 10

           self.template.save(output_path)
           return output_path

       def create_title_clip(self, title, duration):
           temp_path = "temp_title.png"
           self.create_title_image(title, temp_path)
           clip = ImageClip(temp_path).set_duration(duration)
           os.remove(temp_path)
           return clip