"""
LLM Registry

This module provides specific LLM model getter functions for different AI models.
Each function returns a configured model instance with only provider and model name.
Runtime settings like temperature, max_tokens should be set during agent.run() via model_settings.

Usage:
    from ai_agents.core.llm_registry import (
        get_gpt41_mini, get_gpt41, get_gemini25_pro, get_gemini25_flash_lite, get_gemini25_flash,
        get_gpt_oss_20b, get_gpt_oss_120b, get_grok_3_mini, get_grok_2_1212,
        get_kimi_k2, get_deepseek_chat_v31, get_glm_45
    )

    model = get_gpt41_mini()  # Returns a configured GPT-4.1 Mini model
    model = get_gpt_oss_20b()  # Returns a configured GPT OSS 20B model
    
    # Runtime settings are set during agent.run()
    result = await agent.run(
        "prompt text",
        model_settings={'temperature': 0.1, 'max_tokens': 4000}
    )
"""

from functools import lru_cache
from pydantic_ai.models import Model
from ai_agents.core.config import settings
from ai_agents.core.llm_factory import create_fallback_model


@lru_cache(maxsize=32)
def get_gpt41_mini() -> Model:
    """
    Get GPT-4.1 Mini model.
    
    Configuration is read from settings:
    - ai__gpt41_mini__provider
    - ai__gpt41_mini__model_name
    
    Returns:
        Configured GPT-4.1 Mini model instance
    """
    return create_fallback_model(
        primary_model_name=settings.ai__gpt41_mini__model_name,
        primary_provider=settings.ai__gpt41_mini__provider
    )


@lru_cache(maxsize=32) 
def get_gpt41() -> Model:
    """
    Get GPT-4.1 model.
    
    Configuration is read from settings:
    - ai__gpt41__provider
    - ai__gpt41__model_name
    
    Returns:
        Configured GPT-4.1 model instance
    """
    return create_fallback_model(
        primary_model_name=settings.ai__gpt41__model_name,
        primary_provider=settings.ai__gpt41__provider
    )


@lru_cache(maxsize=32)
def get_gpt5() -> Model:
    """
    Get GPT-5 model.
    
    Configuration is read from settings:
    - ai__gpt5__provider
    - ai__gpt5__model_name
    
    Returns:
        Configured GPT-5 model instance
    """
    return create_fallback_model(
        primary_model_name=settings.ai__gpt5__model_name,
        primary_provider=settings.ai__gpt5__provider
    )


@lru_cache(maxsize=32)
def get_gpt5_mini() -> Model:
    """
    Get GPT-5 Mini model.
    
    Configuration is read from settings:
    - ai__gpt5_mini__provider
    - ai__gpt5_mini__model_name
    
    Returns:
        Configured GPT-5 Mini model instance
    """
    return create_fallback_model(
        primary_model_name=settings.ai__gpt5_mini__model_name,
        primary_provider=settings.ai__gpt5_mini__provider
    )


@lru_cache(maxsize=32)
def get_gpt5_chat() -> Model:
    """
    Get GPT-5 Chat model.
    
    Configuration is read from settings:
    - ai__gpt5_chat__provider
    - ai__gpt5_chat__model_name
    
    Returns:
        Configured GPT-5 Chat model instance
    """
    return create_fallback_model(
        primary_model_name=settings.ai__gpt5_chat__model_name,
        primary_provider=settings.ai__gpt5_chat__provider
    )


@lru_cache(maxsize=32)
def get_gemini25_pro() -> Model:
    """
    Get Gemini 2.5 Pro model.
    
    Configuration is read from settings:
    - ai__gemini25_pro__provider
    - ai__gemini25_pro__model_name
    
    Returns:
        Configured Gemini 2.5 Pro model instance
    """
    return create_fallback_model(
        primary_model_name=settings.ai__gemini25_pro__model_name,
        primary_provider=settings.ai__gemini25_pro__provider
    )


@lru_cache(maxsize=32)
def get_claude4_sonnet() -> Model:
    """
    Get Claude-4 Sonnet model.
    
    Configuration is read from settings:
    - ai__claude4_sonnet__provider
    - ai__claude4_sonnet__model_name
    
    Returns:
        Configured Claude-4 Sonnet model instance
    """
    return create_fallback_model(
        primary_model_name=settings.ai__claude4_sonnet__model_name,
        primary_provider=settings.ai__claude4_sonnet__provider
    )


