import uvicorn

from src.autonomous_agent.config.settings import load_dotenv
from src.autonomous_agent.config.telemetry import start_tracing
from src.autonomous_agent.agents.coding_agent import coding_agent
from src.autonomous_agent.config.models import gemma4_ollama_cloud, gptoss_ollama_cloud

load_dotenv()
start_tracing()

app = coding_agent.to_web(models=[gemma4_ollama_cloud, gptoss_ollama_cloud])
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=7932,
        reload=True,
    )