import asyncio
import base64
import io
import logging
import struct
from dataclasses import dataclass, field
from typing import Callable, Optional

from openai import OpenAI

logger = logging.getLogger(__name__)


@dataclass
class AsrSession:
    session_id: str
    audio_buffer: bytearray = field(default_factory=bytearray)
    on_partial: Optional[Callable] = None
    on_final: Optional[Callable] = None
    on_ready: Optional[Callable] = None
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


def _pcm_to_wav(pcm_bytes: bytes, sample_rate: int = 16000,
                channels: int = 1, bits_per_sample: int = 16) -> bytes:
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


class VoiceAsrService:
    """ASR service backed by MiMo REST API (OpenAI-compatible)."""

    def __init__(self, model: str, api_key: str, language: str = "zh",
                 base_url: str = "https://api.xiaomimimo.com/v1"):
        self.model = model
        self.language = language
        self.api_key = api_key
        self.base_url = base_url
        if not api_key:
            logger.warning(
                "VoiceAsrService initialized with empty mimo_api_key. "
                "ASR calls will likely fail. Set MIMO_API_KEY environment variable."
            )
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self._sessions: dict[str, AsrSession] = {}

    async def start_session(self, session_id: str, on_partial: Callable,
                            on_final: Callable, on_ready: Callable):
        session = AsrSession(
            session_id=session_id,
            on_partial=on_partial,
            on_final=on_final,
            on_ready=on_ready,
        )
        self._sessions[session_id] = session
        if on_ready:
            on_ready()

    async def send_audio(self, session_id: str, audio_bytes: bytes):
        session = self._sessions.get(session_id)
        if session:
            async with session.lock:
                session.audio_buffer.extend(audio_bytes)

    async def stop_session(self, session_id: str):
        self._sessions.pop(session_id, None)

    def is_session_active(self, session_id: str) -> bool:
        return session_id in self._sessions

    def _recognize_sync(self, session_id: str, audio_b64: str) -> Optional[str]:
        """Synchronous ASR call — runs in a thread to avoid blocking the event loop."""
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": [{
                        "type": "input_audio",
                        "input_audio": {
                            "data": f"data:audio/wav;base64,{audio_b64}"
                        }
                    }]
                }],
                extra_body={
                    "asr_options": {"language": self.language}
                },
            )
            text = completion.choices[0].message.content or ""
            return text.strip()
        except Exception:
            logger.exception("MiMo ASR error for session %s", session_id)
            return None

    async def recognize(self, session_id: str) -> Optional[str]:
        """Send buffered audio to MiMo ASR and return the transcription."""
        session = self._sessions.get(session_id)
        if not session:
            return None

        async with session.lock:
            if not session.audio_buffer:
                return None
            pcm_bytes = bytes(session.audio_buffer)
            session.audio_buffer.clear()

        wav_bytes = _pcm_to_wav(pcm_bytes, sample_rate=16000)
        audio_b64 = base64.b64encode(wav_bytes).decode("utf-8")

        text = await asyncio.to_thread(self._recognize_sync, session_id, audio_b64)

        if text and session.on_final:
            session.on_final(text)

        return text
