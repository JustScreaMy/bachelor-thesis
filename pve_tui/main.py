from .tui import PveTuiApp
from .core.utils import load_config

def create_app() -> PveTuiApp:
    config = load_config()
    return PveTuiApp(config)

def main() -> int:
    app = create_app()

    return app.run()


if __name__ == "__main__":
    raise SystemExit(main())
