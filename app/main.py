import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from app.video_editor import create_summary_video
import uuid

app = FastAPI()

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

    for vid in videos:
        path = f"temp/{session_id}/{vid.filename}"
        with open(path, "wb") as f:
            f.write(await vid.read())
        video_paths.append(path)

    for photo in photos:
        path = f"temp/{session_id}/{photo.filename}"
        with open(path, "wb") as f:
            f.write(await photo.read())
        photo_paths.append(path)

    if music:
        music_path = f"temp/{session_id}/{music.filename}"
        with open(music_path, "wb") as f:
            f.write(await music.read())

    # Ensure the app/static directory exists before saving the output
    output_dir = "app/static"
    os.makedirs(output_dir, exist_ok=True)

    output_path = f"{output_dir}/final_{session_id}.mp4"
    create_summary_video(video_paths, photo_paths, output_path, music_path)

    return FileResponse(output_path, media_type="video/mp4", filename="family_summary.mp4")
