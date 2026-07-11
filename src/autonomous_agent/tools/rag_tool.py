from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic_ai import FunctionToolset, RunContext

from src.autonomous_agent.data_model.rag_agent_model import RagAgentDeps
from src.autonomous_agent.prompts.tool_instruction.rag_toolset import (
    get_rag_toolset_instruction,
    get_memory_toolset_instruction,
)


def ingest_documents(
    ctx: RunContext[RagAgentDeps],
    documents: list[str],
    ids: list[str],
    metadatas: list[dict] | None = None,
) -> dict:
    """
    Ingest documents into the RAG vector store.

    Each document is a text chunk. Each document must have a unique string id.
    Optionally provide metadata (dict of key-value pairs) for each document.

    Parameters
    ----------
    documents : list[str]
        The text chunks to ingest.
    ids : list[str]
        Unique identifier for each document.
    metadatas : list[dict] | None
        Optional metadata for each document.
    """
    try:
        collection = ctx.deps.collection
        collection.add(documents=documents, ids=ids, metadatas=metadatas)
        return {"status": "ok", "ingested": len(documents)}
    except Exception as e:
        return {"status": "error", "message": f"Failed to ingest documents: {e}"}


def ingest_file(
    ctx: RunContext[RagAgentDeps],
    file_path: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> dict:
    """
    Read a file from the workspace, split it into chunks, and ingest into the RAG vector store.

    The file is read from the Docker executor workspace, chunked by character count,
    and each chunk is stored with a unique id derived from the file path and chunk index.

    Parameters
    ----------
    file_path : str
        Path to the file relative to the workspace root.
    chunk_size : int
        Maximum number of characters per chunk.
    chunk_overlap : int
        Number of overlapping characters between consecutive chunks.
    """
    try:
        executor = ctx.deps.executor
        result = executor.execute(f"cat {file_path}")
        if result.get("exit_code", 1) != 0:
            return {"status": "error", "message": result.get("stderr", "Failed to read file")}

        content = result.get("stdout", "")
        if not content.strip():
            return {"status": "error", "message": "File is empty"}

        chunks = []
        start = 0
        while start < len(content):
            end = start + chunk_size
            chunks.append(content[start:end])
            start = end - chunk_overlap
            if start + chunk_overlap >= len(content):
                break

        collection = ctx.deps.collection
        ids = [f"{file_path}::chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"file_path": file_path, "chunk_index": i} for i in range(len(chunks))]
        collection.add(documents=chunks, ids=ids, metadatas=metadatas)
        return {"status": "ok", "ingested": len(chunks), "file": file_path}
    except Exception as e:
        return {"status": "error", "message": f"Failed to ingest file: {e}"}


def query_documents(
    ctx: RunContext[RagAgentDeps],
    query: str,
    n_results: int = 5,
) -> list[dict]:
    """
    Query the RAG vector store for documents relevant to the given query.

    Returns the top matching document chunks with their metadata and similarity scores.

    Parameters
    ----------
    query : str
        The search query.
    n_results : int
        Number of results to return (default 5).
    """
    try:
        collection = ctx.deps.collection
        results = collection.query(query_texts=[query], n_results=n_results)

        output = []
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        ids = results.get("ids", [[]])[0]

        for i in range(len(documents)):
            entry = {
                "id": ids[i],
                "document": documents[i],
                "metadata": metadatas[i] if i < len(metadatas) else {},
                "distance": distances[i] if i < len(distances) else None,
            }
            output.append(entry)

        return output
    except Exception as e:
        return [{"error": f"Failed to query documents: {e}"}]


def list_documents(ctx: RunContext[RagAgentDeps]) -> dict:
    """
    List all documents currently stored in the RAG vector store.

    Returns the total count and all document ids.
    """
    try:
        collection = ctx.deps.collection
        all_ids = collection.get()["ids"]
        return {"count": len(all_ids), "ids": all_ids}
    except Exception as e:
        return {"status": "error", "message": f"Failed to list documents: {e}"}


def remember_fact(
    ctx: RunContext[RagAgentDeps],
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
    ctx: RunContext[RagAgentDeps],
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


def list_facts(ctx: RunContext[RagAgentDeps]) -> dict:
    """
    List all facts currently stored in persistent memory.

    Returns the total count and all fact ids with their metadata.
    """
    try:
        collection = ctx.deps.memory_collection
        data = collection.get()
        ids = data.get("ids", [])
        metadatas = data.get("metadatas", [])
        return {"count": len(ids), "facts": [{"id": ids[i], "metadata": metadatas[i]} for i in range(len(ids))]}
    except Exception as e:
        return {"status": "error", "message": f"Failed to list facts: {e}"}


rag_toolset = FunctionToolset(
    tools=[ingest_documents, ingest_file, query_documents, list_documents],
    instructions=get_rag_toolset_instruction(),
)

memory_toolset = FunctionToolset(
    tools=[remember_fact, recall_facts, list_facts],
    instructions=get_memory_toolset_instruction(),
)
