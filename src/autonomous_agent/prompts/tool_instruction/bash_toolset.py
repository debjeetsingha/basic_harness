def get_bash_toolset_instruction():
    prompt = """
Execute shell commands inside the project workspace.

The current working directory persists between calls.

Use this tool to:
- inspect files
- navigate directories
- run Python
- run git
- execute tests
- run build tools

Do not attempt to leave the workspace.

Do not use destructive commands.

Prefer reading project files before modifying them.

Run one logical command per invocation.
"""
    return prompt
 