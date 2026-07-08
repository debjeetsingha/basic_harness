from pydantic_ai.models.openai import OpenAIChatModelSettings

openai_chat_high_settings = OpenAIChatModelSettings(
    openai_reasoning_effort="high"
)
openai_chat_medium_settings = OpenAIChatModelSettings(
    openai_reasoning_effort="medium"
)
openai_chat_low_settings = OpenAIChatModelSettings(
    openai_reasoning_effort="low"
)
gemini_studio_settings = OpenAIChatModelSettings(
    openai_reasoning_effort="medium",
)
