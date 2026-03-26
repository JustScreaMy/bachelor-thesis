import os
import sys
from pathlib import Path

from pve_tui.core.models import ApplicationConfig


def load_config() -> ApplicationConfig:
    # Check current directory first (Development convenience)
    if (local_config := Path.cwd() / 'config.toml').exists():
        config_file = local_config
    else:
        config_path = get_config_dir('pve_tui')

        if not (config_file := config_path / 'config.toml').exists():
            raise FileNotFoundError(f'Configuration file not found: {config_file}')

    config = ApplicationConfig.from_toml(config_file)

    # Environment variable overrides for token_id and token
    # This applies to all contexts if set
    env_token_id = os.environ.get('PVE_TOKEN_ID')
    env_token = os.environ.get('PVE_TOKEN')

    if env_token_id or env_token:
        from pve_tui.core.models.client_config import ContextConfig

        new_contexts = {}
        for name, ctx in config.contexts.items():
            new_contexts[name] = ContextConfig(
                base_url=ctx.base_url,
                token_id=env_token_id if env_token_id else ctx.token_id,
                token=env_token if env_token else ctx.token,
                verify_ssl=ctx.verify_ssl,
            )
        config.contexts = new_contexts

    return config


def get_config_dir(subdir_name: str) -> Path:
    if sys.platform.startswith('win'):
        folder = os.environ.get('APPDATA', Path.home())
        return Path(folder) / subdir_name

    if sys.platform == 'darwin':
        return Path.home() / 'Library' / 'Application Support' / subdir_name

    folder = os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')
    return Path(folder) / subdir_name
