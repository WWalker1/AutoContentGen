import requests
from moviepy.editor import TextClip, CompositeVideoClip

class SubtitleGenerator:
    def __init__(self, xi_api_key, font_path="Mont-HeavyDEMO.otf", font_size=120, font_color='white', stroke_color='black', stroke_width=5, voice_id='21m00Tcm4TlvDq8ikWAM'):
        self.xi_api_key = xi_api_key
        self.font_path = font_path
        self.font_size = font_size
        self.font_color = font_color
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
        self.voice_id = voice_id

    def generate_subtitles(self, script, alignment, start_time=0):
        char_starts = alignment['character_start_times_seconds']
        char_ends = alignment['character_end_times_seconds']
        chars = alignment['characters']

        subtitles = []
        current_subtitle = ""
        current_start = None
        for i, char in enumerate(chars):
            if char == " ":
                if current_subtitle:
                    end_time = char_ends[i] + start_time
                    subtitles.append((current_subtitle.strip(), current_start + start_time, end_time))
                    current_subtitle = ""
            else:
                if not current_subtitle:
                    current_start = char_starts[i]
                current_subtitle += char

        if current_subtitle:
            end_time = char_ends[-1] + start_time
            subtitles.append((current_subtitle.strip(), current_start + start_time, end_time))

        return subtitles

    def add_subtitles_to_video(self, video_clip, subtitles):
        video_width = video_clip.w
        video_height = video_clip.h

        subtitle_clips = []
        for text, start, end in subtitles:
            clip = TextClip(text, fontsize=self.font_size, color=self.font_color,
                          stroke_color=self.stroke_color, stroke_width=self.stroke_width,
                          method='caption', size=(video_width - 100, None), align='center',
                          font=self.font_path)

            clip = clip.set_position(('center', video_height - 150)).set_start(start).set_end(end)
            subtitle_clips.append(clip)

        return CompositeVideoClip([video_clip] + subtitle_clips)