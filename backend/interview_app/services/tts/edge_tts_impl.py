import os
import logging
from interview_app.config import settings
from interview_app.services.tts.base import TTSProvider

logger = logging.getLogger(__name__)

class EdgeTTSProvider(TTSProvider):
    """
    High-fidelity neural TTS using edge-tts.
    """
    def __init__(self):
        self.voice = settings.TTS_VOICE or "en-US-GuyNeural"

    async def synthesize(self, text: str, output_path: str) -> str:
        try:
            import edge_tts
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(output_path)
            return output_path
        except Exception as e:
            logger.error(f"EdgeTTS synthesis failed: {e}. Writing placeholder audio file.")
            # Create a silent/empty file so the endpoint does not crash
            with open(output_path, "wb") as f:
                f.write(b"")
            return output_path
