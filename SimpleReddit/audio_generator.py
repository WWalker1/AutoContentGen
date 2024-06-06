import requests
import json
from moviepy.editor import AudioFileClip

class AudioGenerator:
    def __init__(self, xi_api_key):
        self.xi_api_key = xi_api_key
        self.voice_id = "21m00Tcm4TlvDq8ikWAM"  # You can change this to another voice if desired

    def generate_audio(self, text, output_path):
        # Request 1: Get audio stream
        stream_url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/stream"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.xi_api_key
        }
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        response = requests.post(stream_url, json=data, headers=headers)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(response.content)

        # Request 2: Get alignment data
        align_url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        align_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "xi-api-key": self.xi_api_key
        }

        align_response = requests.post(align_url, json=data, headers=align_headers)
        align_response.raise_for_status()

        alignment = align_response.json()['audio_file']['speech_marks']
        simplified_alignment = {
            'character_start_times_seconds': [mark['start'] / 1000 for mark in alignment],
            'character_end_times_seconds': [mark['end'] / 1000 for mark in alignment],
            'characters': [mark['text'] for mark in alignment]
        }

        audio_clip = AudioFileClip(output_path)
        return audio_clip, simplified_alignment

    def generate_full_audio(self, title, content, output_path):
        full_text = f"{title}. {content}"
        return self.generate_audio(full_text, output_path)