import tkinter as tk
from threading import Thread
from colorama import Fore, Style
import io
import speech_recognition as sr
import whisper
import torch
from datetime import datetime, timedelta
from queue import Queue
from tempfile import NamedTemporaryFile
from time import sleep
import os
from colorama import Fore, Style

# Variables globales
transcription = ['']
root = None
label = None


def update_transcription():
    global label, transcription
    while True:
        # Actualiza el texto de la etiqueta con la última transcripción
        label.config(text=transcription[-1])
        root.update()


def main_thread():
    global transcription
    # Definir argumentos por defecto
    model = "medium"
    non_english = False
    energy_threshold = 1000
    record_timeout = 2
    phrase_timeout = 3

    # The last time a recording was retreived from the queue.
    phrase_time = None
    # Current raw audio bytes.
    last_sample = bytes()
    # Thread safe Queue for passing data from the threaded recording callback.
    data_queue = Queue()
    # We use SpeechRecognizer to record our audio because it has a nice feauture where it can detect when speech ends.
    recorder = sr.Recognizer()
    recorder.energy_threshold = energy_threshold
    # Definitely do this, dynamic energy compensation lowers the energy threshold dramtically to a point where the SpeechRecognizer never stops recording.
    recorder.dynamic_energy_threshold = True

    # Use the default microphone

    # source = sr.Microphone(sample_rate=16000)
    source = sr.LoopbackOutputAudio(sample_rate=48000, chunk_size=1024)

    # Load / Download model
    # if model != "large" and not non_english:
    #     model = model + ".en"
    audio_model = whisper.load_model(model)

    temp_file = NamedTemporaryFile().name
    #transcription = ['']

    # with source:
    #     recorder.adjust_for_ambient_noise(source)

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

    while True:
        try:
            now = datetime.utcnow()
            # Pull raw recorded audio from the queue.
            if not data_queue.empty():
                phrase_complete = False
                # If enough time has passed between recordings, consider the phrase complete.
                # Clear the current working audio buffer to start over with the new data.
                if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                    last_sample = bytes()
                    phrase_complete = True
                # This is the last time we received new audio data from the queue.
                phrase_time = now

                # Concatenate our current audio data with the latest audio data.
                while not data_queue.empty():
                    data = data_queue.get()
                    last_sample += data

                # Use AudioData to convert the raw data to wav data.
                audio_data = sr.AudioData(last_sample, source.SAMPLE_RATE, source.SAMPLE_WIDTH)
                wav_data = io.BytesIO(audio_data.get_wav_data())

                # Write wav data to the temporary file as bytes.
                with open(temp_file, 'w+b') as f:
                    f.write(wav_data.read())

                # Read the transcription.
                result = audio_model.transcribe(temp_file, fp16=torch.cuda.is_available(), language="es")

                text = result['text'].strip()

                # If we detected a pause between recordings, add a new item to our transcripion.
                # Otherwise edit the existing one.
                if phrase_complete:
                    transcription.append(text)
                else:
                    transcription[-1] = text

                # Clear the console to reprint the updated transcription.
                os.system('cls' if os.name == 'nt' else 'clear')
                # for line in transcription:
                #     print(line)
                print(Fore.GREEN + "Real-Time Transcription: " + Style.RESET_ALL, transcription[-1])
                # Flush stdout.
                print('', end='', flush=True)

                # Infinite loops are bad for processors, must sleep.
                sleep(0.25)
        except KeyboardInterrupt:
            break



def main():
    global root, label
    root = tk.Tk()
    root.title("Transcripción en tiempo real")

    # Crea una etiqueta para mostrar la transcripción
    label = tk.Label(root, text="")
    label.pack(padx=20, pady=20)

    # Crea y ejecuta un hilo para actualizar la transcripción en la interfaz
    update_thread = Thread(target=update_transcription)
    update_thread.daemon = True
    update_thread.start()

    # Crea y ejecuta un hilo para ejecutar la función main()
    main_thread_ = Thread(target=main_thread)
    main_thread_.start()

    # Ejecuta el bucle principal de la interfaz gráfica
    root.mainloop()


if __name__ == "__main__":
    main()
