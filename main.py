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

titleaudio = 'title.mp3'
contentsaudio = 'contents.mp3'
titless = 'title.png'
creditbarss = 'credit.png'
finalimgage = 'image.png'
finalnooverlay = 'final-overlay.mp4'
final = 'final.mp4'
backgroundvideo = 'background_video.mp4'
minecraft = 'https://www.youtube.com/watch?v=u7kdVe8q5zs'
subway_surfers = 'https://www.youtube.com/watch?v=RbVMiu4ubT0'

os.environ["PATH"] += os.pathsep + "C:\\Program Files\\ImageMagick-7.0.10-Q16"

for file in [titleaudio, contentsaudio, titless, creditbarss, finalimgage, finalnooverlay, final, backgroundvideo]:
    if os.path.exists(file):
        os.remove(file)

async def save_speech(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

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

def resize_image(image_clip, height):
    aspect_ratio = image_clip.size[0] / image_clip.size[1]
    new_width = int(height * aspect_ratio)
    image_pil = Image.fromarray(image_clip.get_frame(0))
    image_pil = image_pil.resize((new_width, height), Image.Resampling.LANCZOS)
    return ImageClip(np.array(image_pil)).set_duration(image_clip.duration)

def process_video(subreddit_name, timeframe, clip_length, game, use_youtube, use_tiktok):
    reddit = praw.Reddit(
        client_id="OAFOzx9mKDcw1hyTYc9h7A",
        client_secret="joLalAI15OzWENrytTxfJ9VWI07LTw",
        password="Password123",
        user_agent="testscript by u/Lonely_Eggplant920",
        username="Lonely_Eggplant920",
    )

    subreddit = reddit.subreddit(subreddit_name)
    top_post = next(subreddit.top(time_filter=timeframe, limit=1))

    Title = top_post.title
    Contents = top_post.selftext
    PostLink = "https://reddit.com" + top_post.permalink
    print("Title, contents, and link retrieved.")

    VOICES = ['en-US-GuyNeural']
    TITLE_VOICE = VOICES[0]

    async def amain():
        await save_speech(Title, TITLE_VOICE, titleaudio)
        await save_speech(Contents, TITLE_VOICE, contentsaudio)

    asyncio.run(amain())

    if game == "Subway Surfers":
        video_url = subway_surfers
    elif game == "Minecraft":
        video_url = minecraft
    else:
        video_url = None

    if video_url:
        try:
            if video_url.startswith('http'):
                yt = YouTube(video_url, on_progress_callback=on_progress)
                ys = yt.streams.get_highest_resolution()
                ys.download(filename=backgroundvideo)
                print("Background video downloaded.")
            else:
                print(f"Using local video: {video_url}")
        except Exception as e:
            print(f"Error handling video: {e}")
            return

    # Ensure the background video exists before proceeding
    if not os.path.exists(backgroundvideo):
        print(f"Error: {backgroundvideo} not found.")
        return

    chromedriver_autoinstaller.install()
    driver = webdriver.Chrome()
    driver.get(PostLink)
    driver.implicitly_wait(10)

    capture_element(driver, '[slot="title"]', titless)
    capture_element(driver, '[slot="credit-bar"]', creditbarss)
    driver.quit()

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

    try:
        video_clip = VideoFileClip(backgroundvideo)
    except OSError as e:
        print(f"Error reading video file: {e}")
        return

    phone_aspect_ratio = (9, 16)
    phone_width, phone_height = video_clip.size

    if phone_width / phone_height > phone_aspect_ratio[0] / phone_aspect_ratio[1]:
        new_width = phone_height * phone_aspect_ratio[0] / phone_aspect_ratio[1]
        new_height = phone_height
    else:
        new_width = phone_width
        new_height = phone_width * phone_aspect_ratio[1] / phone_aspect_ratio[0]

    video_clip = video_clip.crop(width=new_width, height=new_height, x_center=phone_width / 2, y_center=phone_height / 2)

    title_audio = AudioFileClip(titleaudio)
    contents_audio = AudioFileClip(contentsaudio)

    composite_audio = concatenate_audioclips([title_audio, contents_audio])

    video_clip = video_clip.set_audio(composite_audio)

    video_duration = title_audio.duration + contents_audio.duration
    video_clip = video_clip.subclip(0, video_duration)

    output_file = finalnooverlay
    video_clip.write_videofile(output_file, codec="libx264", audio_codec="aac")
    print(f"Video saved as {output_file}")

    video = VideoFileClip(finalnooverlay)

    image = ImageClip(finalimgage).set_duration(video.duration)
    image = resize_image(image, height=25)
    print(f"Resized image to height 35 pixels.")

    image = image.set_position(("center", "center"))

    composite = CompositeVideoClip([video, image])

    output_file = final
    composite.write_videofile(output_file, codec="libx264")

    if os.path.exists(output_file):
        try:
            os.remove(finalnooverlay)
            print("Temporary file 'final-overlay.mp4' deleted successfully.")
        except Exception as e:
            print(f"Error deleting file: {e}")

    split_video_into_clips(final, clip_length)

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

def start_gui():
    def on_start():
        subreddit = subreddit_combobox.get()
        timeframe = timeframe_combobox.get().lower()
        clip_length = int(clip_length_combobox.get())
        game = game_combobox.get()
        use_youtube = youtube_var.get()
        use_tiktok = tiktok_var.get()
        process_video(subreddit, timeframe, clip_length, game, use_youtube, use_tiktok)
    
    root = tk.Tk()
    root.title("Video Processing Tool")

    tk.Label(root, text="Subreddit:").pack()
    subreddit_combobox = ttk.Combobox(root, values=["AmItheAsshole"])
    subreddit_combobox.pack()

    tk.Label(root, text="Timeframe:").pack()
    timeframe_combobox = ttk.Combobox(root, values=["hour", "day", "week", "month", "year", "all"])
    timeframe_combobox.pack()

    tk.Label(root, text="Clip Length (seconds):").pack()
    clip_length_combobox = ttk.Combobox(root, values=["30", "60", "120", "300", "600"])
    clip_length_combobox.pack()

    tk.Label(root, text="Game:").pack()
    game_combobox = ttk.Combobox(root, values=["Minecraft", "Subway Surfers"])
    game_combobox.pack()

    youtube_var = tk.BooleanVar()
    youtube_checkbox = tk.Checkbutton(root, text="Upload to YouTube", variable=youtube_var)
    youtube_checkbox.pack()

    tiktok_var = tk.BooleanVar()
    tiktok_checkbox = tk.Checkbutton(root, text="Upload to TikTok", variable=tiktok_var)
    tiktok_checkbox.pack()

    start_button = tk.Button(root, text="Start", command=on_start)
    start_button.pack()

    root.mainloop()

if __name__ == "__main__":
    start_gui()
