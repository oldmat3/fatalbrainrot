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
import subprocess

titleaudio = 'title.mp3'
contentsaudio = 'contents.mp3'
titless = 'title.png'
creditbarss = 'credit.png'
finalimgage = 'image.png'
baskgroundvideo = '13 Minutes Minecraft Parkour Gameplay [Free to Use] [Map Download].mp4'
video_url = 'https://www.youtube.com/watch?v=NX-i0IWl3yg'
service = Service(r'C:\Users\kalen\Downloads\chromedriver_win32\chromedriver.exe')

if os.path.exists(titleaudio):
    os.remove(titleaudio)

if os.path.exists(contentsaudio):
    os.remove(contentsaudio)

if os.path.exists(titless):
    os.remove(titless)

if os.path.exists(creditbarss):
    os.remove(creditbarss)

if os.path.exists(finalimgage):
    os.remove(finalimgage)

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
print("Title retrieved")
print("Contents retrieved")
print("Link retrieved:", PostLink)

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
try:
    if os.path.exists(baskgroundvideo):
        print("background video already downloaded")
    else:
        yt = YouTube(video_url)
        stream = yt.streams.get_highest_resolution()
        stream.download()
        print("Download completed")
except Exception as e:
    print(f"if your seeing this its youtube, Go complain on the pytube GitHub until they fix it.")

driver = webdriver.Chrome(service=service)
driver.get(PostLink)

driver.implicitly_wait(10)

title_element = driver.find_element(By.CSS_SELECTOR, '[slot="title"]')
title_location = title_element.location
title_size = title_element.size

png = driver.get_screenshot_as_png()
image = Image.open(io.BytesIO(png))

left = title_location['x']
top = title_location['y']
right = title_location['x'] + title_size['width']
bottom = title_location['y'] + title_size['height']

title_image = image.crop((left, top, right, bottom))
title_image.save('title.png')

credit_bar_element = driver.find_element(By.CSS_SELECTOR, '[slot="credit-bar"]')
credit_bar_location = credit_bar_element.location
credit_bar_size = credit_bar_element.size

left = credit_bar_location['x']
top = credit_bar_location['y']
right = credit_bar_location['x'] + credit_bar_size['width']
bottom = credit_bar_location['y'] + credit_bar_size['height']

credit_bar_image = image.crop((left, top, right, bottom))
credit_bar_image.save('credit.png')

driver.quit()

command = [
    'magick', 'convert',
    creditbarss,
    '-background', 'none',
    titless,
    '-background', 'none',
    '-gravity', 'north',
    '-splice', '0x5',
    '-append',
    finalimgage
]

subprocess.run(command, check=True)

print(f"Images combined and saved as {finalimgage}")
