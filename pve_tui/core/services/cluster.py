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

    @staticmethod
    def _parse_server_brief(
        server_data: dict,
        server_type: models.ServerType,
        node: str,
    ) -> models.ServerBrief:
        """Helper method to parse server data into ServerBrief model."""
        status_value = server_data.get('status', 'stopped')
        try:
            status = models.ServerStatus(status_value)
        except ValueError:
            status = models.ServerStatus.Stopped

        return models.ServerBrief(
            server_id=server_data.get('vmid', 0),
            name=server_data.get('name', ''),
            type=server_type,
            status=status,
            cpus=server_data.get('cpus', 0),
            cpu_usage=server_data.get('cpu', 0),
            memory=server_data.get('maxmem', 0),
            memory_used=server_data.get('mem', 0),
            uptime=server_data.get('uptime', 0),
            node=node,
        )

    async def fetch_server_brief(
        self,
        node: str,
        vmid: int,
        server_type: models.ServerType,
    ) -> models.ServerBrief | None:
        """
        Fetches a brief overview of a single server by VMID, node name, and server type.

        Args:
            node: The node name where the server is located.
            vmid: The VMID of the server.
            server_type: The type of the server (VM or LXC).

        Returns:
            ServerBrief object if found, None otherwise.
        """
        endpoint_type = 'qemu' if server_type == models.ServerType.VM else 'lxc'

        async with self.client.request(
            f'/nodes/{node}/{endpoint_type}/{vmid}/status/current',
        ) as res:
            res.raise_for_status()
            data = await res.json()
            server_data = data.get('data', {})
            if server_data:
                server_data['vmid'] = vmid  # Ensure vmid is in the data
                return self._parse_server_brief(server_data, server_type, node)

        return None

    async def fetch_servers_brief(self) -> list[models.ServerBrief]:
        """Fetches a brief overview of all servers (VMs and LXCs) in the cluster."""
        nodes = await self.get_nodes()
        servers = []

        async def fetch_node_qemu(
            node_name: str,
        ) -> list[tuple[dict, models.ServerType, str]]:
            async with self.client.request(f'/nodes/{node_name}/qemu') as res:
                res.raise_for_status()
                data = await res.json()
                return [
                    (item, models.ServerType.VM, node_name)
                    for item in data.get('data', [])
                ]

        async def fetch_node_lxc(
            node_name: str,
        ) -> list[tuple[dict, models.ServerType, str]]:
            async with self.client.request(f'/nodes/{node_name}/lxc') as res:
                res.raise_for_status()
                data = await res.json()
                return [
                    (item, models.ServerType.LXC, node_name)
                    for item in data.get('data', [])
                ]

        tasks = []
        for node in nodes:
            tasks.append(fetch_node_qemu(node))
            tasks.append(fetch_node_lxc(node))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                continue

            for server_data, server_type, node in result:
                servers.append(self._parse_server_brief(server_data, server_type, node))

        return servers

    async def fetch_server_details_qemu(
        self,
        node: str,
        vmid: int,
    ) -> models.ServerQEMU:
        brief = await self.fetch_server_brief(node, vmid, models.ServerType.VM)

        async with self.client.request(f'/nodes/{node}/qemu/{vmid}/config') as res:
            res.raise_for_status()
            data = await res.json()
            config_data = data.get('data', {})
            if config_data:
                arch = config_data.get('arch', 'unknown')
                baloon = config_data.get('balloon', 0)
                cpu_limit = config_data.get('cpulimit', 0)
                cpu_units = config_data.get('cpuunits', 0)
                on_boot = config_data.get('onboot', 0)
                cpu_type = config_data.get('cpu', 'host')

        return models.ServerQEMU(
            brief=brief,
            arch=models.ServerArch(arch),
            baloon=baloon,
            cpu_limit=cpu_limit,
            cpu_units=cpu_units,
            on_boot=bool(on_boot),
            cpu_type=cpu_type,
        )

    async def fetch_server_details_lxc(self, node: str, vmid: int) -> models.ServerLXC:
        brief = await self.fetch_server_brief(node, vmid, models.ServerType.LXC)

        async with self.client.request(f'/nodes/{node}/lxc/{vmid}/config') as res:
            res.raise_for_status()
            data = await res.json()
            config_data = data.get('data', {})
            if config_data:
                arch = config_data.get('arch', 'unknown')
                cpu_limit = config_data.get('cpulimit', 0)
                cpu_units = config_data.get('cpuunits', 0)
                on_boot = config_data.get('onboot', 0)
                disk = config_data.get('disk', 0)
                max_disk = config_data.get('maxdisk', 0)

        return models.ServerLXC(
            brief=brief,
            arch=models.ServerArch(arch),
            disk=disk,
            max_disk=max_disk,
            cpu_limit=cpu_limit,
            cpu_units=cpu_units,
            on_boot=bool(on_boot),
        )
