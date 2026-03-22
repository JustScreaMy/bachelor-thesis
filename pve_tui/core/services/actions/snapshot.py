from typing import TYPE_CHECKING

from .base import ActionManager

if TYPE_CHECKING:
    from ... import models


class SnapshotManager(ActionManager):
    """Handles snapshot operations like creation and rollback."""

    async def list_snapshots(self, server: 'models.ServerBrief') -> list[dict]:
        """Fetches the list of snapshots for a server."""
        path = self.get_path_snapshot(server)
        async with self.client.request(path, method='GET') as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data.get('data', [])

    async def create(
        self,
        server: 'models.ServerBrief',
        name: str,
        description: str = '',
    ) -> str:
        """Creates a snapshot for a single server."""
        path = self.get_path_snapshot(server)
        payload = {
            'snapname': name,
            'description': description,
        }
        # Note: Proxmox VMs support 'vmstate', but containers do not.
        # We keep it simple for now as it defaults to False/0.
        async with self.client.request(path, method='POST', json=payload) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data.get('data')  # Returns UPID

    async def rollback(
        self,
        server: 'models.ServerBrief',
        snapshot_name: str,
    ) -> str:
        """Rolls back the server to a specific snapshot."""
        path = f'{self.get_path_snapshot(server)}/{snapshot_name}/rollback'
        async with self.client.request(path, method='POST') as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data.get('data')  # Returns UPID

    async def rollback_to_latest(self, server: 'models.ServerBrief') -> str:
        """Finds the latest snapshot and rolls back to it."""
        snapshots = await self.list_snapshots(server)
        # Filter out 'current' and sort by time (descending)
        valid_snapshots = [s for s in snapshots if s.get('name') != 'current']
        if not valid_snapshots:
            raise ValueError(f'No snapshots found for server {server.server_id}')

        # snaptime is a Unix timestamp
        latest = max(valid_snapshots, key=lambda x: x.get('snaptime', 0))
        return await self.rollback(server, latest['name'])

    # Bulk Actions
    async def create_many(
        self,
        servers: list['models.ServerBrief'],
        name: str,
        description: str = '',
    ) -> tuple[dict[int, str], dict[int, Exception]]:
        """Creates a snapshot for multiple servers in parallel."""

        async def _create(s: 'models.ServerBrief'):
            return await self.create(s, name, description)

        return await self.run_bulk(servers, _create)

    async def rollback_to_latest_many(
        self,
        servers: list['models.ServerBrief'],
    ) -> tuple[dict[int, str], dict[int, Exception]]:
        """Rolls back multiple servers to their respective latest snapshots."""
        return await self.run_bulk(servers, self.rollback_to_latest)
