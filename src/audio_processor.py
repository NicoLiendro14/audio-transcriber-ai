import audioop
import os
import tempfile
import threading
import time
import wave
from datetime import datetime, timedelta
from queue import Queue
from tempfile import NamedTemporaryFile
from typing import Optional, Union
from colorama import Fore, Style
from pydub import AudioSegment as am
import speech_recognition as sr
from src import sr_edited
import io
from src.audio_transcriber import AudioTranscriber, AudioObject
import pyaudiowpatch as pyaudio


class AudioProcessor(object):
    def __init__(self):
        raise NotImplementedError("this is an abstract class")

    def set_transcriber(self, transcriber: AudioTranscriber):
        raise NotImplementedError("this is an abstract class")

    def process_audio(self):
        raise NotImplementedError("this is an abstract class")

    def run(self):
        """
        Runs the audio transcriber by starting recording and processing the audio data.
        """
        raise NotImplementedError("this is an abstract class")

class ProcessorContinue(AudioProcessor):
    def __init__(self):
        self.transcriber: Union[AudioTranscriber, None] = None
        self.transcription = ['']
        self.queue = Queue()

    def set_transcriber(self, transcriber: AudioTranscriber):
        self.transcriber = transcriber

    def transcribe(self):
        while True:
            # Obtiene el nombre de archivo de la cola
            if not self.queue.empty():
                filename:AudioObject = self.queue.get()

                text_transcripted_not_generated = self.transcriber.transcribe(filename)
                full_text = ''.join(segment for segment in text_transcripted_not_generated)
                print(full_text)

                self.transcription.append(full_text)

    def process_audio(self, ):
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

            chunk_duration = 0.1  # Duración de cada chunk en segundos
            stream = p.open(format=pyaudio.paInt16,
                            channels=default_speakers["maxInputChannels"],
                            rate=int(default_speakers["defaultSampleRate"]),
                            frames_per_buffer=int(default_speakers["defaultSampleRate"] * chunk_duration),
                            input=True,
                            input_device_index=default_speakers["index"])

            silence_threshold = 200
            silence_time = 0.5
            RATE = int(default_speakers["defaultSampleRate"])
            CHUNK = int(default_speakers["defaultSampleRate"] * chunk_duration)
            RECORD_SECONDS = 3
            while True:
                frames = []
                silence_counter = 0
                while True:
                    data = stream.read(CHUNK)
                    rms = audioop.rms(data, 2)
                    if rms >= silence_threshold:
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

                wav_path_filename = self.save_wav_file(RATE, default_speakers, frames)

                sound = am.from_file(wav_path_filename, format='wav', frame_rate=RATE)
                sound = sound.set_frame_rate(16000)
                sound.export(wav_path_filename, format='wav')
                audio_obj = AudioObject(file=wav_path_filename)
                self.queue.put(audio_obj)

    def save_wav_file(self, RATE, default_speakers, frames):
        WAVE_OUTPUT_FILENAME = tempfile.mktemp(suffix=".wav")
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(default_speakers["maxInputChannels"])
        wf.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        return WAVE_OUTPUT_FILENAME

    def run(self):
        # Crea los hilos
        listen_thread = threading.Thread(target=self.process_audio)
        transcribe_thread = threading.Thread(target=self.transcribe)

        # Inicia los hilos
        listen_thread.start()
        transcribe_thread.start()

        # Espera a que los hilos terminen
        listen_thread.join()
        transcribe_thread.join()

class ProcessorPhrases(AudioProcessor):
    def __init__(self):
        """
        Initializes the AudioProcessor class.

        """
        self.transcriber = None
        self.data_queue = Queue()
        self.last_sample = bytes()
        self.phrase_time: Optional[datetime] = None
        self.phrase_timeout = 3
        self.record_timeout = 2
        self.recorder = sr_edited.Recognizer()
        self.source = sr_edited.LoopbackOutputAudio()
        self.temp_file = NamedTemporaryFile().name
        self.transcriber: Union[AudioTranscriber, None] = None
        self.transcription = ['']

    def set_transcriber(self, transcriber: AudioTranscriber):
        self.transcriber = transcriber

    def record_callback(self, _, audio: sr.AudioData) -> None:
        """
        Threaded callback function to receive audio data when recordings finish.

        Args:
            _: Unused parameter.
            audio: An AudioData object containing the recorded bytes.
        """
        data = audio.get_raw_data()
        self.data_queue.put(data)

    def start_recording(self) -> None:
        """
        Starts recording audio in the background using a separate thread.
        """
        self.recorder.listen_in_background(self.source, self.record_callback, phrase_time_limit=self.record_timeout)

    def process_audio(self) -> None:
        """
        Processes the recorded audio data and performs real-time transcription.
        """
        while True:
            try:
                now = datetime.utcnow()
                if not self.data_queue.empty():
                    phrase_complete = False
                    if self.phrase_time and now - self.phrase_time > timedelta(seconds=self.phrase_timeout):
                        self.last_sample = bytes()
                        phrase_complete = True

                    self.phrase_time = now

                    while not self.data_queue.empty():
                        data = self.data_queue.get()
                        self.last_sample += data

                    if self.data_queue.empty():
                        self.last_sound_time = time.time()

                    audio_data = sr_edited.AudioData(self.last_sample, self.source.SAMPLE_RATE,
                                                     self.source.SAMPLE_WIDTH)
                    wav_data = io.BytesIO(audio_data.get_wav_data())

                    with open(self.temp_file + ".wav", 'w+b') as f:
                        f.write(wav_data.read())

                    sound = am.from_file(self.temp_file + ".wav", format='wav', frame_rate=self.source.SAMPLE_RATE)
                    sound = sound.set_frame_rate(16000)
                    sound.export(self.temp_file + ".wav", format='wav')

                    audio_obj = AudioObject(file=self.temp_file + ".wav")

                    full_text = self.transcriber.transcribe(audio_obj)
                    try:
                        text = full_text[-1]
                    except IndexError:
                        text = ""

                    if phrase_complete:
                        self.transcription.append(text)
                    else:
                        self.transcription[-1] = text

                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(Fore.GREEN + "Real-Time Transcription: " + Style.RESET_ALL, self.transcription[-1])
                    print('', end='', flush=True)

                    time.sleep(0.0002)
            except KeyboardInterrupt:
                break

    def run(self) -> None:
        """
        Runs the audio transcriber by starting recording and processing the audio data.
        """
        self.start_recording()
        self.process_audio()
