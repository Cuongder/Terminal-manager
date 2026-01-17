"""Configuration management for Terminal Manager."""

import json
import os
from pathlib import Path

import sys

# Determine path to config.json
if getattr(sys, 'frozen', False):
    # If run as exe, config is next to the executable
    ROOT_DIR = Path(sys.executable).parent
else:
    # If run as script, config is in project root (src/../)
    ROOT_DIR = Path(__file__).parent.parent

CONFIG_FILE = ROOT_DIR / "config.json"

DEFAULT_CONFIG = {
    "recent_projects": [],
    "custom_commands": [],
    "max_recent": 10,
    "theme": "dark"
}


def load_config() -> dict:
    """Load configuration from file."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                # Merge with defaults for any missing keys
                return {**DEFAULT_CONFIG, **config}
        except (json.JSONDecodeError, IOError):
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def save_config(config: dict) -> None:
    """Save configuration to file."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Error saving config: {e}")


def add_recent_project(path: str) -> None:
    """Add a project to recent projects list."""
    config = load_config()
    recent = config["recent_projects"]
    
    # Remove if already exists
    if path in recent:
        recent.remove(path)
    
    # Add to front
    recent.insert(0, path)
    
    # Keep only max_recent items
    config["recent_projects"] = recent[:config["max_recent"]]
    save_config(config)


def get_recent_projects() -> list:
    """Get list of recent projects."""
    config = load_config()
    # Filter out non-existent paths
    return [p for p in config["recent_projects"] if os.path.isdir(p)]


def add_custom_command(label: str, command: str) -> None:
    """Add a custom command."""
    config = load_config()
    config["custom_commands"].append({"label": label, "command": command})
    save_config(config)


def remove_custom_command(index: int) -> None:
    """Remove a custom command by index."""
    config = load_config()
    if 0 <= index < len(config["custom_commands"]):
        config["custom_commands"].pop(index)
        save_config(config)


def get_custom_commands() -> list:
    """Get list of custom commands."""
    config = load_config()
    return config["custom_commands"]
