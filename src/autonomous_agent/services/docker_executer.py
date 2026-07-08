from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import docker


class DockerExecutor:
    """
    Disposable Docker workspace for autonomous coding agents.

    Workflow
    --------
    1. Creates a temporary copy of the project.
    2. Starts an isolated Docker container.
    3. Copies the project into the container.
    4. Initializes a Git repository.
    5. Executes arbitrary shell commands.
    6. Generates a Git diff.
    7. Cleans everything up.

    Example
    -------
    with DockerExecutor("/home/user/project") as executor:

        executor.execute("ls")

        executor.execute("pytest")

        print(executor.diff())
    """

    def __init__(
        self,
        project: str | Path,
        image: str = "ai-agent",
    ):
        self.project = Path(project).resolve()

        if not self.project.exists():
            raise FileNotFoundError(self.project)

        self.image = image

        self.client = docker.from_env()

        self.container = None

        self.temp_dir: Path | None = None

        self.cwd = "/workspace/project"

    def start(self):

        self.temp_dir = Path(tempfile.mkdtemp(prefix="coding-agent-"))

        shutil.copytree(
            self.project,
            self.temp_dir / "project",
            dirs_exist_ok=True,
        )

        self.container = self.client.containers.run(
            image=self.image,
            command="sleep infinity",
            detach=True,
            working_dir="/workspace",
            network_disabled=True,
            mem_limit="4g",
            nano_cpus=2_000_000_000,
            auto_remove=True,
        )

        subprocess.run(
            [
                "docker",
                "cp",
                str(self.temp_dir / "project"),
                f"{self.container.id}:/workspace",
            ],
            check=True,
        )

        self._initialize_git()

    def _initialize_git(self):

        commands = [
            "git init -q",
            'git config user.name "AI Agent"',
            'git config user.email "agent@example.com"',
            "git add .",
            'git commit -qm "Initial snapshot"',
        ]

        for command in commands:
            result = self.execute(command)

            if not result["success"]:
                raise RuntimeError(
                    f"Failed to initialize git.\nCommand: {command}\n{result['stderr']}"
                )

    def execute(self, command: str) -> dict:
        """
        Execute a shell command inside the container.

        The current working directory is preserved between calls.
        If the command is a standalone `cd`, the working directory
        is updated without spawning a persistent shell.

        Returns
        -------
        dict
            {
                "success": bool,
                "stdout": str,
                "stderr": str,
                "exit_code": int,
            }
        """

        command = command.strip()

        #
        # Handle `cd` ourselves.
        #
        if command == "cd":
            command = "cd ~"

        if command.startswith("cd "):
            target = command[3:].strip()

            result = self.container.exec_run(
                f"cd {target} && pwd",
                workdir=self.cwd,
                demux=True,
            )

            stdout, stderr = result.output

            stdout = (stdout or b"").decode().strip()
            stderr = (stderr or b"").decode().strip()

            if result.exit_code == 0:
                self.cwd = stdout

            return {
                "success": result.exit_code == 0,
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": result.exit_code,
            }

        #
        # Everything else.
        #
        result = self.container.exec_run(
            command,
            workdir=self.cwd,
            demux=True,
        )

        stdout, stderr = result.output

        return {
            "success": result.exit_code == 0,
            "stdout": (stdout or b"").decode(),
            "stderr": (stderr or b"").decode(),
            "exit_code": result.exit_code,
        }

    def diff(self) -> str:

        result = self.container.exec_run(
            "git diff --binary HEAD",
            workdir="/workspace/project",
        )

        return result.output.decode()

    def cleanup(self):

        if self.container is not None:
            try:
                self.container.stop()

            except docker.errors.NotFound:
                pass

        if self.temp_dir is not None:
            shutil.rmtree(
                self.temp_dir,
                ignore_errors=True,
            )

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
