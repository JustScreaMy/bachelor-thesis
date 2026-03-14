from typing import TYPE_CHECKING

from .actions.group import GroupManager
from .actions.snapshot import SnapshotManager
from .actions.status import StatusManager

if TYPE_CHECKING:
    from .api import ProxmoxClient


class ActionService:
    """Service to coordinate all server actions through specialized managers."""

    def __init__(self, client: 'ProxmoxClient'):
        self.client = client
        self.status = StatusManager(client)
        self.snapshots = SnapshotManager(client)
        self.groups = GroupManager(client)
