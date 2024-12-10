import os
import io
import praw
import asyncio
import edge_tts
import chromedriver_autoinstaller
import subprocess
from PIL import Image
from pytubefix import YouTube
from pytubefix.cli import on_progress
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_audioclips, ImageClip, CompositeVideoClip
import numpy as np

# Define filenames used in the script
titleaudio = 'title.mp3'
contentsaudio = 'contents.mp3'
titless = 'title.png'
creditbarss = 'credit.png'
finalimgage = 'image.png'
finalnooverlay = 'final-overlay.mp4'
final = 'final.mp4'
backgroundvideo = 'backgroundvideo.mp4'

# Configure PATH for ImageMagick and 
os.environ["PATH"] += os.pathsep + r"C:\Program Files\ImageMagick-7.0.10-Q16"


# Remove existing files if they exist to avoid conflicts
for file in [titleaudio, contentsaudio, titless, creditbarss, finalimgage, finalnooverlay, final]:
    if os.path.exists(file):
        os.remove(file)

# Function to generate speech audio from text
async def save_speech(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

# Function to capture elements from the webpage
def capture_element(driver, selector, output_filename):
    element = driver.find_element(By.CSS_SELECTOR, selector)
    location = element.location
    size = element.size
    png = driver.get_screenshot_as_png()
    image = Image.open(io.BytesIO(png))
    cropped_image = image.crop((
        location['x'], location['y'],
        location['x'] + size['width'],
        location['y'] + size['height']
    ))
    cropped_image.save(output_filename)
    print(f"Captured and saved screenshot to {output_filename}")

# Add the resize_image function
def resize_image(image_clip, height):

    # Calculate the aspect ratio to determine the new width
    aspect_ratio = image_clip.size[0] / image_clip.size[1]
    new_width = int(height * aspect_ratio)
    
    # Extract the first frame of the image clip and convert it to a PIL image
    image_pil = Image.fromarray(image_clip.get_frame(0))
    
    # Resize the image using a high-quality filter
    image_pil = image_pil.resize((new_width, height), Image.Resampling.LANCZOS)
    
    # Convert the PIL image back to an ImageClip and set the duration to match the video
    return ImageClip(np.array(image_pil)).set_duration(image_clip.duration)

# Process video function
def process_video():
    # Hardcoded subreddit name, timeframe, and clip length
    subreddit_name = "AmItheAsshole"
    timeframe = "day"

    # Initialize Reddit API client
    reddit = praw.Reddit(
        client_id="OAFOzx9mKDcw1hyTYc9h7A",
        client_secret="joLalAI15OzWENrytTxfJ9VWI07LTw",
        password="Password123",
        user_agent="testscript by u/Lonely_Eggplant920",
        username="Lonely_Eggplant920",
    )

    # Retrieve the top post from the selected subreddit
    subreddit = reddit.subreddit(subreddit_name)
    top_post = next(subreddit.top(time_filter=timeframe, limit=1))

    # Extract title, content, and post link
    Title = top_post.title
    Contents = top_post.selftext
    PostLink = "https://reddit.com" + top_post.permalink
    print("Title, contents, and link retrieved.")

    # Setup for speech synthesis
    VOICES = ['en-US-GuyNeural']
    TITLE_VOICE = VOICES[0]

    # Create speech audio for the title and content
    async def amain():
        await save_speech(Title, TITLE_VOICE, titleaudio)
        await save_speech(Contents, TITLE_VOICE, contentsaudio)

    # Run the speech synthesis tasks
    asyncio.run(amain())

    # Install and configure ChromeDriver
    chromedriver_autoinstaller.install()
    driver = webdriver.Chrome()
    driver.get(PostLink)
    driver.implicitly_wait(10)

    # Capture and save screenshots of the title and credit bar sections
    capture_element(driver, '[slot="title"]', titless)
    capture_element(driver, '[slot="credit-bar"]', creditbarss)
    driver.quit()

    # Combine the title and credit bar images into the final overlay image
    command = [
        'magick', creditbarss, '-background', 'none',
        titless, '-background', 'none', '-gravity', 'north',
        '-splice', '0x0', '-append', finalimgage
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Images combined and saved as {finalimgage}")
    except FileNotFoundError as e:
        print(f"Error: {e}")

    # Load the main video clip
    video_clip = VideoFileClip(backgroundvideo)


    # Load audio files for title and content
    title_audio = AudioFileClip(titleaudio)
    contents_audio = AudioFileClip(contentsaudio)

    # Concatenate the audio files into one
    composite_audio = concatenate_audioclips([title_audio, contents_audio])

    # Set the concatenated audio to the video
    video_clip = video_clip.set_audio(composite_audio)

    # Set the video duration to match the combined audio duration
    video_duration = title_audio.duration + contents_audio.duration
    video_clip = video_clip.subclip(0, video_duration)

    # Output the final video with audio overlay
    output_file = finalnooverlay
    video_clip.write_videofile(output_file, codec="libx264", audio_codec="aac")
    print(f"Video saved as {output_file}")

    # Resize the overlay image and combine with video
    overlay_image = ImageClip(finalimgage).set_duration(video_clip.duration)
    overlay_image = resize_image(overlay_image, height=150)
    overlay_image = overlay_image.set_position(("center", "center"))

    # Combine video and image
    composite = CompositeVideoClip([video_clip, overlay_image])

    # Export the final video with the combined layers
    final_output_file = final
    composite.write_videofile(final_output_file, codec="libx264")
    print(f"Final video saved as {final_output_file}")

    # Delete the temporary overlay video if it exists
    if os.path.exists(output_file):
        try:
            os.remove(output_file)
            print("Temporary file 'final-overlay.mp4' deleted successfully.")
        except Exception as e:
            print(f"Error deleting file: {e}")

# Process the video
process_video()
