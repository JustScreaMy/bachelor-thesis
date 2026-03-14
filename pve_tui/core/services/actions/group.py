from typing import TYPE_CHECKING

from .base import ActionManager

if TYPE_CHECKING:
    from ... import models


class GroupManager(ActionManager):
    """Handles grouping and tagging logic for servers."""

    async def add_to_group(self, server: 'models.ServerBrief', group_name: str) -> str:
        """Adds a 'pve-tui-{group_name}' tag to the server."""
        # path = self.get_path_config(server)
        # Fetch current tags, append 'pve-tui-{group_name}', then POST update
        # Implement tagging logic here
        raise NotImplementedError('Grouping (tagging) logic not yet implemented.')
