import aeneas

# Load the audio file and the corresponding text
audio_file = "tts_audio.mp3"
text_file = "practice_text.txt"

# Create a configuration object
config = aeneas.Configuration()

# Load the TXT file
with open(text_file, "r") as file:
    transcript = file.read()

# Create a task object
task = aeneas.Task()
task.audio_file_path_absolute = audio_file
task.text_file_format = aeneas.TextFileFormat.PLAIN
task.text = transcript

# Process the task
executor = aeneas.ExecuteTask(task, config)
result = executor.execute()

# Access the aligned segments
for segment in result.sync_map_leaves():
    print(f"Text: {segment.text}")
    print(f"Start: {segment.begin:.3f}s")
    print(f"End: {segment.end:.3f}s")