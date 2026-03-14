from textual.app import App

from ..core import models
from ..core.services.action import ActionService
from ..core.services.api import ProxmoxClient
from ..core.services.discovery import DiscoveryService
from ..core.services.resource import ResourceService
from .screens import MainScreen


class PveTuiApp(App):
    """Main application class for the Proxmox VE TUI."""

    MODES = {'default': 'main'}

    SCREENS = {'main': MainScreen}

    application_config: models.ApplicationConfig
    client: ProxmoxClient
    discovery_service: DiscoveryService
    resource_service: ResourceService
    action_service: ActionService

    def __init__(self, application_config: models.ApplicationConfig, **kwargs) -> None:
        super().__init__(**kwargs)

        self.application_config = application_config
        self.client = ProxmoxClient.from_config(self.application_config)

        self.resource_service = ResourceService(self.client)
        self.discovery_service = DiscoveryService(self.client, self.resource_service)
        self.action_service = ActionService(self.client)

    async def on_mount(self) -> None:
        self.log('ProxmoxClient health: %s', await self.client.is_healthy())
        await self.switch_mode('default')

    async def on_unmount(self) -> None:
        self.log('Closing Proxmox client session...')
        await self.client.close()
        self.log('Session closed.')
