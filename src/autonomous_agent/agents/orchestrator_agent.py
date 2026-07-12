from pydantic_ai import Agent

from src.config.models import gemma4_ollama_cloud, ai_studio_gemma31b
from src.autonomous_agent.prompts.agent_prompt.orchestrator_prompt import (
    get_orchestrator_system_prompt,
    get_orchestrator_instruction,
)
from src.autonomous_agent.tools.orchestrator_tool import orchestrator_toolset

orchestrator_agent = Agent(
    ai_studio_gemma31b,
    system_prompt=get_orchestrator_system_prompt(),
    instructions=get_orchestrator_instruction(),
    toolsets=[orchestrator_toolset],
    retries=3,
)
