from moviepy.editor import VideoFileClip
import math

def split_video_into_clips(video_path, clip_duration=60):
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
        
        # Save the clip
        output_path = f"{video_path}_clip_{i + 1}.mp4"
        clip.write_videofile(output_path, codec="libx264")
    
    print("Clips saved successfully.")

# Example usage
video_path = 'final.mp4'
split_video_into_clips(video_path)
