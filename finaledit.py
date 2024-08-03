from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image
import numpy as np

def resize_image(image_clip, height):
    aspect_ratio = image_clip.size[0] / image_clip.size[1]
    new_width = int(height * aspect_ratio)
    image_pil = image_clip.get_frame(0)
    image_pil = Image.fromarray(image_pil)
    image_pil = image_pil.resize((new_width, height), Image.Resampling.LANCZOS)
    return ImageClip(np.array(image_pil)).set_duration(image_clip.duration)

video = VideoFileClip("final-overlay.mp4")
image = ImageClip("image.png").set_duration(video.duration)
image = resize_image(image, height=35)
image = image.set_position("center")
composite = CompositeVideoClip([video, image])
composite.write_videofile("final.mp4", codec="libx264")
