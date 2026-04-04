# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License

from __future__ import annotations

import hashlib
import logging
from collections import OrderedDict
from collections.abc import Generator
from functools import lru_cache
from threading import Lock
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_deepseek import ChatDeepSeek

from deepresearch.config.llms_config import LLMType, get_llm_configs

logger = logging.getLogger(__name__)

_MAX_LLM_CACHE_SIZE = 24


def _make_llm_instance(
    llm_type: LLMType, streaming: bool = False, max_tokens: int = 8192
) -> ChatDeepSeek:
    """
    Factory function to create a new LLM instance. Wrapped with lru_cache for automatic eviction.
    Cache key is the tuple (llm_type, streaming, max_tokens).
    """
    try:
        llm_config = get_llm_configs()[llm_type]
    except KeyError as e:
        raise KeyError(f"LLM configuration for '{llm_type}' not found") from e

    config_dict = llm_config.__dict__.copy()
    config_dict["streaming"] = streaming
    config_dict["max_tokens"] = max_tokens
    config_dict["temperature"] = 0.6

    return ChatDeepSeek(**config_dict)


_cached_make_llm_instance = lru_cache(maxsize=_MAX_LLM_CACHE_SIZE)(_make_llm_instance)


def _get_llm_instance(
    llm_type: LLMType, streaming: bool = False, max_tokens: int = 8192
) -> ChatDeepSeek:
    """
    Retrieves a cached ChatOpenAI instance or creates a new one with specified parameters.
    Uses LRU eviction policy to prevent unbounded memory growth (max 24 instances).

    Args:
        llm_type: Type of LLM to retrieve (must be defined in LLMType)
        streaming: Whether to enable streaming mode
        max_tokens: Maximum number of tokens to generate, defaults to 8192 (8K)

    Returns:
        Configured ChatOpenAI instance

    Raises:
        KeyError: If specified LLMType has no configuration
    """
    return _cached_make_llm_instance(llm_type, streaming, max_tokens)


_MAX_RESPONSE_CACHE_SIZE = 100


