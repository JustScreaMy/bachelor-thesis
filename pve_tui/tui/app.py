from textual.app import App

from ..core import models
from ..core.services.api import ProxmoxClient
from ..core.services.context import ServiceContext
from .screens import MainScreen


class PveTuiApp(App):
    """Main application class for the Proxmox VE TUI."""

    MODES = {'default': 'main'}

    SCREENS = {'main': MainScreen}

    application_config: models.ApplicationConfig
    services: ServiceContext

    def __init__(self, application_config: models.ApplicationConfig, **kwargs) -> None:
        super().__init__(**kwargs)

        self.application_config = application_config
        client = ProxmoxClient.from_config(self.application_config)
        self.services = ServiceContext(client)

    @property
    def discovery_service(self):
        return self.services.discovery

    @property
    def resource_service(self):
        return self.services.resource

    @property
    def action_service(self):
        return self.services.actions

    async def on_mount(self) -> None:
        self.log('ProxmoxClient health: %s', await self.services.client.is_healthy())
        await self.switch_mode('default')

    async def on_unmount(self) -> None:
        self.log('Closing Proxmox client session...')
        await self.services.close()
        self.log('Session closed.')
