# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

pve_tui — a Python TUI and CLI for managing Proxmox VE clusters. The TUI uses Textual, the CLI uses Typer. Both share a core service layer that talks to the Proxmox API via aiohttp.

## Commands

```bash
# Install dependencies
uv sync

# Run TUI
uv run pve-tui

# Run CLI
uv run pve <command>

# Lint & format (via prek / ruff)
uv run ruff check .
uv run ruff format .

# Run pre-commit hooks
prek run --all-files
```

No test suite exists yet.

## Architecture

```
pve_tui/
├── core/           # Shared business logic
│   ├── models/     # Dataclasses: ServerBrief, ServerGroupBrief, ApplicationConfig, etc.
│   ├── services/   # Service layer
│   │   ├── api.py          # ProxmoxClient (async aiohttp client)
│   │   ├── context.py      # ServiceContext (DI container for all services)
│   │   ├── discovery.py    # Discovers nodes and servers
│   │   ├── resource.py     # Fetches detailed server info (QEMU/LXC)
│   │   └── actions/        # Action managers: status, snapshot, group
│   └── utils.py    # Config loading, platform-specific config paths
├── tui/            # Textual TUI
│   ├── app.py      # PveTuiApp entry point
│   ├── screens/    # MainScreen with split view (list + detail/actions)
│   └── widgets/    # MultiselectListView, ServerBrief, SplitView, etc.
├── cli/            # Typer CLI
│   ├── main.py     # CLI entry, context selection
│   ├── server.py   # start/stop/shutdown/reboot commands
│   ├── snapshot.py # list/create/delete/rollback commands
│   └── resolve.py  # Resolves targets (VMID or group name) to servers
└── main.py         # TUI launcher
```

**Entry points** (pyproject.toml): `pve-tui` → TUI, `pve` → CLI.

**Key patterns:**

- Async everywhere — aiohttp client, asyncio concurrency
- ServiceContext holds ProxmoxClient + all services, injected into TUI app and CLI
- Action managers (`status`, `snapshot`, `group`) support bulk operations with parallel execution
- Server groups are derived from Proxmox tags with `pve-tui-` prefix
- Config: TOML with multi-context support, env var overrides (`PVE_TOKEN_ID`, `PVE_TOKEN`)

## Code Style

- Python 3.14+, single quotes, ruff for linting/formatting
- Imports are reordered by `reorder-python-imports` (pre-commit hook)
- Trailing commas enforced by `add-trailing-comma`
