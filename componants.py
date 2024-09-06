import praw
import asyncio
import edge_tts
import os
from pytubefix import YouTube
from pytubefix.cli import on_progress
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from PIL import Image
import io
import subprocess
import chromedriver_autoinstaller

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

# Initialize Reddit API client
reddit = praw.Reddit(
    client_id="OAFOzx9mKDcw1hyTYc9h7A",
    client_secret="joLalAI15OzWENrytTxfJ9VWI07LTw",
    password="Password123",
    user_agent="testscript by u/Lonely_Eggplant920",
    username="Lonely_Eggplant920",
)

# Retrieve the top post from the 'AmItheAsshole' subreddit
subreddit = reddit.subreddit('AmItheAsshole')
top_post = next(subreddit.top(time_filter='day', limit=1))

# Extract title, content, and post link
Title = top_post.title
Contents = top_post.selftext
PostLink = "https://reddit.com" + top_post.permalink
print("Title, contents, and link retrieved.")

# Setup for speech synthesis
VOICES = ['en-US-GuyNeural']
TITLE_VOICE = VOICES[0]

# Function to generate speech audio from text
async def save_speech(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

# Create speech audio for the title and content
async def amain():
    await save_speech(Title, TITLE_VOICE, "title.mp3")
    await save_speech(Contents, TITLE_VOICE, "contents.mp3")

# Run the speech synthesis tasks
if __name__ == "__main__":
    asyncio.run(amain())

# Download the background video if not already present
try:
    if not os.path.exists(backgroundvideo):
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

# Run the background processing script
os.system('python background.py')
