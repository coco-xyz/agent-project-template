"""
LLM Factory

Simple factory function to create LLM models based on provider and model name.
Also supports creating FallbackModel instances for improved reliability.
"""
from typing import List, Optional
from pydantic_ai.models import Model
from pydantic_ai.models.fallback import FallbackModel
from .config import settings
from .exceptions import InternalServiceException
from .error_codes import InternalServiceErrorCode


def create_llm_model(model_name: str, provider: str) -> Model:
    """
    Create an LLM model instance based on provider and model name.
    
    Args:
        model_name (str): Model name, e.g. 'gpt-4o', 'claude-3-5-sonnet'
        provider (str): Provider name ('openai', 'google', 'openrouter', 'anthropic')
        
    Returns:
        Model: The LLM model instance
        
    Raises:
        InternalServiceException: If provider is unsupported or model creation fails
    """
    try:
        if provider == 'openai':
            return _create_openai_model(model_name)
        elif provider == 'google':
            return _create_google_model(model_name)
        elif provider == 'openrouter':
            return _create_openrouter_model(model_name)
        elif provider == 'anthropic':
            return _create_anthropic_model(model_name)
        else:
            raise InternalServiceException(
                InternalServiceErrorCode.SERVICE_INIT_FAILED, 
                detail=f"Unsupported provider: {provider}"
            )
    except InternalServiceException:
        raise
    except Exception as e:
        raise InternalServiceException(
            InternalServiceErrorCode.SERVICE_INIT_FAILED, 
            detail=f"Failed to create model {model_name} with provider {provider}: {str(e)}"
        ) from e


def _create_openai_model(model_name: str) -> Model:
    """Create OpenAI model instance."""
    from pydantic_ai.models.openai import OpenAIChatModel
    from pydantic_ai.providers.openai import OpenAIProvider
    
    provider = OpenAIProvider(api_key=settings.ai__openai_api_key)
    return OpenAIChatModel(model_name, provider=provider)


def _create_google_model(model_name: str) -> Model:
    """Create Google model instance."""
    from pydantic_ai.models.google import GoogleModel
    from pydantic_ai.providers.google import GoogleProvider
    
    provider = GoogleProvider(api_key=settings.ai__google_api_key)
    return GoogleModel(model_name, provider=provider)


def _create_openrouter_model(model_name: str) -> Model:
    """Create OpenRouter model instance."""
    from pydantic_ai.models.openai import OpenAIChatModel
    from pydantic_ai.providers.openrouter import OpenRouterProvider
    
    provider = OpenRouterProvider(api_key=settings.ai__openrouter_api_key)
    return OpenAIChatModel(model_name, provider=provider)


def _create_anthropic_model(model_name: str) -> Model:
    """Create Anthropic model instance."""
    from pydantic_ai.models.anthropic import AnthropicModel
    from pydantic_ai.providers.anthropic import AnthropicProvider
    
    provider = AnthropicProvider(api_key=settings.ai__anthropic_api_key)
    return AnthropicModel(model_name, provider=provider)


def create_fallback_model(
    primary_model_name: str,
    primary_provider: str
) -> Model:
    """
    Create a FallbackModel instance with primary model and GPT-5 as fallback.

    Args:
        primary_model_name (str): Primary model name
        primary_provider (str): Primary provider name

    Returns:
        Model: FallbackModel instance with GPT-5 as fallback

    Raises:
        InternalServiceException: If model creation fails
    """
    try:
        # Create primary model
        primary_model = create_llm_model(primary_model_name, primary_provider)

        # Create GPT-5 as fallback
        fallback_model = create_llm_model(
            model_name=settings.ai__gpt5__model_name,
            provider=settings.ai__gpt5__provider
        )

        # Create FallbackModel with primary and fallback
        return FallbackModel(primary_model, fallback_model)

    except InternalServiceException:
        raise
    except Exception as e:
        raise InternalServiceException(
            InternalServiceErrorCode.SERVICE_INIT_FAILED,
            detail=f"Failed to create fallback model {primary_model_name} with provider {primary_provider}: {str(e)}"
        ) from e

