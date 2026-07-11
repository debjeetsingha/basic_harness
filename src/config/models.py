from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.embeddings.openai import OpenAIEmbeddingModel
from .providers import litellm_provider


gemma4_e2b_local = OpenAIChatModel("ollama_local/gemma4:e2b-it-qat", provider=litellm_provider)
gemma4_e4b_local = OpenAIChatModel("ollama_local/gemma4:e4b-it-qat", provider=litellm_provider)

# qwen_4b_local = OpenAIChatModel("ollama_chat/qwen3.5:4b", provider=litellm_provider)
# qwen_0_8b_local = OpenAIChatModel("ollama_chat/qwen3.5:0.8b", provider=litellm_provider)

gemma4_ollama_cloud = OpenAIChatModel("ollama_cloud/gemma4:31b-cloud", provider=litellm_provider)
gptoss_ollama_cloud = OpenAIChatModel("ollama_cloud/gpt-oss:20b-cloud", provider=litellm_provider)

gemini_lite = OpenAIChatModel("gemini/gemini-3.1-flash-lite", provider=litellm_provider)
gemini_flash = OpenAIChatModel("gemini/gemini-3.5-flash", provider=litellm_provider)

ai_studio_gemma26b = OpenAIChatModel(
    "gemini/gemma-4-26b-a4b-it", provider=litellm_provider
)
ai_studio_gemma31b = OpenAIChatModel("gemma-4-31b-it", provider=litellm_provider)


embeddinggemma_local = OpenAIEmbeddingModel("embeddinggemma:latest", 
                                          provider=litellm_provider, 
                                          )