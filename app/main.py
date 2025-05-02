from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
from moviepy.editor import VideoFileClip, AudioFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins (for testing, can be restricted later)
    allow_credentials=True,
    allow_methods=["*"],  # allow all methods like GET, POST, etc.
    allow_headers=["*"],  # allow all headers
)

@app.post("/create-video/")
async def create_video(
    videos: list[UploadFile] = File(...),
    photos: list[UploadFile] = File(default=[]),
    music: UploadFile = File(default=None)
):
    session_id = str(uuid.uuid4())
    os.makedirs(f"temp/{session_id}", exist_ok=True)

    video_paths = []
    photo_paths = []
    music_path = None

    # Save uploaded video files
    for vid in videos:
        path = f"temp/{session_id}/{vid.filename}"
        with open(path, "wb") as f:
            f.write(await vid.read())
        video_paths.append(path)

    # Save uploaded photo files
    for photo in photos:
        path = f"temp/{session_id}/{photo.filename}"
        with open(path, "wb") as f:
            f.write(await photo.read())
        photo_paths.append(path)

    # Save uploaded music file
    if music:
        music_path = f"temp/{session_id}/{music.filename}"
        with open(music_path, "wb") as f:
            f.write(await music.read())

    # Ensure the app/static directory exists before saving the output video
    output_dir = "app/static"
    os.makedirs(output_dir, exist_ok=True)

    output_path = f"{output_dir}/final_{session_id}.mp4"
    create_summary_video(video_paths, photo_paths, output_path, music_path)

    return FileResponse(output_path, media_type="video/mp4", filename="family_summary.mp4")


def create_summary_video(video_paths, photo_paths, output_path, music_path=None):
    clips = []

    for path in video_paths:
        try:
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
