from pydantic_ai import Agent

from src.autonomous_agent.config.models import gemma4_ollama_cloud
from src.autonomous_agent.prompts.agent_prompt.coding_agent_prompt import get_coding_agent_system_prompt, get_coding_agent_instruction
from src.autonomous_agent.tools.bash_tool import bash_toolset
from src.autonomous_agent.config.model_settings import openai_chat_high_settings

coding_agent = Agent(
    gemma4_ollama_cloud,
    system_prompt=(get_coding_agent_system_prompt()),
    instructions=get_coding_agent_instruction(),
    toolsets=[bash_toolset],
    model_settings=openai_chat_high_settings,
    retries=2,
)