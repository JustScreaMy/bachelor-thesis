from contextlib import asynccontextmanager
from typing import AsyncIterator

from .action import ActionService
from .api import ProxmoxClient
from .discovery import DiscoveryService
from .resource import ResourceService


class ServiceContext:
    """Holds all wired-up services for a single Proxmox connection."""

    def __init__(self, client: ProxmoxClient):
        self.client = client
        self.resource = ResourceService(client)
        self.discovery = DiscoveryService(client, self.resource)
        self.actions = ActionService(client)

    async def close(self) -> None:
        await self.client.close()


@asynccontextmanager
async def create_service_context(context: str = '') -> AsyncIterator[ServiceContext]:
    """Creates a ServiceContext from config and ensures cleanup."""
    from ..utils import load_config

    config = load_config()
    client = ProxmoxClient.from_config(config, context=context)
    ctx = ServiceContext(client)
    try:
        yield ctx
    finally:
        await ctx.close()
