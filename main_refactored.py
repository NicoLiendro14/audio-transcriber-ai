from threading import Thread
from src.audio_processor import AudioProcessor, ProcessorContinue
from src.server import WebSocketServer
from src.server_front import setup
from src.audio_transcriber import WhisperLocal


def main() -> None:
    thread1 = Thread(target=setup)
    thread1.start()

    audio_processor = ProcessorContinue()

    transcriber = WhisperLocal()
    audio_processor.set_transcriber(transcriber)

    server = WebSocketServer()

    thread = Thread(target=audio_processor.run)
    thread.start()

    server.start(audio_processor.transcription)


if __name__ == "__main__":
    main()
