
# import os
# os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"
import moviepy.editor as mpe
my_clip = mpe.VideoFileClip('some_clip.mp4')
audio_background = mpe.AudioFileClip('some_background.mp3')
final_audio = mpe.CompositeAudioClip([my_clip.audio, audio_background])
final_clip = my_clip.set_audio(final_audio)