"""Git operations helper."""

import subprocess
import os


def get_git_branch(cwd: str) -> str:
    """Get current git branch name."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return ""


def is_git_repo(cwd: str) -> bool:
    """Check if directory is a git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=cwd,
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        return result.returncode == 0
    except Exception:
        return False


def get_commit_command(message: str) -> str:
    """Generate git commit command with message."""
    # Escape quotes in message
    escaped_message = message.replace('"', '\\"')
    return f'git add . && git commit -m "{escaped_message}"'
