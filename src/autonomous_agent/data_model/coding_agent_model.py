from dataclasses import dataclass

from src.autonomous_agent.services.docker_executer import DockerExecutor


@dataclass
class CodingAgentDeps:
    executor: DockerExecutor
