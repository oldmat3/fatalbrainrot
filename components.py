"""
Collects data from Reddit and YouTube, generates audio from text, and captures screenshots of the Reddit post.
"""

# Standard Library Imports
from asyncio import run as async_run
from io import BytesIO
from os import path, remove
from subprocess import run as sub_run

# Third Party Imports
from PIL import Image
from edge_tts import Communicate
from praw import Reddit
from pytubefix import YouTube
from pytubefix.cli import on_progress
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# Local Imports

# Constants
TITLE_AUDIO = "title.mp3"
CONTENTS_AUDIO = "contents.mp3"
TITLE_IMAGE = "title.png"
CREDIT_BARS = "credit.png"
END_IMAGE = "image.png"
END_OVERLAY = "final-overlay.mp4"
FINAL_VIDEO = "final.mp4"
BACKGROUND_VIDEO = "13 Minutes Minecraft Parkour Gameplay [Free to Use] [Map Download].mp4"
url = "https://www.youtube.com/watch?v=NX-i0IWl3yg"
service = Service(r"C:\Users\kalen\Downloads\chromedriver_win32\chromedriver.exe")  # This needs to be changed to the path of the chromedriver executable. Probably automatically 
# download it into a folder and use that path.

# Remove existing files if they exist
for file in [TITLE_AUDIO, CONTENTS_AUDIO, TITLE_IMAGE, CREDIT_BARS, END_IMAGE, END_OVERLAY, FINAL_VIDEO]:
    if path.exists(file):
        remove(file)

reddit = Reddit(
    client_id="OAFOzx9mKDcw1hyTYc9h7A",
    client_secret="joLalAI15OzWENrytTxfJ9VWI07LTw",
    password="Password123",
    user_agent="testscript by u/Lonely_Eggplant920",
    username="Lonely_Eggplant920",
)

subreddit = reddit.subreddit("AmItheAsshole")

top_post = next(subreddit.top(time_filter="day", limit=1))

Title = top_post.title
Contents = top_post.selftext
PostLink = "https://reddit.com" + top_post.permalink
print("Title retrieved")
print("Contents retrieved")
print("Link retrieved:", PostLink)

VOICES = ["en-US-GuyNeural"]
TITLE_TEXT = Title
CONTENTS_TEXT = Contents
TITLE_VOICE = VOICES[0]
CONTENTS_VOICE = VOICES[0]
TITLE_OUTPUT_FILE = "title.mp3"
CONTENTS_OUTPUT_FILE = "contents.mp3"


async def save_speech(
        text: str,
        voice: str,
        output_file: str
) -> None:
    """
    Generates a speech audio file from text using the specified voice and saves it to the output file.

    Args:
        text (str): The text to convert to speech.
        voice (str): The voice to use for the speech.
        output_file (str): The file to save the speech audio to.

    Returns:
        None
    """
    communicate = Communicate(text, voice)
    await communicate.save(output_file)


async def async_main():
    """
    Main function to generate speech audio files from text.

    Returns:
        None
    """
    await save_speech(TITLE_TEXT, TITLE_VOICE, TITLE_OUTPUT_FILE)
    await save_speech(CONTENTS_TEXT, CONTENTS_VOICE, CONTENTS_OUTPUT_FILE)


if __name__ == "__main__":
    async_run(async_main())

try:
    if path.exists(BACKGROUND_VIDEO):
        print("Background video already downloaded")
    else:
        yt = YouTube(url, on_progress_callback=on_progress)
        print(yt.title)
        ys = yt.streams.get_highest_resolution()
        ys.download()
        print("Download completed")
except Exception as e:
    print(f"Error downloading video: {e}")

driver = webdriver.Chrome(service=service)
driver.get(PostLink)

driver.implicitly_wait(10)

# Capture title screenshot
title_element = driver.find_element(By.CSS_SELECTOR, "[slot=\"title\"]")
title_location = title_element.location
title_size = title_element.size

png = driver.get_screenshot_as_png()
image = Image.open(BytesIO(png))

left = title_location["x"]
top = title_location["y"]
right = title_location["x"] + title_size["width"]
bottom = title_location["y"] + title_size["height"]

title_image = image.crop((left, top, right, bottom))
title_image.save(TITLE_IMAGE)

# Capture credit bar screenshot
credit_bar_element = driver.find_element(By.CSS_SELECTOR, "[slot=\"credit-bar\"]")
credit_bar_location = credit_bar_element.location
credit_bar_size = credit_bar_element.size

left = credit_bar_location["x"]
top = credit_bar_location["y"]
right = credit_bar_location["x"] + credit_bar_size["width"]
bottom = credit_bar_location["y"] + credit_bar_size["height"]

credit_bar_image = image.crop((left, top, right, bottom))
credit_bar_image.save(CREDIT_BARS)

driver.quit()

# Combine images
command = [
    "magick",
    CREDIT_BARS,
    "-background", "none",
    TITLE_IMAGE,
    "-background", "none",
    "-gravity", "north",
    "-splice", "0x0",
    "-append",
    END_IMAGE
]

sub_run(command, check=True)

print(f"Images combined and saved as {END_IMAGE}")
