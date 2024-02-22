import pyaudiowpatch as pyaudio
import wave
import audioop
import tempfile

import scipy
import torch
from faster_whisper import WhisperModel
from browser_service import BrowserService
import webrtcvad
import numpy as np
from scipy.io import wavfile


def get_device(device="cpu"):
    if device == "cpu":
        return device
    if device == "cuda" and torch.cuda.is_available():
        print('CUDA enabled:', torch.cuda.is_available())
        device = "cuda"
        return device


def get_whisper_model(device, model_size="base"):
    model = WhisperModel(model_size, device=get_device(device))
    return model


if __name__ == "__main__":
    browser_service = BrowserService()
    intro_prompt = "Actua como si fueras un ayudante de entrevistas de trabajos de desarrollador Python. Yo te ire pasando mensajes basado en preguntas que me hacen en tiempo real gente de Recursos Humanos, CTOs, Lideres Tecnicos. Tu objetivo es ayudarme con mensajes para que pueda contestar a las preguntas y comentarios que me hacen. Tus ayudas deben ser concisas y efectivas."
    first_message_chatgpt = browser_service.send_response(intro_prompt)

    with pyaudio.PyAudio() as p:
        try:
            wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
        except OSError:
            print("Looks like WASAPI is not available on the system. Exiting...")
            exit()
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
                print(
                    "Default loopback output device not found.\n\nRun `python -m pyaudiowpatch` to check available devices.\nExiting...\n")
                exit()
        print(f"Recording from: ({default_speakers['index']}){default_speakers['name']}")

        silence_counter = []
        chunk_duration = 0.1  # Duración de cada chunk en segundos
        stream = p.open(format=pyaudio.paInt16,
                        channels=default_speakers["maxInputChannels"],
                        rate=int(default_speakers["defaultSampleRate"]),
                        frames_per_buffer=int(default_speakers["defaultSampleRate"] * chunk_duration),
                        input=True,
                        input_device_index=default_speakers["index"])

        print(f"La grabación se está realizando en tiempo real. Presione Ctrl+C para detener.")

        silence_threshold = 200
        silence_time = 0.5
        RATE = int(default_speakers["defaultSampleRate"])
        CHUNK = int(default_speakers["defaultSampleRate"] * chunk_duration)
        RECORD_SECONDS = 10
        is_recording = False
        model = get_whisper_model(device="cuda")
        while True:
            frames = []
            silence_counter = 0
            print("Waiting for sound...")
            while True:
                data = stream.read(CHUNK)
                rms = audioop.rms(data, 2)
                if rms >= silence_threshold:
                    is_recording = True
                    print("Grabando...")
                    break
            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)

                rms = audioop.rms(data, 2)
                # Verifica si el valor RMS es menor que el umbral de silencio
                if rms < silence_threshold:
                    silence_counter += 1
                else:
                    silence_counter = 0

                if silence_counter / (RATE / CHUNK) >= silence_time:
                    break

            WAVE_OUTPUT_FILENAME = tempfile.mktemp(suffix=".wav")
            wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
            wf.setnchannels(default_speakers["maxInputChannels"])
            wf.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()

            segments, info = model.transcribe(WAVE_OUTPUT_FILENAME)

            full_text = ''.join(segment.text for segment in segments)

            print("Transcription Interviewer:")
            print(full_text)
            response_chatgpt_live = browser_service.send_response(full_text)
            print("ChatGPT Response: ", response_chatgpt_live)
