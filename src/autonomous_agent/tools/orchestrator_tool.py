from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic_ai import FunctionToolset, RunContext

from src.autonomous_agent.data_model.orchestrator_model import OrchestratorDeps


def delegate_to_coding_agent(
    ctx: RunContext[OrchestratorDeps],
    task: str,
) -> dict:
    """
    Delegate a coding task to the coding agent.

    The coding agent explores, debugs, and modifies code in an isolated Docker workspace.
    Use this for tasks that involve writing, fixing, or running code.

    Parameters
    ----------
    task : str
        A clear description of what the coding agent should do.
    """
    try:
        result = ctx.deps.coding_agent.run_sync(
            user_prompt=task,
            deps=ctx.deps.coding_deps,
        )
        return {"status": "ok", "output": result.output}
    except Exception as e:
        return {"status": "error", "message": f"Coding agent failed: {e}"}


def delegate_to_rag_agent(
    ctx: RunContext[OrchestratorDeps],
    task: str,
) -> dict:
    """
    Delegate a document indexing or retrieval task to the RAG agent.

    The RAG agent ingests files into a vector store and answers questions from
    retrieved context. Use this for tasks involving searching, indexing, or
    querying documents and code for context.

    Parameters
    ----------
    task : str
        A clear description of what the RAG agent should do.
    """
    try:
        result = ctx.deps.rag_agent.run_sync(
            user_prompt=task,
            deps=ctx.deps.rag_deps,
        )
        return {"status": "ok", "output": result.output}
    except Exception as e:
        return {"status": "error", "message": f"RAG agent failed: {e}"}


def remember_fact(
    ctx: RunContext[OrchestratorDeps],
    fact: str,
    tags: list[str] | None = None,
) -> dict:
    """
    Save an important fact or note to persistent memory across sessions.

    Use this to remember user preferences, key decisions, discovered insights,
    project context, or anything worth recalling in future sessions.

    Parameters
    ----------
    fact : str
        The fact or note to remember.
    tags : list[str] | None
        Optional tags for categorization (e.g. ["preference", "architecture"]).
    """
    try:
        collection = ctx.deps.memory_collection
        fact_id = f"fact_{uuid.uuid4().hex[:12]}"
        metadata = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "fact",
        }
        if tags:
            metadata["tags"] = ", ".join(tags)
        collection.add(documents=[fact], ids=[fact_id], metadatas=[metadata])
        return {"status": "ok", "id": fact_id, "message": "Fact saved to memory"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to save fact: {e}"}


def recall_facts(
    ctx: RunContext[OrchestratorDeps],
    query: str,
    n_results: int = 5,
) -> list[dict]:
    """
    Search persistent memory for facts relevant to the given query.

    Use this to recall past conversation context, user preferences, or previously
    discovered insights.

    Parameters
    ----------
    query : str
        The search query.
    n_results : int
        Number of results to return (default 5).
    """
    try:
        collection = ctx.deps.memory_collection
        count = collection.count()
        if count == 0:
            return []
        actual_n = min(n_results, count)
        results = collection.query(query_texts=[query], n_results=actual_n)

        output = []
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        ids = results.get("ids", [[]])[0]

        for i in range(len(documents)):
            entry = {
                "id": ids[i],
                "fact": documents[i],
                "metadata": metadatas[i] if i < len(metadatas) else {},
            }
            output.append(entry)

        return output
    except Exception as e:
        return [{"error": f"Failed to recall facts: {e}"}]


def list_facts(ctx: RunContext[OrchestratorDeps]) -> dict:
    """
    List all facts currently stored in persistent memory.

    Returns the total count and all fact ids with their metadata.
    """
    try:
        collection = ctx.deps.memory_collection
        data = collection.get()
        ids = data.get("ids", [])
        metadatas = data.get("metadatas", [])
        return {
            "count": len(ids),
            "facts": [
                {"id": ids[i], "metadata": metadatas[i]} for i in range(len(ids))
            ],
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to list facts: {e}"}


orchestrator_toolset = FunctionToolset(
    tools=[
        delegate_to_coding_agent,
        delegate_to_rag_agent,
        remember_fact,
        recall_facts,
        list_facts,
    ],
)
