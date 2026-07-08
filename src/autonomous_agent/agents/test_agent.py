from pydantic_ai import Agent

from src.autonomous_agent.config.models import gemma4_e2b_local
from autonomous_agent.prompts.agent_prompt.test_prompt import get_test_instruction_prompt, get_test_system_prompt
from src.autonomous_agent.tools.test_tool import get_current_directory, get_user_name
from src.autonomous_agent.config.model_settings import openai_chat_high_settings

test_agent = Agent(
    gemma4_e2b_local,
    system_prompt=(get_test_system_prompt()),
    instructions=get_test_instruction_prompt(),
    tools=[get_current_directory, get_user_name],
    model_settings=openai_chat_high_settings,
    retries=2,
)
