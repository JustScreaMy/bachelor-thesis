from typing import TYPE_CHECKING

from .base import ActionManager

if TYPE_CHECKING:
    from ... import models


class StatusManager(ActionManager):
    """Handles status-related actions like start, stop, shutdown, and reboot."""

    async def _post(self, server: 'models.ServerBrief', action: str) -> str:
        """Helper to send POST request to the status endpoint."""
        path = self.get_path_status(server, action)
        async with self.client.request(path, method='POST') as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data.get('data')  # Returns the Proxmox UPID

    async def start(self, server: 'models.ServerBrief') -> str:
        """Starts the server."""
        return await self._post(server, 'start')

    async def stop(self, server: 'models.ServerBrief') -> str:
        """Stops the server immediately (hard power off)."""
        return await self._post(server, 'stop')

    async def shutdown(self, server: 'models.ServerBrief') -> str:
        """Shuts down the server gracefully."""
        return await self._post(server, 'shutdown')

    async def reboot(self, server: 'models.ServerBrief') -> str:
        """Reboots the server."""
        return await self._post(server, 'reboot')

    # Bulk Actions
    async def start_many(
        self,
        servers: list['models.ServerBrief'],
    ) -> tuple[dict[int, str], dict[int, Exception]]:
        """Starts multiple servers in parallel."""
        return await self.run_bulk(servers, self.start)

    async def stop_many(
        self,
        servers: list['models.ServerBrief'],
    ) -> tuple[dict[int, str], dict[int, Exception]]:
        """Stops multiple servers in parallel."""
        return await self.run_bulk(servers, self.stop)

    async def shutdown_many(
        self,
        servers: list['models.ServerBrief'],
    ) -> tuple[dict[int, str], dict[int, Exception]]:
        """Shuts down multiple servers in parallel."""
        return await self.run_bulk(servers, self.shutdown)

    async def reboot_many(
        self,
        servers: list['models.ServerBrief'],
    ) -> tuple[dict[int, str], dict[int, Exception]]:
        """Reboots multiple servers in parallel."""
        return await self.run_bulk(servers, self.reboot)
