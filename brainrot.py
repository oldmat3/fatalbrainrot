import praw
import asyncio
import edge_tts
import os
from pytube import YouTube
from selenium import webdriver

titleaudio = 'title.mp3'
contentsaudio = 'contents.mp3'
baskgroundvideo = '13 Minutes Minecraft Parkour Gameplay [Free to Use] [Map Download].mp4'
video_url = 'https://www.youtube.com/watch?v=NX-i0IWl3yg'

if os.path.exists(titleaudio):
    os.remove(titleaudio)

if os.path.exists(contentsaudio):
    os.remove(contentsaudio)

#reddit scraping
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
print("Title retreived")
print("Contents retreived")

#tts of title and contents of the post
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


#gameplay download
if os.path.exists(baskgroundvideo):
    print("background video already downloaded")
else:
    yt = YouTube(video_url)
    stream = yt.streams.get_highest_resolution()
    stream.download()
    print("Download completed")


#screenshot of post title
driver = webdriver.Firefox() 
  
driver.get("https://www.geeksforgeeks.org/") 
  
element = driver.find_element_by_class_name("header--navbar") 
  
element.screenshot('foo.png')