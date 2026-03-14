from typing import TYPE_CHECKING

from .. import models

if TYPE_CHECKING:
    from .api import ProxmoxClient


class ResourceService:
    """Service for fetching and parsing individual Proxmox resources."""

    def __init__(self, client: 'ProxmoxClient'):
        self.client = client

    @staticmethod
    def _parse_server_brief(
        server_data: dict,
        server_type: models.ServerType,
        node: str,
    ) -> models.ServerBrief:
        """Helper method to parse server data into ServerBrief model."""
        vmid = server_data.get('vmid')
        if vmid is None:
            raise ValueError('Server data is missing VMID')

        status_value = server_data.get('status', 'stopped')
        try:
            status = models.ServerStatus(status_value)
        except ValueError:
            status = models.ServerStatus.Stopped

        tags_raw = server_data.get('tags', '')
        if isinstance(tags_raw, str):
            # Proxmox tags can be separated by different characters, usually ;
            tags = [
                t.strip()
                for t in tags_raw.replace(';', ' ').replace(',', ' ').split()
                if t.strip()
            ]
        else:
            tags = []

        return models.ServerBrief(
            server_id=vmid,
            name=server_data.get('name', ''),
            type=server_type,
            status=status,
            cpus=server_data.get('cpus', 0),
            cpu_usage=server_data.get('cpu', 0),
            memory=server_data.get('maxmem', 0),
            memory_used=server_data.get('mem', 0),
            uptime=server_data.get('uptime', 0),
            node=node,
            tags=tags,
        )

    async def fetch_server_brief(
        self,
        node: str,
        vmid: int,
        server_type: models.ServerType,
    ) -> models.ServerBrief | None:
        """Fetches a brief overview of a single server."""
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

    async def fetch_server_details_qemu(
        self,
        node: str,
        vmid: int,
    ) -> models.ServerQEMU:
        """Fetches full details for a QEMU VM."""
        brief = await self.fetch_server_brief(node, vmid, models.ServerType.VM)

        async with self.client.request(f'/nodes/{node}/qemu/{vmid}/config') as res:
            res.raise_for_status()
            data = await res.json()
            config_data = data.get('data', {})
            if config_data:
                arch = config_data.get('arch', 'unknown')
                balloon = config_data.get('balloon', 0)
                cpu_limit = config_data.get('cpulimit', 0)
                cpu_units = config_data.get('cpuunits', 0)
                on_boot = config_data.get('onboot', 0)
                cpu_type = config_data.get('cpu', 'host')

        return models.ServerQEMU(
            brief=brief,
            arch=models.ServerArch(arch),
            balloon=balloon,
            cpu_limit=cpu_limit,
            cpu_units=cpu_units,
            on_boot=bool(on_boot),
            cpu_type=cpu_type,
        )

    async def fetch_server_details_lxc(self, node: str, vmid: int) -> models.ServerLXC:
        """Fetches full details for an LXC container."""
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
