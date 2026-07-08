from pydantic_ai import FunctionToolset, RunContext
from src.autonomous_agent.services.docker_executer import DockerExecutor
from src.autonomous_agent.prompts.tool_instruction.bash_toolset import (
    get_bash_toolset_instruction,
)
from src.autonomous_agent.data_model.coding_agent_model import CodingAgentDeps


def bash(ctx: RunContext[CodingAgentDeps], command: str) -> dict:
    """
    Execute a bash command inside the isolated project workspace.

    The current working directory is preserved across calls.

    Examples
    --------
    bash("pwd")
    bash("ls")
    bash("git status")
    bash("python main.py")

    To change directories, execute `cd` as its own command.

    Correct:
        bash("cd src")
        bash("pytest")

    Incorrect:
        bash("cd src && pytest")

    The workspace is disposable, so commands may freely modify files,
    install packages, create directories, or delete files.
    Changes affect only the temporary Docker workspace until they are
    explicitly accepted and applied to the user's project.
    """
    return ctx.deps.executor.execute(command)


bash_toolset = FunctionToolset(
    tools=[bash],
    instructions=get_bash_toolset_instruction(),
)
