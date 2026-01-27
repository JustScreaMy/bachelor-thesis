from .tui import PveTuiApp
from .shared.utils import load_config


def main() -> int:
    config = load_config()

    app = PveTuiApp(config)

    return app.run()


if __name__ == "__main__":
    raise SystemExit(main())
