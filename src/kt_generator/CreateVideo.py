import numpy as np
from moviepy.editor import *
import os
from loguru import logger


def circular_mask(width, height):
    center_x = width // 2
    center_y = height // 2
    radius = min(center_x, center_y)

    mask = np.zeros((height, width), dtype=bool)
    y, x = np.ogrid[:height, :width]
    mask = (x - center_x) ** 2 + (y - center_y) ** 2 <= radius**2
    return mask


def create_circular_video(video, video_path):
    # Apply the circular mask to the video frames
    masked_frames = [
        frame * circular_mask(video.w, video.h)[:, :, np.newaxis] for frame in video.iter_frames()
    ]

    # Convert the masked frames into a VideoClip
    video_with_mask = ImageSequenceClip(masked_frames, fps=video.fps)

    # Load the audio from the original video
    audio = AudioFileClip(video_path)

    # Combine the masked video with the original audio
    video_with_mask = video_with_mask.set_audio(audio)
    return video_with_mask


def get_chunk_clip(video_path, image_path):
    video = VideoFileClip(video_path)
    image = ImageClip(image_path)

    video = video.resize(0.7)

    # Set the duration of the image clip to match the video duration
    image = image.set_duration(video.duration)

    # Convert the masked frames into a VideoClip
    video_with_mask = create_circular_video(video, video_path)

    # Create a clips array with the video (with circular mask) on the left and the image on the right
    final_clip = clips_array([[image, video_with_mask]])
    # final_clip.fps = video.fps
    return final_clip


def stitch_video(save_path, video_paths, image_paths):
    logger.info("Stitching video and images together...")
    # summary_video_path = os.path.join(save_path, "chunk_summaries.mp4")
    # summary_clip = VideoFileClip(summary_video_path)

    # summary_clip_circle = create_circular_video(summary_clip, summary_video_path)

    final_clip = concatenate_videoclips(
        # [summary_clip_circle] + 
        [get_chunk_clip(v, i) for v, i in zip(video_paths, image_paths)],
        method="compose",
    )

    # Write the final video to a file
    output_file = os.path.join(save_path, "video_snippet_concat_summary.mp4")
    final_clip.write_videofile(output_file, codec="libx264", audio_codec="aac")

    print("Video and image stitching with circular mask complete.")


if __name__ == "__main__":
    save_path = "./kt_gen_jerry_response"
    videos = [os.path.join(save_path, f"chunk_{i}.mp4") for i in range(14)]
    images = [os.path.join(save_path, f"image_{i}.png") for i in range(14)]
    stitch_video(save_path, videos, images)
