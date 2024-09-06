from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_audioclips
import os

# Load the main video clip
video_clip = VideoFileClip("13 Minutes Minecraft Parkour Gameplay [Free to Use] [Map Download].mp4")

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
title_audio = AudioFileClip("title.mp3")
contents_audio = AudioFileClip("contents.mp3")

# Concatenate the audio files into one
composite_audio = concatenate_audioclips([title_audio, contents_audio])

# Set the concatenated audio to the video
video_clip = video_clip.set_audio(composite_audio)

# Set the video duration to match the combined audio duration
video_duration = title_audio.duration + contents_audio.duration
video_clip = video_clip.subclip(0, video_duration)

# Output the final video with audio overlay
output_file = "final-overlay.mp4"
video_clip.write_videofile(output_file, codec="libx264", audio_codec="aac")

print(f"Video saved as {output_file}")

# Run the final edit script after processing this video
os.system('python finaledit.py')
