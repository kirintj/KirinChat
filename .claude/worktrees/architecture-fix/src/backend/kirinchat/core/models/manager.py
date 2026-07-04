import asyncio
import threading
from typing import Dict, Any

from openai import AsyncOpenAI
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from kirinchat.core.models.embedding import EmbeddingModel
from kirinchat.core.models.reason_model import ReasoningModel
from kirinchat.settings import app_settings


class ModelManager:
    _cache: Dict[str, Any] = {}
    _async_lock: asyncio.Lock | None = None
    _sync_lock = threading.Lock()

    @classmethod
    def _get_async_lock(cls) -> asyncio.Lock:
        """延迟初始化 asyncio.Lock（必须在事件循环中调用）"""
        if cls._async_lock is None:
            cls._async_lock = asyncio.Lock()
        return cls._async_lock

    @classmethod
    def get_conversation_model(cls, **kwargs) -> BaseChatModel:
        """获取对话模型（带同步缓存，兼容现有调用）"""
        cache_key = f"conversation_model_{hash(frozenset(kwargs.items()))}"

        with cls._sync_lock:
            if cache_key not in cls._cache:
                conversation_model = app_settings.multi_models.conversation_model
                cls._cache[cache_key] = ChatOpenAI(
                    stream_usage=True,
                    model=conversation_model.model_name,
                    api_key=conversation_model.api_key,
                    base_url=conversation_model.base_url,
                    **kwargs
                )

        return cls._cache[cache_key]

    @classmethod
    async def aget_conversation_model(cls, **kwargs) -> BaseChatModel:
        """获取对话模型（异步版本，带缓存）"""
        cache_key = f"conversation_model_{hash(frozenset(kwargs.items()))}"

        async with cls._get_async_lock():
            if cache_key not in cls._cache:
                conversation_model = app_settings.multi_models.conversation_model
                cls._cache[cache_key] = ChatOpenAI(
                    stream_usage=True,
                    model=conversation_model.model_name,
                    api_key=conversation_model.api_key,
                    base_url=conversation_model.base_url,
                    **kwargs
                )

        return cls._cache[cache_key]

    @classmethod
    def get_tool_invocation_model(cls, **kwargs) -> BaseChatModel:
        """获取工具调用模型（带同步缓存，兼容现有调用）"""
        cache_key = f"tool_call_model_{hash(frozenset(kwargs.items()))}"

        with cls._sync_lock:
            if cache_key not in cls._cache:
                tool_call_model = app_settings.multi_models.tool_call_model
                cls._cache[cache_key] = ChatOpenAI(
                    stream_usage=True,
                    model=tool_call_model.model_name,
                    api_key=tool_call_model.api_key,
                    base_url=tool_call_model.base_url,
                    **kwargs
                )

        return cls._cache[cache_key]

    @classmethod
    async def aget_tool_invocation_model(cls, **kwargs) -> BaseChatModel:
        """获取工具调用模型（异步版本，带缓存）"""
        cache_key = f"tool_call_model_{hash(frozenset(kwargs.items()))}"

        async with cls._get_async_lock():
            if cache_key not in cls._cache:
                tool_call_model = app_settings.multi_models.tool_call_model
                cls._cache[cache_key] = ChatOpenAI(
                    stream_usage=True,
                    model=tool_call_model.model_name,
                    api_key=tool_call_model.api_key,
                    base_url=tool_call_model.base_url,
                    **kwargs
                )

        return cls._cache[cache_key]

    @classmethod
    def clear_cache(cls):
        """清空缓存（用于配置更新后，同步版本）"""
        with cls._sync_lock:
            cls._cache.clear()

    @classmethod
    async def aclear_cache(cls):
        """清空缓存（用于配置更新后，异步版本）"""
        async with cls._get_async_lock():
            cls._cache.clear()

    @classmethod
    def get_reasoning_model(cls) -> ReasoningModel:
        reasoning_model = app_settings.multi_models.reasoning_model

        return ReasoningModel(
            model_name=reasoning_model.model_name,
            api_key=reasoning_model.api_key,
            base_url=reasoning_model.base_url
        )

    @classmethod
    def get_lingseek_intent_model(cls, **kwargs) -> BaseChatModel:
        lingseek_intent_model = app_settings.multi_models.tool_call_model

        return ChatOpenAI(
            stream_usage=True,
            model=lingseek_intent_model.model_name,
            api_key=lingseek_intent_model.api_key,
            base_url=lingseek_intent_model.base_url
        )

    @classmethod
    def get_qwen_vl_model(cls) -> BaseChatModel:
        qwen_vl_model = app_settings.multi_models.qwen_vl

        return ChatOpenAI(
            stream_usage=True,
            model=qwen_vl_model.model_name,
            api_key=qwen_vl_model.api_key,
            base_url=qwen_vl_model.base_url
        )

    @classmethod
    def get_user_model(cls, **kwargs) -> BaseChatModel:
        user_model = kwargs

        return ChatOpenAI(
            stream_usage=True,
            model=user_model.get("model"),
            api_key=user_model.get("api_key"),
            base_url=user_model.get("base_url")
        )

    @classmethod
    def get_embedding_openai_model(cls) -> AsyncOpenAI:
        """以ChatOpenAI的形式输出"""
        embedding_model = app_settings.multi_models.embedding

        return AsyncOpenAI(
            base_url=embedding_model.base_url,
            api_key=embedding_model.api_key
        )

    @classmethod
    def get_embedding_model(cls) -> EmbeddingModel:
        embedding_model = app_settings.multi_models.embedding

        return EmbeddingModel(
            model=embedding_model.model_name,
            base_url=embedding_model.base_url,
            api_key=embedding_model.api_key
        )
