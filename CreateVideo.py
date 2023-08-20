import numpy as np
from moviepy.editor import *


def circular_mask(width, height):
    center_x = width // 2
    center_y = height // 2
    radius = min(center_x, center_y)

    mask = np.zeros((height, width), dtype=bool)
    y, x = np.ogrid[:height, :width]
    mask = (x - center_x) ** 2 + (y - center_y) ** 2 <= radius**2
    return mask


def get_chunk_clip(video_path, image_path):
    video = VideoFileClip(video_path)
    image = ImageClip(image_path)

    # Trim the video to the desired duration
    video = video.resize(0.5)

    # Set the duration of the image clip to match the video duration
    image = image.with_duration(video.duration).margin(20)

    # Apply the circular mask to the video frames
    # masked_frames = [
    #     frame * circular_mask(video.w, video.h)[:, :, np.newaxis] for frame in video.iter_frames()
    # ]

    # Convert the masked frames into a VideoClip
    # video_with_mask = ImageSequenceClip(masked_frames, fps=video.fps)

    # Create a clips array with the video (with circular mask) on the left and the image on the right
    final_clip = clips_array([[image, video]])
    # final_clip.fps = video.fps
    return final_clip


def stitch_video(save_path, images_len, videos_len):
    videos = [os.path.join(save_path, f"chunk_{i}.mp4") for i in range(videos_len)]
    images = [os.path.join(save_path, f"image_{i}.png") for i in range(images_len)]

    summary_clip = VideoFileClip(os.path.join(save_path, "chunk_summaries.mp4"))

    final_clip = concatenate_videoclips(
        [summary_clip] + [get_chunk_clip(v, i) for v, i in zip(videos, images)], method="compose"
    )

    # Write the final video to a file
    output_file = os.path.join(save_path, "video_snippet_concat_summary.mp4")
    final_clip.write_videofile(output_file, codec="libx264", audio_codec="aac")