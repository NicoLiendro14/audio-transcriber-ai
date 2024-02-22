import sys
import time

from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtCore import Qt, QTimer
from threading import Thread
import io
import speech_recognition as sr
import torch
from datetime import datetime, timedelta
from queue import Queue
from tempfile import NamedTemporaryFile
from time import sleep

from colorama import Fore, Style
from faster_whisper import WhisperModel


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


def set_all_variables():
    global transcription
    model = "medium"
    energy_threshold = 1000
    record_timeout = 2
    phrase_timeout = 3
    phrase_time = None
    last_sample = bytes()
    data_queue = Queue()
    recorder = sr.Recognizer()
    recorder.energy_threshold = energy_threshold
    recorder.dynamic_energy_threshold = True
    source = sr.LoopbackOutputAudio(sample_rate=48000, chunk_size=1024)
    audio_model = get_whisper_model(device="cuda", model_size=model)
    temp_file = NamedTemporaryFile().name

    return audio_model, data_queue, last_sample, phrase_time, phrase_timeout, record_timeout, recorder, source, temp_file


transcription = ['']
audio_model, data_queue, last_sample, phrase_time, phrase_timeout, record_timeout, recorder, source, temp_file = set_all_variables()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Transcription")
        self.setGeometry(0, 0, 600, 200)  # Ajusta el tamaño de la ventana
        self.setStyleSheet("background-color: black;")  # Establece el fondo negro

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)  # Permite el salto de línea en el QLabel

        font = QFont()
        font.setBold(True)
        font.setPointSize(24)
        self.label.setFont(font)

        palette = QPalette()
        palette.setColor(QPalette.Foreground, QColor(255, 255, 0, 200))  # Fuente amarilla opaca
        self.label.setPalette(palette)

        self.setCentralWidget(self.label)

    def update_transcription(self):
        while True:
            if self.label.text() != transcription[-1] or len(transcription[-1]) > 5:
                self.label.setText(transcription[-1])
            else:
                self.label.setText('')
            QApplication.processEvents()

    @staticmethod
    def main_thread():
        global audio_model, data_queue, last_sample, phrase_time, phrase_timeout, record_timeout, recorder, source, temp_file

        def record_callback(_, audio: sr.AudioData) -> None:
            """
            Threaded callback function to recieve audio data when recordings finish.
            audio: An AudioData containing the recorded bytes.
            """
            # Grab the raw bytes and push it into the thread safe queue.
            data = audio.get_raw_data()
            data_queue.put(data)

        # Create a background thread that will pass us raw audio bytes.
        # We could do this manually but SpeechRecognizer provides a nice helper.
        recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)

        # Cue the user that we're ready to go.
        print("Model loaded.\n")

        last_sound_time = time.time()
        silence_printed = False
        while True:
            try:
                if not data_queue.empty():
                    last_sound_time = time.time()
                    if silence_printed:
                        silence_printed = False
                if time.time() - last_sound_time > 7:
                    if not silence_printed:
                        #print("Hubo un silencio")
                        silence_printed = True

                now = datetime.utcnow()
                # Pull raw recorded audio from the queue.
                if not data_queue.empty():
                    phrase_complete = False
                    # If enough time has passed between recordings, consider the phrase complete.
                    # Clear the current working audio buffer to start over with the new data.
                    if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                        last_sample = bytes()
                        phrase_complete = True
                        print("Hubo un silencio")
                    # This is the last time we received new audio data from the queue.
                    phrase_time = now

                    # Concatenate our current audio data with the latest audio data.
                    while not data_queue.empty():
                        data = data_queue.get()
                        last_sample += data

                    if data_queue.empty():
                        last_sound_time = time.time()

                    # Use AudioData to convert the raw data to wav data.
                    audio_data = sr.AudioData(last_sample, source.SAMPLE_RATE, source.SAMPLE_WIDTH)
                    wav_data = io.BytesIO(audio_data.get_wav_data())

                    # Write wav data to the temporary file as bytes.
                    with open(temp_file, 'w+b') as f:
                        f.write(wav_data.read())

                    # Read the transcription.
                    segments, info = audio_model.transcribe(temp_file, language="es")
                    # full_text = ''.join(segment.text for segment in segments)
                    full_text = []
                    for segment in segments:
                        full_text.append(segment.text)
                    try:
                        text = full_text[-1]
                    except IndexError:
                        text = ""
                    # If we detected a pause between recordings, add a new item to our transcripion.
                    # Otherwise edit the existing one.
                    if phrase_complete:
                        transcription.append(text)
                    else:
                        transcription[-1] = text

                    # Clear the console to reprint the updated transcription.
                    # os.system('cls' if os.name == 'nt' else 'clear')
                    # for line in transcription:
                    #     print(line)
                    # print(Fore.GREEN + "Real-Time Transcription: " + Style.RESET_ALL, transcription[-1])
                    # Flush stdout.
                    # print('', end='', flush=True)

                    # Infinite loops are bad for processors, must sleep.
                    sleep(0.25)
            except KeyboardInterrupt:
                break


def main():
    global transcription
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    # Crea y ejecuta un hilo para actualizar la transcripción en la interfaz
    update_thread = Thread(target=window.update_transcription)
    update_thread.daemon = True
    update_thread.start()

    # Crea y ejecuta un hilo para ejecutar la función main()
    main_thread = Thread(target=window.main_thread)
    main_thread.start()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
