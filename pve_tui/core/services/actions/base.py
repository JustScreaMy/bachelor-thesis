import asyncio
from typing import Any
from typing import Awaitable
from typing import Callable
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

    @staticmethod
    async def run_bulk(
        servers: list['models.ServerBrief'],
        action_func: Callable[['models.ServerBrief'], Awaitable[Any]],
    ) -> tuple[dict[int, Any], dict[int, Exception]]:
        """
        Executes an action function in parallel across multiple servers.

        Returns:
            A tuple of (results, errors) where both are dicts keyed by VMID.
        """
        tasks = [action_func(server) for server in servers]
        results_list = await asyncio.gather(*tasks, return_exceptions=True)

        successes = {}
        failures = {}

        for server, result in zip(servers, results_list):
            if isinstance(result, Exception):
                failures[server.server_id] = result
            else:
                successes[server.server_id] = result

        return successes, failures
