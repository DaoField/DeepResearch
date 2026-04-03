# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License

from typing import Generator, Union, Dict, List
from functools import lru_cache
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_deepseek import ChatDeepSeek

from src.config.llms_config import LLMType, llm_configs
import logging

logger = logging.getLogger(__name__)

# Maximum number of cached LLM instances (prevents unbounded memory growth)
_MAX_LLM_CACHE_SIZE = 24


def _make_llm_instance(llm_type: LLMType,
                       streaming: bool = False,
                       max_tokens: int = 8192) -> ChatDeepSeek:
    """
    Factory function to create a new LLM instance. Wrapped with lru_cache for automatic eviction.
    Cache key is the tuple (llm_type, streaming, max_tokens).
    """
    try:
        llm_config = llm_configs[llm_type]
    except KeyError as e:
        raise KeyError(f"LLM configuration for '{llm_type}' not found") from e

    config_dict = llm_config.__dict__.copy()
    config_dict["streaming"] = streaming
    config_dict["max_tokens"] = max_tokens
    config_dict["temperature"] = 0.6

    return ChatDeepSeek(**config_dict)


# Apply LRU cache to the factory function - auto-evicts least recently used when cache is full
_cached_make_llm_instance = lru_cache(maxsize=_MAX_LLM_CACHE_SIZE)(_make_llm_instance)


def _get_llm_instance(llm_type: LLMType,
                      streaming: bool = False,
                      max_tokens: int = 8192) -> ChatDeepSeek:
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


def llm(
        llm_type: LLMType,
        messages: List[Union[HumanMessage, AIMessage, SystemMessage]],
        stream: bool = False
) -> Union[Generator[str, None, None], str]:
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
    llm = _get_llm_instance(llm_type, stream)
    if stream:
        return _stream_llm_response(llm, messages)
    else:
        return _non_stream_llm_response(llm, messages)


def _stream_llm_response(llm: ChatDeepSeek, messages: List[Union[HumanMessage, AIMessage, SystemMessage]]) -> Generator[tuple[str, str], None, None]:
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
        
    # Stream responses and process chunks
    try:
        for chunk in llm.stream(messages):
            if not chunk:
                continue
            reasoning_content = ""
            content = ""
            if hasattr(chunk, 'additional_kwargs'):
                reasoning_content = chunk.additional_kwargs.get("reasoning_content", "")
            if hasattr(chunk, 'content'):
                content = chunk.content
            yield reasoning_content, content
    except Exception as e:
        logger.error(f"LLM streaming error: {e}")


def _non_stream_llm_response(llm: ChatDeepSeek, messages: List[Union[HumanMessage, AIMessage, SystemMessage]]) -> str:
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
        
    reasoning_content = response.additional_kwargs.get("reasoning_content", "") if hasattr(response, 'additional_kwargs') else ""
    content = response.content if hasattr(response, 'content') else str(response)
    
    if reasoning_content:
        return f"<thinking>{reasoning_content}</thinking>\n{content}"
    return content


if __name__ == "__main__":
    try:
        # Example conversation message list
        conversation = [
            SystemMessage(
                content="You are a physics expert skilled at explaining complex concepts in simple, understandable language."),
            HumanMessage(content="Please explain the concept of quantum superposition."),
            AIMessage(
                content="Quantum superposition is a fundamental principle in quantum mechanics, stating that microscopic particles can exist in multiple states simultaneously until measured, at which point they collapse to a definite state."),
        ]

        # Demonstrate non-streaming response (continuing the conversation)
        print("=== Non-streaming Response ===")
        non_stream_response = llm(
            "basic",
            [*conversation, HumanMessage(content="Can you explain this using an everyday analogy?")],
            stream=False
        )
        print(non_stream_response)

        # Demonstrate streaming response
        print("\n=== Streaming Response ===")
        for reasoning_content, content in llm(
                "basic",
                [*conversation, HumanMessage(content="What is quantum entanglement then?")],
                stream=True
        ):
            print(reasoning_content, end="", flush=True)
            print(content, end="", flush=True)

    except Exception as e:
        print(f"Error with LLM response: {e}")
