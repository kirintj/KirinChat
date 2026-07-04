import re
import logging
from typing import Callable, List
from dataclasses import dataclass

from kirinchat.settings import app_settings
from kirinchat.core.models.manager import ModelManager

logger = logging.getLogger(__name__)

SENTENCE_BOUNDARY = re.compile(r'[。！？.!?]')


@dataclass
class ChatMessage:
    role: str  # "system" | "user" | "assistant"
    content: str


class VoiceLlmService:
    """Streaming LLM with voice output optimization."""

    def __init__(self, max_chars: int = 120, stream_interval_ms: int = 180,
                 min_chars_delta: int = 12):
        self.max_chars = max_chars
        self.stream_interval_ms = stream_interval_ms
        self.min_chars_delta = min_chars_delta

    async def chat_stream(
        self, messages: List[ChatMessage],
        on_token: Callable,
        on_sentence: Callable,
    ) -> str:
        """Stream LLM response. Calls on_token for each token chunk,
        on_sentence when a sentence boundary is hit. Returns full text."""
        buffer = ""
        sentence_buffer = ""

        llm = ModelManager.get_conversation_model()

        async for chunk in llm.astream([{"role": m.role, "content": m.content} for m in messages]):
            token = chunk.content or ""
            if not token:
                continue
            buffer += token
            sentence_buffer += token

            if len(buffer) >= self.min_chars_delta:
                await on_token(buffer)
                buffer = ""

            match = SENTENCE_BOUNDARY.search(sentence_buffer)
            if match:
                if buffer:
                    await on_token(buffer)
                    buffer = ""
                sentence_text = sentence_buffer[:match.end()]
                sentence_buffer = sentence_buffer[match.end():]
                optimized = self._optimize_for_voice(sentence_text)
                if optimized:
                    await on_sentence(optimized)

        if buffer:
            await on_token(buffer)
        if sentence_buffer.strip():
            optimized = self._optimize_for_voice(sentence_buffer)
            if optimized:
                await on_sentence(optimized)

        return ""

    async def chat(self, messages: List[ChatMessage]) -> str:
        """Non-streaming LLM call."""
        llm = ModelManager.get_conversation_model()
        resp = await llm.ainvoke([{"role": m.role, "content": m.content} for m in messages])
        return resp.content or ""

    def _optimize_for_voice(self, text: str) -> str:
        """Strip markdown, collapse whitespace, truncate to max_chars."""
        text = re.sub(r'[*_`#\[\]()~>]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        if len(text) > self.max_chars:
            cut = text[:self.max_chars]
            for punct in '。！？.!?':
                idx = cut.rfind(punct)
                if idx > self.max_chars // 2:
                    return cut[:idx + 1]
            return cut
        return text
