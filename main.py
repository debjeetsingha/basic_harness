import uvicorn
import os

from src.autonomous_agent.config.settings import load_dotenv
from src.autonomous_agent.config.telemetry import start_tracing
from src.autonomous_agent.agents.coding_agent import coding_agent
from src.autonomous_agent.config.models import gemma4_ollama_cloud, gptoss_ollama_cloud
from src.autonomous_agent.services.docker_executer import DockerExecutor
from src.autonomous_agent.data_model.coding_agent_model import CodingAgentDeps

load_dotenv()
start_tracing()

app = coding_agent.to_web(models=[gemma4_ollama_cloud, gptoss_ollama_cloud])

with DockerExecutor(os.getenv("WORKING_DIR_FOR_AGENT")) as executor:
    deps = CodingAgentDeps(
        executor=executor,
    )
    result = coding_agent.run_sync(
        user_prompt="list all the files in the project and delete them except .git",
        deps=deps,
    )

    print(result.output)

    # print("----steps----")

    # print(result.all_messages())

    print("---git diff---")

    print(executor.diff())


# if __name__ == "__main__":
#     uvicorn.run(
#         "main:app",
#         host="127.0.0.1",
#         port=7932,
#         reload=True,
#     )
