import os

from pydantic_ai.providers.openai import OpenAIProvider

litellm_provider = OpenAIProvider(
    base_url=os.getenv("LITELLM_PROXY_URL"),
    api_key=os.getenv("LITELLM_PROXY_API_KEY"),
)
