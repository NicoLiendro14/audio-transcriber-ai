import subprocess
import os


def get_proccess_video(input_video_path, output_video_path):
    ffmpeg_proxy = f"ffmpeg -y -loglevel error -hwaccel cuda -i {input_video_path} -s 1280x720 -b:v 1M -c:v h264_nvenc -rc vbr -tune hq -cq:v 19 -c:a aac -b:a 128k {output_video_path}"
    try:
        subprocess.run(ffmpeg_proxy, shell=True, check=True)
        print(f"\nVideo completado.")
    except subprocess.CalledProcessError as e:
        print(f"Error al crear el Proxy: {e.returncode}")


def convertir_video_a_mp3(video_input_path, audio_output_path):
    try:
        os.remove(audio_output_path)
    except Exception as e:
        print(e)
    comando_ffmpeg = [
        'ffmpeg',
        '-i', video_input_path,
        '-vn',
        '-acodec', 'libmp3lame',
        '-q:a', '0',
        audio_output_path
    ]

    subprocess.run(comando_ffmpeg, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
