from typing import TYPE_CHECKING

from .base import ActionManager

if TYPE_CHECKING:
    from ... import models


class GroupManager(ActionManager):
    """
    Handles grouping logic by managing Proxmox tags with 'pve-tui-' prefix.
    """

    @staticmethod
    def _format_tag(group_name: str) -> str:
        """Ensures the group name has the correct prefix."""
        if group_name.startswith('pve-tui-'):
            return group_name
        return f'pve-tui-{group_name}'

    async def _update_tags(self, server: 'models.ServerBrief', tags: list[str]) -> str:
        """Sends the updated tag list to the Proxmox API."""
        path = self.get_path_config(server)
        # Proxmox expects tags as a separated string (usually semicolon)
        tag_string = ';'.join(tags)
        payload = {'tags': tag_string}

        async with self.client.request(path, method='PUT', json=payload) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data.get('data')  # Returns UPID

    async def add_to_group(self, server: 'models.ServerBrief', group_name: str) -> str:
        """Adds a specific group tag to a single server."""
        tag = self._format_tag(group_name)
        if tag in server.tags:
            return ''  # Already in group

        new_tags = list(server.tags)
        new_tags.append(tag)
        return await self._update_tags(server, new_tags)

    async def remove_from_group(
        self,
        server: 'models.ServerBrief',
        group_name: str,
    ) -> str:
        """Removes a specific group tag from a single server."""
        tag = self._format_tag(group_name)
        if tag not in server.tags:
            return ''  # Not in group

        new_tags = [t for t in server.tags if t != tag]
        return await self._update_tags(server, new_tags)

    # Bulk Actions
    async def create_group_with_servers(
        self,
        servers: list['models.ServerBrief'],
        group_name: str,
    ) -> tuple[dict[int, str], dict[int, Exception]]:
        """Adds multiple servers to a new or existing group."""

        async def _add(s: 'models.ServerBrief'):
            return await self.add_to_group(s, group_name)

        return await self.run_bulk(servers, _add)

    async def remove_groups(
        self,
        groups: list['models.ServerGroupBrief'],
    ) -> tuple[dict[int, str], dict[int, Exception]]:
        """
        Removes all selected groups by stripping their tags from all
        associated servers.
        """
        # Create a map of server_id -> (server, tags_to_remove)
        server_map: dict[int, tuple['models.ServerBrief', set[str]]] = {}

        for group in groups:
            tag = self._format_tag(group.name)
            for server in group.servers:
                if server.server_id not in server_map:
                    server_map[server.server_id] = (server, set())
                server_map[server.server_id][1].add(tag)

        # Process the removal
        servers_to_process = [item[0] for item in server_map.values()]

        async def _process_wrapper(server: 'models.ServerBrief'):
            _, tags_to_remove = server_map[server.server_id]
            # Strip the tags
            new_tags = [t for t in server.tags if t not in tags_to_remove]
            return await self._update_tags(server, new_tags)

        return await self.run_bulk(servers_to_process, _process_wrapper)
