from fastapi import FastAPI, File, UploadFile
from typing import List
from moviepy.editor import VideoFileClip, AudioFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
import os
import shutil

app = FastAPI()

# Utility function to create summary video
def create_summary_video(video_paths, photo_paths, output_path, music_path=None):
    clips = []

    for path in video_paths:
        try:
            print(f"Trying to load video: {path}")
            clip = VideoFileClip(path)
            clips.append(clip)
        except Exception as e:
            print(f"Skipping video {path}: {e}")

    if not clips:
        raise ValueError("No valid video clips to process.")

    final_clip = concatenate_videoclips(clips)

    if music_path:
        try:
            final_clip = final_clip.set_audio(AudioFileClip(music_path))
        except Exception as e:
            print(f"Could not set background music: {e}")

    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

# Endpoint for uploading videos and creating summary video
@app.post("/create-video/")
async def create_video(
    videos: List[UploadFile] = File(...),
    photos: List[UploadFile] = File(...),
    music: UploadFile = File(None)
):
    # Create temporary directories to store files
    video_dir = "temp_videos"
    photo_dir = "temp_photos"
    os.makedirs(video_dir, exist_ok=True)
    os.makedirs(photo_dir, exist_ok=True)

    video_paths = []
    photo_paths = []
    
    try:
        # Save videos
        for video in videos:
            video_path = os.path.join(video_dir, video.filename)
            with open(video_path, "wb") as f:
                shutil.copyfileobj(video.file, f)
            video_paths.append(video_path)

        # Save photos
        for photo in photos:
            photo_path = os.path.join(photo_dir, photo.filename)
            with open(photo_path, "wb") as f:
                shutil.copyfileobj(photo.file, f)
            photo_paths.append(photo_path)

        # Music file (optional)
        music_path = None
        if music:
            music_path = os.path.join("temp_music", music.filename)
            os.makedirs("temp_music", exist_ok=True)
            with open(music_path, "wb") as f:
                shutil.copyfileobj(music.file, f)

        # Output video path
        output_path = "output_video.mp4"

        # Create summary video
        create_summary_video(video_paths, photo_paths, output_path, music_path)

        # Clean up temporary files
        shutil.rmtree(video_dir)
        shutil.rmtree(photo_dir)
        if music_path:
            shutil.rmtree("temp_music")

        return {"message": "Video created successfully", "output_path": output_path}
    
    except Exception as e:
        return {"error": str(e)}
