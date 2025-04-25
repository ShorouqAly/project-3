from moviepy.editor import VideoFileClip, concatenate_videoclips, ImageClip, AudioFileClip

def create_summary_video(video_paths, photo_paths, output_path, music_path=None, target_duration=300):
    clips = []

    for path in video_paths:
        try:
            clip = VideoFileClip(path).subclip(0, min(5, VideoFileClip(path).duration))
            clips.append(clip)
        except Exception as e:
            print(f"Skipping video {path}: {e}")

    for path in photo_paths:
        try:
            clip = ImageClip(path).set_duration(3).fadein(0.5).fadeout(0.5)
            clips.append(clip)
        except Exception as e:
            print(f"Skipping photo {path}: {e}")

    clips = sorted(clips, key=lambda c: c.duration)
    total_time = 0
    final_clips = []
    for c in clips:
        if total_time + c.duration <= target_duration:
            final_clips.append(c)
            total_time += c.duration
        else:
            break

    final = concatenate_videoclips(final_clips, method="compose")

    if music_path:
        try:
            audio = AudioFileClip(music_path).subclip(0, final.duration)
            final = final.set_audio(audio)
        except:
            print("Failed to add background music")

    final.write_videofile(output_path, codec="libx264", fps=24)
