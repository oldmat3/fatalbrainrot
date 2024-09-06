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

titleaudio = 'title.mp3'
contentsaudio = 'contents.mp3'
titless = 'title.png'
creditbarss = 'credit.png'
finalimgage = 'image.png'
finalnooverlay = 'final-overlay.mp4'
final = 'final.mp4'
backgroundvideo = '13 Minutes Minecraft Parkour Gameplay [Free to Use] [Map Download].mp4'
url = 'https://www.youtube.com/watch?v=NX-i0IWl3yg'

os.environ["PATH"] += os.pathsep + "C:\\Program Files\\ImageMagick-7.0.10-Q16"

for file in [titleaudio, contentsaudio, titless, creditbarss, finalimgage, finalnooverlay, final]:
    if os.path.exists(file):
        os.remove(file)

reddit = praw.Reddit(
    client_id="OAFOzx9mKDcw1hyTYc9h7A",
    client_secret="joLalAI15OzWENrytTxfJ9VWI07LTw",
    password="Password123",
    user_agent="testscript by u/Lonely_Eggplant920",
    username="Lonely_Eggplant920",
)

subreddit = reddit.subreddit('AmItheAsshole')
top_post = next(subreddit.top(time_filter='day', limit=1))

Title = top_post.title
Contents = top_post.selftext
PostLink = "https://reddit.com" + top_post.permalink
print("Title, contents, and link retrieved.")

VOICES = ['en-US-GuyNeural']
TITLE_VOICE = VOICES[0]

async def save_speech(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

async def amain():
    await save_speech(Title, TITLE_VOICE, titleaudio)
    await save_speech(Contents, TITLE_VOICE, contentsaudio)

if __name__ == "__main__":
    asyncio.run(amain())

try:
    if not os.path.exists(backgroundvideo):
        yt = YouTube(url, on_progress_callback=on_progress)
        ys = yt.streams.get_highest_resolution()
        ys.download()
        print("Background video downloaded.")
except Exception as e:
    print(f"Error downloading video: {e}")

chromedriver_autoinstaller.install()
driver = webdriver.Chrome()
driver.get(PostLink)
driver.implicitly_wait(10)

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

video_clip = VideoFileClip(backgroundvideo)

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

def resize_image(image_clip, height):
    aspect_ratio = image_clip.size[0] / image_clip.size[1]
    new_width = int(height * aspect_ratio)
    image_pil = Image.fromarray(image_clip.get_frame(0))
    image_pil = image_pil.resize((new_width, height), Image.Resampling.LANCZOS)
    return ImageClip(np.array(image_pil)).set_duration(image_clip.duration)

video = VideoFileClip(finalnooverlay)

image = ImageClip(finalimgage).set_duration(video.duration)

image = resize_image(image, height=35)

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

os.system('python minute.py')
