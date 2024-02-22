import pyaudiowpatch as pyaudio
import wave
import audioop
import tempfile
from faster_whisper import WhisperModel
import torch
import threading

print('CUDA enabled:', torch.cuda.is_available())
model_size = "base"
model = WhisperModel(model_size, device="cuda")

chunk_duration = 0.1  # Duración de cada chunk en segundos
WAVE_OUTPUT_FILENAME = "test.wav"

def record_audio(stream, frames, silence_counter, silence_threshold, silence_time, RATE, CHUNK, RECORD_SECONDS):
    while True:
        frames_chunk = []

        print("Esperando sonido...")
        while True:
            data = stream.read(CHUNK)
            rms = audioop.rms(data, 2)
            if rms >= silence_threshold:
                print("Grabando...")
                break

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames_chunk.append(data)

            rms = audioop.rms(data, 2)
            # Verifica si el valor RMS es menor que el umbral de silencio
            if rms < silence_threshold:
                silence_counter += 1
            else:
                silence_counter = 0

            if silence_counter / (RATE / CHUNK) >= silence_time:
                break

        frames.extend(frames_chunk)

def transcribe_audio(frames, model):
    while True:
        if len(frames) > 0:
            frames_chunk = frames[:]
            frames.clear()

            WAVE_OUTPUT_FILENAME = tempfile.mktemp(suffix=".wav")

            with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
                wf.setnchannels(default_speakers["maxInputChannels"])
                wf.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames_chunk))

            segments, info = model.transcribe(WAVE_OUTPUT_FILENAME)
            full_text = ''.join(segment.text for segment in segments)

            print("Transcription Interviewer:")
            print(full_text)

if __name__ == "__main__":
    with pyaudio.PyAudio() as p:
        # Resto del código...

        frames = []
        silence_counter = 0

        try:
            # Get default WASAPI info
            wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
        except OSError:
            print("Looks like WASAPI is not available on the system. Exiting...")
            exit()

        # Get default WASAPI speakers
        default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
        if not default_speakers["isLoopbackDevice"]:
            for loopback in p.get_loopback_device_info_generator():
                """
                Try to find loopback device with same name(and [Loopback suffix]).
                Unfortunately, this is the most adequate way at the moment.
                """
                if default_speakers["name"] in loopback["name"]:
                    default_speakers = loopback
                    break
            else:
                print("Default loopback output device not found.\n\nRun `python -m pyaudiowpatch` to check available devices.\nExiting...\n")
                exit()
        stream = p.open(format=pyaudio.paInt16,
                        channels=default_speakers["maxInputChannels"],
                        rate=int(default_speakers["defaultSampleRate"]),
                        frames_per_buffer=int(default_speakers["defaultSampleRate"] * chunk_duration),
                        input=True,
                        input_device_index=default_speakers["index"])

        print(f"La grabación se está realizando en tiempo real. Presione Ctrl+C para detener.")

        silence_threshold = 300
        silence_time = 1
        RATE = int(default_speakers["defaultSampleRate"])
        CHUNK = int(default_speakers["defaultSampleRate"] * chunk_duration)
        RECORD_SECONDS = 7

        record_thread = threading.Thread(target=record_audio, args=(stream, frames, silence_counter, silence_threshold, silence_time, RATE, CHUNK, RECORD_SECONDS))
        record_thread.start()

        transcribe_thread = threading.Thread(target=transcribe_audio, args=(frames, model))
        transcribe_thread.start()

        record_thread.join()
        transcribe_thread.join()
