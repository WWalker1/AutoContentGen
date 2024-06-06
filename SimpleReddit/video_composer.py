from moviepy.editor import CompositeVideoClip, VideoFileClip, concatenate_videoclips, AudioFileClip, vfx
import os 

class VideoComposer:
    def __init__(self, audio_generator, video_selector, title_screen, subtitle_generator):
        self.audio_generator = audio_generator
        self.video_selector = video_selector
        self.title_screen = title_screen
        self.subtitle_generator = subtitle_generator

    def create_video(self, title, content, output_path):
        # Generate title audio
        title_audio_path = "title_audio.mp3"
        title_audio, _ = self.audio_generator.generate_audio(title, title_audio_path)
        title_duration = title_audio.duration

        # Generate main audio and get alignment data
        main_audio_path = "main_audio.mp3"
        main_audio, alignment = self.audio_generator.generate_audio(content, main_audio_path)

        # Generate subtitles using the same alignment data
        subtitles = self.subtitle_generator.generate_subtitles(content, alignment)

        total_duration = title_duration + main_audio.duration + 0.1  # Add small buffer

        # Select and prepare background video
        bg_video_path = self.video_selector.select_video(total_duration)
        bg_video = self.video_selector.trim_video(bg_video_path, total_duration)

        # Create title clip
        title_clip = self.title_screen.create_title_clip(title, title_duration)
        title_clip = title_clip.resize(height=bg_video.h)
        title_clip = title_clip.set_position(('center', 'center'))

        # Darken the background video during title
        darkened_bg = bg_video.subclip(0, title_duration).fx(vfx.colorx, 0.5)
        title_part = CompositeVideoClip([darkened_bg, title_clip]).set_audio(title_audio)

        # Main content video with subtitles
        main_video = bg_video.subclip(title_duration, total_duration)
        
        # Generate subtitles using the same alignment data
        subtitles = self.subtitle_generator.generate_subtitles(content, alignment)
        main_video = self.subtitle_generator.add_subtitles_to_video(main_video, subtitles)
        
        # Delay the main audio to start after the title
        delayed_main_audio = AudioFileClip(main_audio_path).set_start(title_duration)
        main_video = main_video.set_audio(delayed_main_audio)

        # Combine title and main video
        final_video = concatenate_videoclips([title_part, main_video])
        final_video.write_videofile(output_path, fps=bg_video.fps, codec='libx264')

        # Clean up temporary files and close clips
        title_audio.close()
        main_audio.close()
        delayed_main_audio.close()
        bg_video.close()
        title_clip.close()
        darkened_bg.close()
        title_part.close()
        main_video.close()
        final_video.close()

        os.remove(title_audio_path)
        os.remove(main_audio_path)
