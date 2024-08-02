import praw
import asyncio
import edge_tts
import os
from pytube import YouTube
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from PIL import Image
import io

titleaudio = 'title.mp3'
contentsaudio = 'contents.mp3'
titless = 'element_screenshot.png'
baskgroundvideo = '13 Minutes Minecraft Parkour Gameplay [Free to Use] [Map Download].mp4'
video_url = 'https://www.youtube.com/watch?v=NX-i0IWl3yg'
service = Service(r'C:\Users\kalen\Downloads\chromedriver_win32\chromedriver.exe')

if os.path.exists(titleaudio):
    os.remove(titleaudio)

if os.path.exists(contentsaudio):
    os.remove(contentsaudio)

if os.path.exists(titless):
    os.remove(titless)

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
print("Title retrieved")
print("Contents retrieved")

VOICES = ['en-US-GuyNeural', 'en-US-JennyNeural']
TITLE_TEXT = Title
CONTENTS_TEXT = Contents
TITLE_VOICE = VOICES[0]
CONTENTS_VOICE = VOICES[1]
TITLE_OUTPUT_FILE = "title.mp3"
CONTENTS_OUTPUT_FILE = "contents.mp3"

async def save_speech(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

async def amain():
    await save_speech(TITLE_TEXT, TITLE_VOICE, TITLE_OUTPUT_FILE)
    await save_speech(CONTENTS_TEXT, CONTENTS_VOICE, CONTENTS_OUTPUT_FILE)

if __name__ == "__main__":
    asyncio.run(amain())

if os.path.exists(baskgroundvideo):
    print("background video already downloaded")
else:
    yt = YouTube(video_url)
    stream = yt.streams.get_highest_resolution()
    stream.download()
    print("Download completed")

driver = webdriver.Chrome(service=service)
driver.get('https://example.com')

element = driver.find_element(By.CSS_SELECTOR, 'h1')

location = element.location
size = element.size

png = driver.get_screenshot_as_png()

image = Image.open(io.BytesIO(png))
left = location['x']
top = location['y']
right = location['x'] + size['width']
bottom = location['y'] + size['height']

image = image.crop((left, top, right, bottom))
image.save('element_screenshot.png')

driver.quit()
