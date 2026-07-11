from dataclasses import dataclass

from chromadb import Collection

from src.services.docker_executer import DockerExecutor


@dataclass
class RagAgentDeps:
    executor: DockerExecutor
    collection: Collection
    memory_collection: Collection
