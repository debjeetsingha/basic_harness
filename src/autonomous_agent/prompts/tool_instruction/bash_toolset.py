def get_bash_toolset_instruction():
    prompt = """
Use this tool whenever you need to execute shell commands.

The working directory persists across invocations.

When changing directories:

- Execute `cd` by itself.
- Wait for it to succeed.
- Execute the next command afterward.

Good:

bash("cd src")
bash("pytest")

Good:

bash("cd tests")
bash("python test_api.py")

Avoid:

bash("cd src && pytest")

Avoid:

bash("cd src; python main.py")

The workspace is isolated inside a disposable Docker container. You may freely create, modify, or delete files within the workspace. None of these changes affect the user's original project until they are explicitly reviewed and applied.
"""
    return prompt
