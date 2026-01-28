import asyncio

from .. import models
from .api import ProxmoxClient


class ClusterService:
    """
    Service for interacting with Proxmox VE cluster-related API endpoints.

    Attributes:
        client (ProxmoxClient): The ProxmoxClient instance for making API requests.
    """

    client: ProxmoxClient

    def __init__(self, client: ProxmoxClient):
        self.client = client

    async def get_nodes(self) -> list[str]:
        """Fetches the list of nodes in the Proxmox VE cluster."""
        async with self.client.request('/nodes') as response:
            response.raise_for_status()
            data = await response.json()
            nodes = [node['node'] for node in data.get('data', [])]
            return nodes

    async def get_servers_brief(self) -> list[models.ServerBrief]:
        """Fetches a brief overview of all servers (VMs) in the cluster."""
        nodes = await self.get_nodes()
        servers = []

        async def fetch_node_vms(node_name: str) -> list[dict]:
            async with self.client.request(f'/nodes/{node_name}/qemu') as res:
                res.raise_for_status()
                data = await res.json()
                return data.get('data', [])

        results = await asyncio.gather(
            *(fetch_node_vms(node) for node in nodes),
            return_exceptions=True,
        )

        for result in results:
            if isinstance(result, Exception):
                continue

            for server in result:
                status_value = server.get('status', 'stopped')
                try:
                    status = models.ServerStatus(status_value)
                except ValueError:
                    status = models.ServerStatus.Stopped

                servers.append(
                    models.ServerBrief(
                        server_id=server.get('vmid', 0),
                        name=server.get('name', ''),
                        status=status,
                        cpus=server.get('cpus', 0),
                        cpu_usage=server.get('cpu', 0),
                        memory=server.get('maxmem', 0),
                        memory_used=server.get('mem', 0),
                        uptime=server.get('uptime', 0),
                    ),
                )
        return servers
