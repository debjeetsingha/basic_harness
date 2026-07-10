from dataclasses import dataclass

from src.services.docker_executer import DockerExecutor


@dataclass
class CodingAgentDeps:
    executor: DockerExecutor
