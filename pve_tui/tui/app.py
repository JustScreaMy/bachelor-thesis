from textual.app import App, ComposeResult
from textual.widgets import Header, Footer

from .screens import MainScreen

class PveTuiApp(App):
    """Main application class for the Proxmox VE TUI."""

    MODES = {
        'default': 'main'
    }

    SCREENS = {
        'main': MainScreen
    }

    def on_mount(self) -> None:
        self.switch_mode('default')