from typing import TYPE_CHECKING

from .base import ActionManager

if TYPE_CHECKING:
    from ... import models


class SnapshotManager(ActionManager):
    """Handles snapshot operations like creation and rollback."""

    async def create(
        self,
        server: 'models.ServerBrief',
        name: str,
        description: str = '',
    ) -> str:
        """Creates a snapshot."""
        # path = self.get_path_snapshot(server)
        # body = {"snapname": name, "description": description}
        # Implement snapshot creation logic here
        raise NotImplementedError('Snapshot creation logic not yet implemented.')

    async def rollback(
        self,
        server: 'models.ServerBrief',
        snapshot_name: str,
    ) -> str:
        """Rolls back the server to a specific snapshot."""
        # path = f"{self.get_path_snapshot(server)}/{snapshot_name}/rollback"
        # Implement snapshot rollback logic here
        raise NotImplementedError('Snapshot rollback logic not yet implemented.')
