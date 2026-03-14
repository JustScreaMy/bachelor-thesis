from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ... import models
    from ..api import ProxmoxClient


class ActionManager:
    """Base class for specialized server action logic."""

    def __init__(self, client: 'ProxmoxClient'):
        self.client = client

    @staticmethod
    def get_path_status(server: 'models.ServerBrief', action: str) -> str:
        """Constructs the API path for status actions."""
        etype = 'qemu' if server.type == 'vm' else 'lxc'
        return f'/nodes/{server.node}/{etype}/{server.server_id}/status/{action}'

    @staticmethod
    def get_path_config(server: 'models.ServerBrief') -> str:
        """Constructs the API path for configuration actions."""
        etype = 'qemu' if server.type == 'vm' else 'lxc'
        return f'/nodes/{server.node}/{etype}/{server.server_id}/config'

    @staticmethod
    def get_path_snapshot(server: 'models.ServerBrief') -> str:
        """Constructs the API path for snapshot actions."""
        etype = 'qemu' if server.type == 'vm' else 'lxc'
        return f'/nodes/{server.node}/{etype}/{server.server_id}/snapshot'
