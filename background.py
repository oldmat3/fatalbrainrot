"""
This script is used to create a video with a background image and an audio file.
"""

# Standard Library Imports

# Third Party Imports
from moviepy.editor import *

# Local Imports

# Constants


video_clip = VideoFileClip("13 Minutes Minecraft Parkour Gameplay [Free to Use] [Map Download].mp4")

phone_aspect_ratio = (9, 16)
phone_width, phone_height = video_clip.size

if phone_width / phone_height > phone_aspect_ratio[0] / phone_aspect_ratio[1]:
    new_width = phone_height * phone_aspect_ratio[0] / phone_aspect_ratio[1]
    new_height = phone_height
else:
    new_width = phone_width
    new_height = phone_width * phone_aspect_ratio[1] / phone_aspect_ratio[0]

video_clip = video_clip.crop(width=new_width, height=new_height, x_center=phone_width / 2, y_center=phone_height / 2)  # No idea how this is working given the crop function doesn't exist

title_audio = AudioFileClip("title.mp3")
contents_audio = AudioFileClip("contents.mp3")

title_audio_duration = title_audio.duration
contents_audio_duration = contents_audio.duration

composite_audio = concatenate_audioclips([title_audio, contents_audio])

video_clip = video_clip.set_audio(composite_audio)

video_duration = title_audio_duration + contents_audio_duration
video_clip = video_clip.subclip(0, video_duration)

output_file = "final-overlay.mp4"
video_clip.write_videofile(output_file, codec="libx264", audio_codec="aac")

print(f"Video saved as {output_file}")
