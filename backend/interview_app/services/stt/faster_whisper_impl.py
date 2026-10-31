import logging
import asyncio
from interview_app.config import settings
from interview_app.services.stt.base import STTProvider

logger = logging.getLogger(__name__)

class FasterWhisperProvider(STTProvider):
    """
    Local Whisper transcription via faster-whisper.
    """
    def __init__(self):
        self.model = None
        self.model_size = settings.WHISPER_MODEL_SIZE or "small"

    def _load_model(self):
        if self.model is None:
            try:
                from faster_whisper import WhisperModel
                # CPU float32 or int8, GPU cuda float16
                self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
                logger.info(f"Loaded faster-whisper model '{self.model_size}'")
            except Exception as e:
                logger.warning(f"Failed to load faster-whisper: {e}")
                self.model = False

    async def transcribe(self, audio_path: str, context_prompt: str = "") -> str:
        self._load_model()
        if not self.model:
            logger.warning("faster-whisper not available. Returning placeholder transcript.")
            return "Transcript captured from voice answer."

        def _run_sync():
            segments, _ = self.model.transcribe(
                audio_path,
                language="en",
                initial_prompt=context_prompt
            )
            return " ".join([seg.text.strip() for seg in segments])

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _run_sync)