class ThreadSafeLRUCache:
    """Thread-safe LRU cache for LLM responses with O(1) operations."""

    def __init__(self, max_size: int = _MAX_RESPONSE_CACHE_SIZE):
        self._cache: OrderedDict[str, str] = OrderedDict()
        self._lock = Lock()
        self._max_size = max_size
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> str | None:
        """Get item from cache, moving it to end (most recently used)."""
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                self._hits += 1
                return self._cache[key]
            self._misses += 1
            return None

    def set(self, key: str, value: str) -> None:
        """Set item in cache, evicting oldest if at capacity."""
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                self._cache[key] = value
            else:
                self._cache[key] = value
                while len(self._cache) > self._max_size:
                    self._cache.popitem(last=False)

    def clear(self) -> None:
        """Clear the cache."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total = self._hits + self._misses
            hit_rate = self._hits / total if total > 0 else 0
            return {
                "size": len(self._cache),
                "max_size": self._max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": hit_rate,
            }


_response_cache = ThreadSafeLRUCache(_MAX_RESPONSE_CACHE_SIZE)


def _message_hash(messages: list[HumanMessage | AIMessage | SystemMessage]) -> str:
    """Generate a stable hash for a list of messages using SHA-256."""
    content = "".join([f"{msg.type}:{msg.content}" for msg in messages])
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:32]


def _cached_llm_response(
    llm_type: LLMType,
    message_hash: str,
    stream: bool,
    messages: list[HumanMessage | AIMessage | SystemMessage],
) -> Generator[str] | str:
    """Cached LLM response generation"""
    llm = _get_llm_instance(llm_type, stream)
    if stream:
        return _stream_llm_response(llm, messages)
    else:
        return _non_stream_llm_response(llm, messages)


def llm(
    llm_type: LLMType,
    messages: list[HumanMessage | AIMessage | SystemMessage],
    stream: bool = False,
) -> Generator[str] | str:
    """
    Generates responses from LLM with support for streaming and non-streaming modes.

    Args:
        llm_type: Type of LLM to use
        messages: List of messages representing the conversation history
        stream: If True, returns response chunks via generator

    Returns:
        - Generator yielding string chunks if stream=True
        - Complete response string if stream=False
    """
    if not messages:
        logger.warning("Empty messages list provided to LLM")
        return "" if not stream else (_ for _ in ())

    if not stream:
        message_hash = _message_hash(messages)
        cache_key = f"{llm_type}:{message_hash}"

        cached = _response_cache.get(cache_key)
        if cached is not None:
            logger.debug(f"Cache hit for LLM response: {llm_type}")
            return cached

        response = _cached_llm_response(llm_type, message_hash, stream, messages)

        if response:
            _response_cache.set(cache_key, response)

        return response
    else:
        llm_instance = _get_llm_instance(llm_type, stream)
        return _stream_llm_response(llm_instance, messages)


def _stream_llm_response(
    llm: ChatDeepSeek, messages: list[HumanMessage | AIMessage | SystemMessage]
) -> Generator[tuple[str, str]]:
    """
    Handles streaming responses from LLM.

    Args:
        llm: ChatDeepSeek instance with streaming enabled
        messages: List of messages representing the conversation history

    Yields:
        Tuples containing (reasoning_content, content) for each response chunk
    """
    if not messages:
        logger.warning("Empty messages list provided to LLM stream")
        return

    try:
        for chunk in llm.stream(messages):
            if not chunk:
                continue
            reasoning_content = ""
            content = ""
            if hasattr(chunk, "additional_kwargs"):
                reasoning_content = chunk.additional_kwargs.get("reasoning_content", "")
            if hasattr(chunk, "content"):
                content = chunk.content
            yield reasoning_content, content
    except Exception as e:
        logger.error(f"LLM streaming error: {e}")


def _non_stream_llm_response(
    llm: ChatDeepSeek, messages: list[HumanMessage | AIMessage | SystemMessage]
) -> str:
    """
    Handles non-streaming responses from LLM.

    Args:
        llm: ChatDeepSeek instance with streaming disabled
        messages: List of messages representing the conversation history

    Returns:
        Complete response string
    """
    if not messages:
        logger.warning("Empty messages list provided to LLM")
        return ""

    try:
        response = llm.invoke(messages)
    except Exception as e:
        logger.error(f"LLM invoke error: {e}")
        return ""

    if not response:
        logger.warning("Empty response from LLM")
        return ""

    reasoning_content = (
        response.additional_kwargs.get("reasoning_content", "")
        if hasattr(response, "additional_kwargs")
        else ""
    )
    content = response.content if hasattr(response, "content") else str(response)

    if reasoning_content:
        return f"<thinking>{reasoning_content}</thinking>\n{content}"
    return content


def get_cache_stats() -> dict[str, Any]:
    """Get cache statistics for monitoring."""
    return _response_cache.get_stats()


def clear_cache() -> None:
    """Clear the response cache."""
    _response_cache.clear()
    _cached_make_llm_instance.cache_clear()


if __name__ == "__main__":
    try:
        conversation = [
            SystemMessage(
                content="You are a physics expert skilled at explaining complex concepts in simple, understandable language."
            ),
            HumanMessage(
                content="Please explain the concept of quantum superposition."
            ),
            AIMessage(
                content="Quantum superposition is a fundamental principle in quantum mechanics, stating that microscopic particles can exist in multiple states simultaneously until measured, at which point they collapse to a definite state."
            ),
        ]

        print("=== Non-streaming Response ===")
        non_stream_response = llm(
            "basic",
            [
                *conversation,
                HumanMessage(content="Can you explain this using an everyday analogy?"),
            ],
            stream=False,
        )
        print(non_stream_response)

        print("\n=== Streaming Response ===")
        for reasoning_content, content in llm(
            "basic",
            [*conversation, HumanMessage(content="What is quantum entanglement then?")],
            stream=True,
        ):
            print(reasoning_content, end="", flush=True)
            print(content, end="", flush=True)

        print("\n=== Cache Stats ===")
        print(get_cache_stats())

    except Exception as e:
        print(f"Error with LLM response: {e}")
