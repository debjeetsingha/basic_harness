def get_rag_toolset_instruction():
    prompt = """
Use these tools to manage and query the RAG vector store.

ingest_file:
  Read a file from the workspace and ingest it as chunks.
  Use this for source code, documentation, text files, etc.

ingest_documents:
  Add raw text chunks directly to the vector store.
  Use this when you have pre-processed text or want to add content not from a file.

query_documents:
  Search the vector store for documents relevant to a query.
  Use this to find context before answering questions.
  Returns the top matching chunks with metadata and similarity scores.

list_documents:
  Show all document ids currently in the vector store.
  Use this to understand what has been ingested.

When building a knowledge base:
1. Identify relevant files in the workspace using bash commands (ls, find, etc.).
2. Ingest them using ingest_file.
3. Verify ingestion with list_documents.
4. Answer the user's questions using query_documents.
"""
    return prompt


def get_memory_toolset_instruction():
    prompt = """
Use these tools to manage persistent memory across sessions.

remember_fact:
  Save an important fact, preference, decision, or insight to long-term memory.
  Use tags to categorize the fact for easier recall later.
  Examples: user preferences, project architecture decisions, debugging insights.

recall_facts:
  Search persistent memory for facts relevant to a query.
  Use this at the start of a session to load relevant past context.
  Returns matching facts with their metadata and timestamps.

list_facts:
  List all facts currently stored in persistent memory.
  Use this to see what has been remembered.

When managing memory:
- Save facts proactively when the user shares important information.
- Recall facts at the start of a session to provide contextual responses.
- Use descriptive tags to make facts easy to find later.
- Avoid saving trivial or temporary information.
"""
    return prompt
