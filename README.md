# Reddit Video Creator

The Reddit Video Creator is a Python script that generates videos based on posts from a specified subreddit. It retrieves the hottest posts from the subreddit, allows the user to select a post, and then creates a video using the post's title and body as the script. The script utilizes text-to-speech (TTS) technology to generate audio and combines it with a random background video to create an engaging video.

## Features

- Retrieves the hottest posts from a specified subreddit
- Allows the user to select a post to generate a video
- Generates audio using the Eleven Labs TTS API
- Combines the generated audio with a random background video
- Adds the post's title and body as subtitles to the video
- Optionally includes a title image at the beginning of the video

## Prerequisites

Before running the script, make sure you have the following:

- Python 3.x installed
- Required Python libraries: `gtts`, `moviepy`, `praw`, `pandas`, `whisper`, `opencv-python`, `Pillow`, `numpy`, `requests`
- An Eleven Labs API key for the TTS functionality

## Getting Started

1. Clone the repository or download the script files.

2. Install the required Python libraries by running the following command:
   ```
   pip install gtts moviepy praw pandas whisper opencv-python Pillow numpy requests
   ```

3. Replace the placeholders in the script with your own values:
   - Set the `XI_API_KEY` variable in `main.py` with your Eleven Labs API key.
   - Update the `font_path` variable in `main.py` with the path to your desired font file.
   - Modify the `video_path` variable in `main.py` to point to your background video file.
   - Update the `titles_folder` variable in `main.py` with the path to the folder containing your title images (optional).

4. Run the `main.py` script:
   ```
   python main.py
   ```

5. Follow the prompts to select a post from the specified subreddit.

6. The script will generate the video and save it as `output_video.mp4` in the same directory.

## Use Cases

- Creating engaging videos for social media platforms like YouTube Shorts or TikTok
- Generating video summaries or highlights of popular Reddit posts
- Automating the process of creating content based on user-generated content from Reddit

## Customization

You can customize various aspects of the video generation process:

- Modify the `subreddit` variable in `main.py` to specify a different subreddit.
- Adjust the `num_posts` variable in `main.py` to retrieve a different number of posts.
- Update the TTS voice and settings by modifying the `generate_tts_audio` function in `main.py`.
- Customize the video parameters such as fps and codec in the `export_final_video` function in `main.py`.
- Modify the text styling (font, size, color, outline) in the `VideoTranscriber` class in `reddit_video_creator.py`.

## License

This project is open-source and available under the [MIT License](LICENSE).

## Acknowledgements

- [Eleven Labs](https://www.elevenlabs.io/) for providing the TTS API
- [PRAW](https://praw.readthedocs.io/) for simplifying Reddit API interactions
- [MoviePy](https://zulko.github.io/moviepy/) for video editing capabilities
- [OpenCV](https://opencv.org/) for image processing and video manipulation

Feel free to contribute, provide feedback, or report any issues you encounter while using this script.
