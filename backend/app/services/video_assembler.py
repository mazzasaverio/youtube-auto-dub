from moviepy.editor import VideoFileClip, AudioFileClip


def merge_audio_with_video(video_path: str, audio_path: str, output_path: str):
    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)
    final_clip = video_clip.set_audio(audio_clip)
    final_clip.write_videofile(output_path)
