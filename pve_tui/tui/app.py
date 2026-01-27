from textual.app import App

from .screens import MainScreen
from ..shared import models
from ..shared.api_client import APIClient

class PveTuiApp(App):
    """Main application class for the Proxmox VE TUI."""

    MODES = {"default": "main"}

    SCREENS = {"main": MainScreen}

    application_config: models.ApplicationConfig
    api_client: APIClient

    def __init__(self, application_config: models.ApplicationConfig, **kwargs) -> None:
        super().__init__(**kwargs)

        self.application_config = application_config
        self.api_client = APIClient.from_config(self.application_config)

        self.log("APIClient health: %s", self.api_client.is_healthy())

    def on_mount(self) -> None:
        self.switch_mode("default")
