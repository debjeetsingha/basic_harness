from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from chromadb import Collection

from src.autonomous_agent.data_model.coding_agent_model import CodingAgentDeps
from src.autonomous_agent.data_model.rag_agent_model import RagAgentDeps
from src.services.docker_executer import DockerExecutor

if TYPE_CHECKING:
    from pydantic_ai import Agent


@dataclass
class OrchestratorDeps:
    executor: DockerExecutor
    memory_collection: Collection
    coding_agent: Agent
    coding_deps: CodingAgentDeps
    rag_agent: Agent
    rag_deps: RagAgentDeps
