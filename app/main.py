from moviepy.editor import VideoFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips

def create_summary_video(video_paths, photo_paths, output_path, music_path=None):
    clips = []

    for path in video_paths:
        try:
            clip = VideoFileClip(path)
            clips.append(clip)
        except Exception as e:
            print(f"Skipping video {path}: {e}")

    # Add logic to process photo_paths if needed

    if not clips:
        raise ValueError("No valid video clips to process.")

    final_clip = concatenate_videoclips(clips)
    
    if music_path:
        try:
            final_clip = final_clip.set_audio(AudioFileClip(music_path))
        except Exception as e:
            print(f"Could not set background music: {e}")

    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
