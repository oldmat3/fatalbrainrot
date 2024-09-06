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
import tkinter as tk
from tkinter import ttk
import math

# Define filenames used in the script
titleaudio = 'title.mp3'
contentsaudio = 'contents.mp3'
titless = 'title.png'
creditbarss = 'credit.png'
finalimgage = 'image.png'
finalnooverlay = 'final-overlay.mp4'
final = 'final.mp4'
backgroundvideo = '13 Minutes Minecraft Parkour Gameplay [Free to Use] [Map Download].mp4'
url = 'https://www.youtube.com/watch?v=NX-i0IWl3yg'

# Configure PATH for ImageMagick
os.environ["PATH"] += os.pathsep + "C:\\Program Files\\ImageMagick-7.0.10-Q16"

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
    aspect_ratio = image_clip.size[0] / image_clip.size[1]
    new_width = int(height * aspect_ratio)
    image_pil = Image.fromarray(image_clip.get_frame(0))
    image_pil = image_pil.resize((new_width, height), Image.Resampling.LANCZOS)
    return ImageClip(np.array(image_pil)).set_duration(image_clip.duration)

# Process video function
def process_video(subreddit_name, timeframe, clip_length, game, use_youtube, use_tiktok):
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

    # Download the background video if not already present
    try:
        if use_youtube and not os.path.exists(backgroundvideo):
            yt = YouTube(url, on_progress_callback=on_progress)
            ys = yt.streams.get_highest_resolution()
            ys.download()
            print("Background video downloaded.")
    except Exception as e:
        print(f"Error downloading video: {e}")

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

    # Define the aspect ratio for phone screens
    phone_aspect_ratio = (9, 16)
    phone_width, phone_height = video_clip.size

    # Adjust the video dimensions to fit the phone aspect ratio
    if phone_width / phone_height > phone_aspect_ratio[0] / phone_aspect_ratio[1]:
        new_width = phone_height * phone_aspect_ratio[0] / phone_aspect_ratio[1]
        new_height = phone_height
    else:
        new_width = phone_width
        new_height = phone_width * phone_aspect_ratio[1] / phone_aspect_ratio[0]

    # Crop the video to the new dimensions centered in the frame
    video_clip = video_clip.crop(width=new_width, height=new_height, x_center=phone_width / 2, y_center=phone_height / 2)

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

    # Load the video clip to be used as the background
    video = VideoFileClip(finalnooverlay)

    # Load the overlay image and match its duration with the video
    image = ImageClip(finalimgage).set_duration(video.duration)

    # Resize the image to a height of 35 pixels while keeping its aspect ratio
    image = resize_image(image, height=35)
    print(f"Resized image to height 35 pixels.")

    # Set the position of the image overlay to be at the center of the video
    image = image.set_position(("center", "center"))

    # Combine the video and image into a single composite clip
    composite = CompositeVideoClip([video, image])

    # Export the final video with the combined layers
    output_file = final
    composite.write_videofile(output_file, codec="libx264")

    # Check if the final video was created and then delete the overlay video
    if os.path.exists(output_file):
        try:
            os.remove(finalnooverlay)
            print("Temporary file 'final-overlay.mp4' deleted successfully.")
        except Exception as e:
            print(f"Error deleting file: {e}")

    # Split the final video into clips
    split_video_into_clips(final, clip_length)


# Function to split video into clips
def split_video_into_clips(video_path, clip_duration=60):
    video = VideoFileClip(video_path)
    total_duration = video.duration
    num_clips = math.ceil(total_duration / clip_duration)
    
    for i in range(num_clips):
        start_time = i * clip_duration
        end_time = min((i + 1) * clip_duration, total_duration)
        clip = video.subclip(start_time, end_time)
        output_path = f"{video_path}_clip_{i + 1}.mp4"
        clip.write_videofile(output_path, codec="libx264")
    
    print("Clips saved successfully.")

# Create a GUI for user input
def start_gui():
    def on_start():
        subreddit = subreddit_combobox.get()
        timeframe = timeframe_combobox.get().lower()
        clip_length = int(clip_length_combobox.get())
        game = game_combobox.get()
        use_youtube = youtube_var.get()
        use_tiktok = tiktok_var.get()
        process_video(subreddit, timeframe, clip_length, game, use_youtube, use_tiktok)
    
    # Create the main window
    root = tk.Tk()
    root.title("Fatal Brainrot")

    # Subreddit input
    tk.Label(root, text="Subreddit:").pack()
    subreddit_combobox = ttk.Combobox(root, values=["AmItheAsshole"])
    subreddit_combobox.pack()

    # Timeframe input
    tk.Label(root, text="Timeframe:").pack()
    timeframe_combobox = ttk.Combobox(root, values=["hour", "day", "week", "month", "year"])
    timeframe_combobox.pack()

    # Clip Length input
    tk.Label(root, text="Clip Length (seconds):").pack()
    clip_length_combobox = ttk.Combobox(root, values=["30", "60"])
    clip_length_combobox.pack()

    # Game input
    tk.Label(root, text="Game:").pack()
    game_combobox = ttk.Combobox(root, values=["Minecraft", "Subway Surfers", "GTA"])
    game_combobox.pack()

    # YouTube Checkbox
    youtube_var = tk.BooleanVar()
    youtube_checkbox = tk.Checkbutton(root, text="Upload to YouTube", variable=youtube_var)
    youtube_checkbox.pack()

    # TikTok Checkbox
    tiktok_var = tk.BooleanVar()
    tiktok_checkbox = tk.Checkbutton(root, text="Upload to TikTok", variable=tiktok_var)
    tiktok_checkbox.pack()

    # Start Button
    start_button = tk.Button(root, text="Start", command=on_start)
    start_button.pack()

    # Run the GUI main loop
    root.mainloop()

# Start the GUI
if __name__ == "__main__":
    start_gui()
