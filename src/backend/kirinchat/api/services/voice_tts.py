import asyncio
import base64
import logging
import struct
from typing import Optional

from openai import OpenAI

logger = logging.getLogger(__name__)


def pcm_to_wav(pcm_bytes: bytes, sample_rate: int = 24000,
               channels: int = 1, bits_per_sample: int = 16) -> bytes:
    """Convert raw PCM bytes to WAV with a 44-byte header."""
    data_size = len(pcm_bytes)
    byte_rate = sample_rate * channels * bits_per_sample // 8
    block_align = channels * bits_per_sample // 8
    header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF', 36 + data_size, b'WAVE',
        b'fmt ', 16, 1, channels, sample_rate, byte_rate, block_align, bits_per_sample,
        b'data', data_size,
    )
    return header + pcm_bytes


class VoiceTtsService:
    """Synthesizes text to PCM audio via MiMo TTS REST API."""

    def __init__(self, model: str, api_key: str, voice: str = "冰糖",
                 sample_rate: int = 24000, speech_rate: float = 1.0,
                 volume: int = 60, timeout_seconds: int = 8,
                 base_url: str = "https://api.xiaomimimo.com/v1"):
        self.model = model
        self.voice = voice
        self.sample_rate = sample_rate
        self.timeout_seconds = timeout_seconds
        if not api_key:
            logger.warning(
                "VoiceTtsService initialized with empty mimo_api_key. "
                "TTS calls will likely fail. Set MIMO_API_KEY environment variable."
            )
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def _synthesize_sync(self, text: str) -> Optional[bytes]:
        """Synchronous TTS synthesis — runs in a thread."""
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": ""},
                    {"role": "assistant", "content": text},
                ],
                audio={"format": "pcm16", "voice": self.voice},
                stream=True,
            )

            result_pcm = bytearray()
            for chunk in completion:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                audio = getattr(delta, "audio", None)
                if audio and isinstance(audio, dict):
                    pcm_b64 = audio.get("data", "")
                    if pcm_b64:
                        result_pcm.extend(base64.b64decode(pcm_b64))

            return bytes(result_pcm) if result_pcm else None
        except Exception:
            logger.exception("MiMo TTS error")
            return None

    async def synthesize(self, text: str) -> Optional[bytes]:
        """Synthesize text to raw PCM bytes. Returns None on failure."""
        return await asyncio.wait_for(
            asyncio.to_thread(self._synthesize_sync, text),
            timeout=self.timeout_seconds,
        )

    async def synthesize_to_wav(self, text: str) -> Optional[bytes]:
        """Synthesize text to WAV bytes (PCM + 44-byte header)."""
        pcm = await self.synthesize(text)
        if pcm:
            return pcm_to_wav(pcm, sample_rate=self.sample_rate)
        return None
