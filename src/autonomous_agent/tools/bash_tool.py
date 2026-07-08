"""
Safe Bash Tool
==============

A secure bash execution tool intended for autonomous AI coding agents.

Features
--------
- Executes commands inside a fixed workspace.
- Never allows escaping the workspace.
- Maintains the current working directory across calls.
- Supports normal shell commands.
- Supports `cd`.
- Blocks destructive commands.
- Blocks shell redirection and command chaining.
- Returns structured output.

Example
-------
tool = BashTool("/home/user/project")

tool.run("pwd")

tool.run("ls")

tool.run("cd src")

tool.run("python main.py")

tool.run("git status")
"""

from __future__ import annotations

import os
import shlex
import subprocess
import time
from pathlib import Path
from typing import Any

from pydantic_ai import FunctionToolset

from src.autonomous_agent.prompts.tool_instruction.bash_toolset import get_bash_toolset_instruction

BLOCKED_COMMANDS = {
    "rm",
    "rmdir",
    "mv",
    "dd",
    "mkfs",
    "shutdown",
    "reboot",
    "halt",
    "poweroff",
    "sudo",
    "su",
    "chmod",
    "chown",
}

BLOCKED_TOKENS = {
    "&&",
    "||",
    ";",
    "|",
    ">",
    ">>",
    "<",
    "<<",
    "$(",
    "`",
}


class BashTool:
    """
    Secure bash tool.

    The current working directory is preserved between calls.

    Parameters
    ----------
    workspace:
        Root directory the agent is allowed to access.

    Example
    -------
    bash = BashTool("/home/user/project")

    bash.run("ls")

    bash.run("cd src")

    bash.run("pytest")
    """

    def __init__(self, workspace: str | Path):
        self.workspace = Path(workspace).resolve()

        if not self.workspace.exists():
            raise ValueError("Workspace does not exist.")

        self.cwd = self.workspace

    def _inside_workspace(self, path: Path) -> bool:
        try:
            path.resolve().relative_to(self.workspace)
            return True
        except ValueError:
            return False

    def _error(self, message: str) -> dict[str, Any]:
        return {
            "success": False,
            "cwd": str(self.cwd),
            "stdout": "",
            "stderr": message,
            "exit_code": -1,
            "execution_time": 0,
        }

    def run(self, command: str, timeout: int = 60) -> dict[str, Any]:
        """
        Execute a shell command.

        Parameters
        ----------
        command:
            Command to execute.

        timeout:
            Maximum runtime.

        Returns
        -------
        dict
        """

        command = command.strip()

        if not command:
            return self._error("Empty command.")

        for token in BLOCKED_TOKENS:
            if token in command:
                return self._error(f"Shell operator '{token}' is not allowed.")

        try:
            parts = shlex.split(command)
        except ValueError as e:
            return self._error(str(e))

        executable = parts[0]

        if executable in BLOCKED_COMMANDS:
            return self._error(f"'{executable}' is blocked.")

        #
        # cd
        #
        if executable == "cd":

            if len(parts) == 1:
                target = self.workspace
            else:
                target = (self.cwd / parts[1]).resolve()

            if not target.exists():
                return self._error("Directory does not exist.")

            if not target.is_dir():
                return self._error("Not a directory.")

            if not self._inside_workspace(target):
                return self._error(
                    "Access denied. Cannot leave workspace."
                )

            self.cwd = target

            return {
                "success": True,
                "cwd": str(self.cwd),
                "stdout": str(self.cwd),
                "stderr": "",
                "exit_code": 0,
                "execution_time": 0,
            }

        start = time.perf_counter()

        try:

            result = subprocess.run(
                command,
                shell=True,
                cwd=self.cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

        except subprocess.TimeoutExpired:

            return self._error("Command timed out.")

        elapsed = time.perf_counter() - start

        return {
            "success": result.returncode == 0,
            "cwd": str(self.cwd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
            "execution_time": round(elapsed, 3),
        }
    

bash = BashTool(os.getenv("WORKING_DIR_FOR_AGENT"))

bash_toolset = FunctionToolset(
    tools=[bash.run],
    instructions=get_bash_toolset_instruction(),
)