@lru_cache(maxsize=32)
def get_gemini25_flash_lite() -> Model:
    """
    Get Gemini 2.5 Flash Lite model.
    
    Configuration is read from settings:
    - ai__gemini25_flash_lite__provider
    - ai__gemini25_flash_lite__model_name
    
    Returns:
        Configured Gemini 2.5 Flash Lite model instance
    """
    return create_fallback_model(
        primary_model_name=settings.ai__gemini25_flash_lite__model_name,
        primary_provider=settings.ai__gemini25_flash_lite__provider
    )


@lru_cache(maxsize=32)
def get_gemini25_flash() -> Model:
    """
    Get Gemini 2.5 Flash model.

    Configuration is read from settings:
    - ai__gemini25_flash__provider
    - ai__gemini25_flash__model_name

    Returns:
        Configured Gemini 2.5 Flash model instance
    """
    from ai_agents.core.llm_factory import create_llm_model
    return create_llm_model(
        primary_model_name=settings.ai__gemini25_flash__model_name,
        primary_provider=settings.ai__gemini25_flash__provider
    )


@lru_cache(maxsize=32)
def get_gpt_oss_20b() -> Model:
    """
    Get GPT OSS 20B model.

    Configuration is read from settings:
    - ai__gpt_oss_20b__provider
    - ai__gpt_oss_20b__model_name

    Returns:
        Configured GPT OSS 20B model instance
    """
    return create_fallback_model(
        primary_model_name=settings.ai__gpt_oss_20b__model_name,
        primary_provider=settings.ai__gpt_oss_20b__provider
    )


@lru_cache(maxsize=32)
def get_gpt_oss_120b() -> Model:
    """
    Get GPT OSS 120B model.

    Configuration is read from settings:
    - ai__gpt_oss_120b__provider
    - ai__gpt_oss_120b__model_name

    Returns:
        Configured GPT OSS 120B model instance
    """
    return create_fallback_model(
        primary_model_name=settings.ai__gpt_oss_120b__model_name,
        primary_provider=settings.ai__gpt_oss_120b__provider
    )


@lru_cache(maxsize=32)
def get_grok_3_mini() -> Model:
    """
    Get Grok 3 Mini model.

    Configuration is read from settings:
    - ai__grok_3_mini__provider
    - ai__grok_3_mini__model_name

    Returns:
        Configured Grok 3 Mini model instance
    """
    return create_fallback_model(
        primary_model_name=settings.ai__grok_3_mini__model_name,
        primary_provider=settings.ai__grok_3_mini__provider
    )


@lru_cache(maxsize=32)
def get_grok_2_1212() -> Model:
    """
    Get Grok 2 1212 model.

    Configuration is read from settings:
    - ai__grok_2_1212__provider
    - ai__grok_2_1212__model_name

    Returns:
        Configured Grok 2 1212 model instance
    """
    return create_fallback_model(
        primary_model_name=settings.ai__grok_2_1212__model_name,
        primary_provider=settings.ai__grok_2_1212__provider
    )


@lru_cache(maxsize=32)
def get_kimi_k2() -> Model:
    """
    Get Kimi K2 model.

    Configuration is read from settings:
    - ai__kimi_k2__provider
    - ai__kimi_k2__model_name

    Returns:
        Configured Kimi K2 model instance
    """
    return create_fallback_model(
        primary_model_name=settings.ai__kimi_k2__model_name,
        primary_provider=settings.ai__kimi_k2__provider
    )


@lru_cache(maxsize=32)
def get_deepseek_chat_v31() -> Model:
    """
    Get DeepSeek Chat V3.1 model.

    Configuration is read from settings:
    - ai__deepseek_chat_v31__provider
    - ai__deepseek_chat_v31__model_name

    Returns:
        Configured DeepSeek Chat V3.1 model instance
    """
    return create_fallback_model(
        primary_model_name=settings.ai__deepseek_chat_v31__model_name,
        primary_provider=settings.ai__deepseek_chat_v31__provider
    )


@lru_cache(maxsize=32)
def get_glm_45() -> Model:
    """
    Get GLM 4.5 model.

    Configuration is read from settings:
    - ai__glm_45__provider
    - ai__glm_45__model_name

    Returns:
        Configured GLM 4.5 model instance
    """
    return create_fallback_model(
        primary_model_name=settings.ai__glm_45__model_name,
        primary_provider=settings.ai__glm_45__provider
    )