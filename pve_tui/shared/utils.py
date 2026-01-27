import os
import sys
from pathlib import Path

from pve_tui.shared.models import ApplicationConfig


def load_config() -> ApplicationConfig:
    config_path = get_config_dir("pve_tui")

    if not (config_file := config_path / "config.toml").exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")

    config = ApplicationConfig.from_toml(config_file)

    return config


def get_config_dir(subdir_name: str) -> Path:
    if sys.platform.startswith("win"):
        folder = os.environ.get("APPDATA", Path.home())
        return Path(folder) / subdir_name

    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / subdir_name

    folder = os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")
    return Path(folder) / subdir_name
