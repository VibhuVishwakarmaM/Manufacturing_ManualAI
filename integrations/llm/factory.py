from django.conf import settings
from .base import BaseLLMProvider
from .mock_provider import MockLLMProvider
from .openai_provider import OpenAILLMProvider
from .anthropic_provider import AnthropicLLMProvider, OllamaLLMProvider

def get_llm_provider(name: str = None) -> BaseLLMProvider:
    """Factory to retrieve configured LLM provider."""
    ai_cfg = getattr(settings, 'AI_SETTINGS', {})
    provider_name = (name or ai_cfg.get('LLM_PROVIDER', 'mock')).lower()

    if provider_name == 'openai':
        return OpenAILLMProvider()
    elif provider_name == 'anthropic':
        return AnthropicLLMProvider()
    elif provider_name == 'ollama':
        return OllamaLLMProvider()
    elif provider_name == 'mock':
        return MockLLMProvider()
    else:
        return MockLLMProvider()
