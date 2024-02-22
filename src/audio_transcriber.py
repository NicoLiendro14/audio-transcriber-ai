from typing import Any, Optional, List

import torch
from faster_whisper import WhisperModel

class AudioObject:
    def __init__(self,  file: Optional[str], audio: Optional[Any] = None,):
        self.audio = audio
        self.file =  file

class AudioTranscriber(object):
    def __init__(self):
        raise NotImplementedError("this is an abstract class")

    def transcribe(self, audio):
        raise NotImplementedError("this is an abstract class")

class WhisperLocal(AudioTranscriber):
    def __init__(self, model_size:str = "base", device:str = "cpu"):
        self.audio_model = self._get_whisper_model(model_size, device)

    def get_device(self, device: str) -> str:
        """
        Gets the device to use for computation.

        Args:
            device: The desired device ("cpu" or "cuda").

        Returns:
            The selected device ("cpu" or "cuda").
        """
        if device == "cpu":
            return device
        if device == "cuda" and torch.cuda.is_available():
            print('CUDA enabled:', torch.cuda.is_available())
            device = "cuda"
            return device
        else:
            return "cpu"

    def _get_whisper_model(self, model_size: str, device: str) -> WhisperModel:
        """
        Gets the Whisper model.

        Args:
            model_size: The size of the Whisper model to use.
            device: The device to use for computation.

        Returns:
            The initialized WhisperModel object.
        """
        device = self.get_device(device)
        model = WhisperModel(model_size, device=device)
        return model

    def transcribe(self, audio: AudioObject) -> List[str]:
        segments, info = self.audio_model.transcribe(audio.file, language="es")
        full_text = [segment.text for segment in segments]
        return full_text