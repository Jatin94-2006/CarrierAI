from abc import ABC, abstractmethod

class STTProvider(ABC):
    """
    Abstract interface for Speech-to-Text providers.
    Allows hot-swapping between faster-whisper, Groq, and OpenAI via config.
    """
    
    @abstractmethod
    async def transcribe(self, audio_path: str, context_prompt: str = "") -> str:
        """
        Transcribes audio at audio_path into text.
        context_prompt can be populated with project & skill names to improve technical term accuracy.
        """
        pass
