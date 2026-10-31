from abc import ABC, abstractmethod

class TTSProvider(ABC):
    """
    Abstract interface for Text-to-Speech providers.
    Supports Kokoro-82M self-hosted, Edge-TTS, and browser fallbacks.
    """
    
    @abstractmethod
    async def synthesize(self, text: str, output_path: str) -> str:
        """
        Synthesizes text into audio and saves it at output_path.
        Returns the output_path on success.
        """
        pass
