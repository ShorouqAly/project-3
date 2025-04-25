from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.video_editor import create_summary_video
import os
import uuid

app = FastAPI()

# ─── CORS MIDDLEWARE ──────────────────────────────────────────────────────────
origins = [
    "https://video-editor-frontend.vercel.app",  # your Vercel frontend URL
    # you can add more origins here if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # or ["*"] to allow all origins (less secure)
    allow_credentials=True,
    allow_methods=["*"],          # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],          # Authorization, Content-Type, etc.
)
# ──────────────────────────────────────────────────────────────────────────────

@app.post("/create-video/")
async def create_video(
    videos: list[UploadFile] = File(...),
    photos: list[UploadFile] = File(default=[]),
    music: UploadFile = File(default=None)
):
    session_id = str(uuid.uuid4())
    temp_dir = f"temp/{session_id}"
    os.makedirs(temp_dir, exist_ok=True)

    video_paths = []
    for vid in videos:
        path = f"{temp_dir}/{vid.filename}"
        with open(path, "wb") as f:
            f.write(await vid.read())
        video_paths.append(path)

    photo_paths = []
    for photo in photos:
        path = f"{temp_dir}/{photo.filename}"
        with open(path, "wb") as f:
            f.write(await photo.read())
        photo_paths.append(path)

    music_path = None
    if music:
        music_path = f"{temp_dir}/{music.filename}"
        with open(music_path, "wb") as f:
            f.write(await music.read())

    output_path = f"app/static/final_{session_id}.mp4"
    create_summary_video(video_paths, photo_paths, output_path, music_path)

    return FileResponse(
        output_path,
        media_type="video/mp4",
        filename="family_summary.mp4"
    )
