from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image
import numpy as np
import os

def resize_image(image_clip, height):
    """
    Resizes an ImageClip to a specified height while maintaining the aspect ratio.

    Args:
        image_clip (ImageClip): The image clip to resize.
        height (int): The desired height of the resized image.

    Returns:
        ImageClip: A resized ImageClip with the new dimensions.
    """
    # Calculate the aspect ratio to determine the new width
    aspect_ratio = image_clip.size[0] / image_clip.size[1]
    new_width = int(height * aspect_ratio)
    
    # Extract the first frame of the image clip and convert it to a PIL image
    image_pil = Image.fromarray(image_clip.get_frame(0))
    
    # Resize the image using a high-quality filter
    image_pil = image_pil.resize((new_width, height), Image.Resampling.LANCZOS)
    
    # Convert the PIL image back to an ImageClip and set the duration to match the video
    return ImageClip(np.array(image_pil)).set_duration(image_clip.duration)

# Load the video clip to be used as the background
video = VideoFileClip("final-overlay.mp4")

# Load the overlay image and match its duration with the video
image = ImageClip("image.png").set_duration(video.duration)

# Resize the image to a height of 35 pixels while keeping its aspect ratio
image = resize_image(image, height=35)

# Set the position of the image overlay to be at the center of the video
image = image.set_position(("center", "center"))

# Combine the video and image into a single composite clip
composite = CompositeVideoClip([video, image])

# Export the final video with the combined layers
output_file = "final.mp4"
composite.write_videofile(output_file, codec="libx264")

# Check if the final video was created and then delete the overlay video
if os.path.exists(output_file):
    try:
        os.remove("final-overlay.mp4")
        print("Temporary file 'final-overlay.mp4' deleted successfully.")
    except Exception as e:
        print(f"Error deleting file: {e}")

os.system('python minute.py')
