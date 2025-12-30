from .tui import PveTuiApp

def main() -> int:
    """Entry point for the Proxmox VE TUI application."""

    app = PveTuiApp()
    return app.run()

if __name__ == '__main__':
    raise SystemExit(main())