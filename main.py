import os

import chromadb

from src.config.settings import load_dotenv
from src.config.telemetry import start_tracing
from src.autonomous_agent.agents.coding_agent import coding_agent
from src.autonomous_agent.agents.rag_agent import rag_agent
from src.autonomous_agent.agents.orchestrator_agent import orchestrator_agent

from src.services.docker_executer import DockerExecutor
from src.autonomous_agent.data_model.coding_agent_model import CodingAgentDeps
from src.autonomous_agent.data_model.rag_agent_model import RagAgentDeps
from src.autonomous_agent.data_model.orchestrator_model import OrchestratorDeps

load_dotenv()
# start_tracing()

SUMMARIZE_PROMPT = (
    "Summarize the key points of our conversation in a concise paragraph. "
    "Focus on: what the user wanted, what was accomplished, important decisions made, "
    "and any open items. Save this summary to memory using remember_fact with the tag 'session_summary'."
)


def run_coding_agent():
    output_dir = os.getenv("OUTPUT_DIR_FOR_AGENT")

    with DockerExecutor(
        os.getenv("WORKING_DIR_FOR_AGENT"), output_dir=output_dir
    ) as executor:
        deps = CodingAgentDeps(executor=executor)
        message_history = None

        while True:
            input_prompt = input("Type exit to exit\n Input:  ")
            if input_prompt == "exit":
                break

            result = coding_agent.run_sync(
                user_prompt=input_prompt,
                deps=deps,
                message_history=message_history,
            )
            message_history = result.all_messages()
            print(result.output)

        print("---git diff---")
        print(executor.diff())

        apply = input("Apply changes to original project? (y/n) ").strip().lower()
        if apply == "y":
            path = executor.apply_changes()
            print(f"---changes applied to {path}---")

        if output_dir:
            path = executor.export_output()
            print(f"---output exported to {path}---")


def run_rag_agent():
    chroma_client = chromadb.PersistentClient()
    collection = chroma_client.get_or_create_collection("workspace_docs")
    memory_collection = chroma_client.get_or_create_collection("conversation_memory")
    output_dir = os.getenv("OUTPUT_DIR_FOR_AGENT")

    with DockerExecutor(
        os.getenv("WORKING_DIR_FOR_AGENT"), output_dir=output_dir
    ) as executor:
        deps = RagAgentDeps(
            executor=executor,
            collection=collection,
            memory_collection=memory_collection,
        )
        message_history = None

        while True:
            input_prompt = input("Type exit to exit\n Input:  ")
            if input_prompt == "exit":
                break

            result = rag_agent.run_sync(
                user_prompt=input_prompt,
                deps=deps,
                message_history=message_history,
            )
            message_history = result.all_messages()
            print(result.output)

        print("---auto-summarizing session---")
        try:
            summary_result = rag_agent.run_sync(
                user_prompt=SUMMARIZE_PROMPT,
                deps=deps,
                message_history=message_history,
            )
            print(summary_result.output)
        except Exception as e:
            print(f"Auto-summarization failed: {e}")

        print("---git diff---")
        print(executor.diff())

        apply = input("Apply changes to original project? (y/n) ").strip().lower()
        if apply == "y":
            path = executor.apply_changes()
            print(f"---changes applied to {path}---")

        if output_dir:
            path = executor.export_output()
            print(f"---output exported to {path}---")


def run_orchestrator():
    chroma_client = chromadb.PersistentClient()
    collection = chroma_client.get_or_create_collection("workspace_docs")
    memory_collection = chroma_client.get_or_create_collection("conversation_memory")
    output_dir = os.getenv("OUTPUT_DIR_FOR_AGENT")

    with DockerExecutor(
        os.getenv("WORKING_DIR_FOR_AGENT"), output_dir=output_dir
    ) as executor:
        coding_deps = CodingAgentDeps(executor=executor)
        rag_deps = RagAgentDeps(
            executor=executor,
            collection=collection,
            memory_collection=memory_collection,
        )
        orchestrator_deps = OrchestratorDeps(
            executor=executor,
            memory_collection=memory_collection,
            coding_agent=coding_agent,
            coding_deps=coding_deps,
            rag_agent=rag_agent,
            rag_deps=rag_deps,
        )

        message_history = None

        while True:
            input_prompt = input("Type exit to exit\n Input:  ")
            if input_prompt == "exit":
                break

            result = orchestrator_agent.run_sync(
                user_prompt=input_prompt,
                deps=orchestrator_deps,
                message_history=message_history,
            )
            message_history = result.all_messages()
            print(result.output)

        print("---auto-summarizing session---")
        try:
            summary_result = orchestrator_agent.run_sync(
                user_prompt=SUMMARIZE_PROMPT,
                deps=orchestrator_deps,
                message_history=message_history,
            )
            print(summary_result.output)
        except Exception as e:
            print(f"Auto-summarization failed: {e}")

        print("---git diff---")
        print(executor.diff())

        apply = input("Apply changes to original project? (y/n) ").strip().lower()
        if apply == "y":
            path = executor.apply_changes()
            print(f"---changes applied to {path}---")

        if output_dir:
            path = executor.export_output()
            print(f"---output exported to {path}---")


if __name__ == "__main__":
    mode = input(
        "Select agent mode:\n  1. coding\n  2. rag\n  3. orchestrator\n> "
    ).strip()

    if mode == "2":
        run_rag_agent()
    elif mode == "3":
        run_orchestrator()
    else:
        run_coding_agent()
