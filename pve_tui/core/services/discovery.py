from typing import TYPE_CHECKING

from .. import models

if TYPE_CHECKING:
    from .api import ProxmoxClient
    from .resource import ResourceService

_RESOURCE_TYPE_MAP: dict[str, models.ServerType] = {
    'qemu': models.ServerType.VM,
    'lxc': models.ServerType.LXC,
}


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
        async with self.client.request(
            '/cluster/resources',
            params={'type': 'vm'},
        ) as res:
            res.raise_for_status()
            data = await res.json()

        servers = []
        for item in data.get('data', []):
            server_type = _RESOURCE_TYPE_MAP.get(item.get('type', ''))
            if server_type is None:
                continue
            try:
                servers.append(
                    self.resource_service._parse_server_brief(
                        item,
                        server_type,
                        item.get('node', ''),
                    ),
                )
            except Exception:
                continue

        return servers
