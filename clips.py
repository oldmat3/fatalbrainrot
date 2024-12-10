from moviepy.editor import VideoFileClip
import math
import os

def split_video_into_clips(video_path, clip_duration=30, output_folder='outputs'):
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Load the video
    video = VideoFileClip(video_path)
    
    # Calculate the number of clips needed
    total_duration = video.duration
    num_clips = math.ceil(total_duration / clip_duration)
    
    # Create and save each clip
    for i in range(num_clips):
        start_time = i * clip_duration
        end_time = min((i + 1) * clip_duration, total_duration)
        
        # Cut the video
        clip = video.subclip(start_time, end_time)
        
        # Define the output path in the outputs folder
        output_path = os.path.join(output_folder, f"{os.path.basename(video_path)}_{i + 1}.mp4")
        
        # Save the clip
        clip.write_videofile(output_path, codec="libx264")
    
    print("Clips saved successfully.")

# Example usage
video_path = './outputs/final.mp4'
split_video_into_clips(video_path)
