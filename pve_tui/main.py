from textual.app import App

from .core.utils import get_config_dir
from .core.utils import load_config
from .tui import PveTuiApp
from .tui.screens import NoConfigScreen


def _config_path() -> str:
    return str(get_config_dir('pve_tui') / 'config.toml')


def main() -> int:
    try:
        config = load_config()
        app = PveTuiApp(config)
    except FileNotFoundError:
        app = _NoConfigApp(_config_path())

    return app.run()


class _NoConfigApp(App):
    def __init__(self, config_path: str) -> None:
        super().__init__()
        self._config_path = config_path

    def on_mount(self) -> None:
        self.push_screen(NoConfigScreen(self._config_path))


if __name__ == '__main__':
    raise SystemExit(main())
