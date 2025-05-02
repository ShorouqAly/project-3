import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from moviepy.editor import VideoFileClip, AudioFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
import shutil
from uuid import uuid4
import tempfile
import logging

app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path for temp files
VIDEO_TEMP_DIR = "temp_videos"
PHOTO_TEMP_DIR = "temp_photos"

# Ensure temporary directories exist
os.makedirs(VIDEO_TEMP_DIR, exist_ok=True)
os.makedirs(PHOTO_TEMP_DIR, exist_ok=True)

def create_summary_video(video_paths, photo_paths, output_path, music_path=None):
    clips = []

    for path in video_paths:
        try:
            logger.info(f"Trying to load video: {path}")
            clip = VideoFileClip(path)
            clips.append(clip)
        except Exception as e:
            logger.error(f"Skipping video {path}: {e}")

    if not clips:
        raise ValueError("No valid video clips to process.")

    final_clip = concatenate_videoclips(clips)

    if music_path:
        try:
            final_clip = final_clip.set_audio(AudioFileClip(music_path))
        except Exception as e:
            logger.error(f"Could not set background music: {e}")

    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

@app.post("/create-video/")
async def create_video(videos: list[UploadFile] = File(...), photos: list[UploadFile] = File(...), music: UploadFile = File(...)):
    # Temp files for videos, photos, and music
    video_paths = []
    photo_paths = []
    temp_video_paths = []
    temp_photo_paths = []
    temp_music_path = None

    # Save video files to temp directory
    try:
        for video in videos:
            video_temp_path = os.path.join(VIDEO_TEMP_DIR, f"{uuid4()}.mp4")
            temp_video_paths.append(video_temp_path)
            with open(video_temp_path, "wb") as f:
                shutil.copyfileobj(video.file, f)
            video_paths.append(video_temp_path)
    except Exception as e:
        logger.error(f"Error saving video files: {e}")
        raise HTTPException(status_code=400, detail="Error saving video files.")

    # Save photo files to temp directory
    try:
        for photo in photos:
            photo_temp_path = os.path.join(PHOTO_TEMP_DIR, f"{uuid4()}.jpg")
            temp_photo_paths.append(photo_temp_path)
            with open(photo_temp_path, "wb") as f:
                shutil.copyfileobj(photo.file, f)
            photo_paths.append(photo_temp_path)
    except Exception as e:
        logger.error(f"Error saving photo files: {e}")
        raise HTTPException(status_code=400, detail="Error saving photo files.")

    # Save music file to temp directory
    try:
        music_temp_path = os.path.join(PHOTO_TEMP_DIR, f"{uuid4()}.mp3")
        temp_music_path = music_temp_path
        with open(music_temp_path, "wb") as f:
            shutil.copyfileobj(music.file, f)
    except Exception as e:
        logger.error(f"Error saving music file: {e}")
        raise HTTPException(status_code=400, detail="Error saving music file.")

    # Create the summary video
    output_path = os.path.join("output_videos", f"{uuid4()}.mp4")
    try:
        create_summary_video(video_paths, photo_paths, output_path, temp_music_path)
    except ValueError as e:
        logger.error(f"Error creating summary video: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    # Clean up temporary files
    for temp_video in temp_video_paths:
        os.remove(temp_video)
    for temp_photo in temp_photo_paths:
        os.remove(temp_photo)
    os.remove(temp_music_path)

    return {"message": "Video created successfully", "output_video": output_path}
