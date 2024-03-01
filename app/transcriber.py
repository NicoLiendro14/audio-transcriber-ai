import os
from src.audio_transcriber import WhisperLocal, AudioObject
from video_converter.convert_format import convertir_video_a_mp3


def transcribe_video_mp4(mp4_path):
    mp3_path = os.path.splitext(mp4_path)[0] + ".mp3"
    convertir_video_a_mp3(mp4_path, mp3_path)

    whisper = WhisperLocal(model_size="medium", device="cuda")

    audio = AudioObject(file=mp3_path)

    text_transcripted_not_generated = whisper.transcribe(audio)
    full_text = ''.join(segment for segment in text_transcripted_not_generated)
    del whisper
    try:
        os.remove(mp3_path)
    except Exception as e:
        print(e)

    return full_text
