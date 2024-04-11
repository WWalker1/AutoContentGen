from gtts import gTTS
import os

def text_to_speech(text, filename, language='en'):
    # Create a gTTS object
    speech = gTTS(text=text, lang=language, slow=False)
    
    # Save the audio file
    speech.save(filename)
    
    # Play the audio file
    os.system(f"start {filename}")

# Example usage
text = "Hello, this is an example of text-to-speech using gTTS in Python."
filename = "output.mp3"
text_to_speech(text, filename)