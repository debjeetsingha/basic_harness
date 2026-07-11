from pydantic_ai import Agent

from src.config.models import gemma4_e4b_local
from src.autonomous_agent.prompts.agent_prompt.rag_agent_prompt import (
    get_rag_agent_system_prompt,
    get_rag_agent_instruction,
)
from src.autonomous_agent.tools.rag_tool import rag_toolset, memory_toolset

rag_agent = Agent(
    gemma4_e4b_local,
    system_prompt=get_rag_agent_system_prompt(),
    instructions=get_rag_agent_instruction(),
    toolsets=[rag_toolset, memory_toolset],
    retries=3,
)
