import asyncio
from typing import TYPE_CHECKING

from .. import models

if TYPE_CHECKING:
    from .api import ProxmoxClient
    from .resource import ResourceService


class DiscoveryService:
    """Service for discovering nodes and listing all resources in the cluster."""

    def __init__(self, client: 'ProxmoxClient', resource_service: 'ResourceService'):
        self.client = client
        self.resource_service = resource_service

    async def get_nodes(self) -> list[str]:
        """Fetches the list of nodes in the Proxmox VE cluster."""
        async with self.client.request('/nodes') as response:
            response.raise_for_status()
            data = await response.json()
            nodes = [node['node'] for node in data.get('data', [])]
            return nodes

    async def fetch_all_servers(self) -> list[models.ServerBrief]:
        """Fetches a brief overview of all servers (VMs and LXCs) in the cluster."""
        nodes = await self.get_nodes()
        servers = []

        async def fetch_node_resources(
            node_name: str,
            endpoint: str,
            server_type: models.ServerType,
        ) -> list[tuple[dict, models.ServerType, str]]:
            async with self.client.request(f'/nodes/{node_name}/{endpoint}') as res:
                res.raise_for_status()
                data = await res.json()
                return [(item, server_type, node_name) for item in data.get('data', [])]

        tasks = []
        for node in nodes:
            tasks.append(
                fetch_node_resources(node, 'qemu', models.ServerType.VM),
            )
            tasks.append(
                fetch_node_resources(node, 'lxc', models.ServerType.LXC),
            )

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                # We skip node-level failures to show partial data if some nodes are down
                continue

            for server_data, server_type, node in result:
                try:
                    servers.append(
                        self.resource_service._parse_server_brief(
                            server_data,
                            server_type,
                            node,
                        ),
                    )
                except Exception:
                    continue

        return servers
