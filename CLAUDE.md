# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

pve_tui — a Python TUI and CLI for managing Proxmox VE clusters. The TUI uses Textual, the CLI uses Typer. Both share a core service layer that talks to the Proxmox API via aiohttp.

## Commands

```bash
# Run TUI
pve-tui

# Run CLI
pve <command>
```

### Development

```bash
# Install with dev dependencies
uv sync

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

## Installation

```bash
# Via uv (recommended)
uv tool install pve-tui --index-url https://git.kropcloud.net/api/packages/JustScreaMy/pypi/simple/ --extra-index-url https://pypi.org/simple/

# Via pipx
pipx install pve-tui --index-url https://git.kropcloud.net/api/packages/JustScreaMy/pypi/simple/ --pip-args='--extra-index-url https://pypi.org/simple/'
```

Package is hosted on a Forgejo PyPI registry at `git.kropcloud.net`.

## Release Cycle

Versioning is managed by **bumpver** (dev dependency). The release flow:

1. `uv run bumpver update --patch` (or `--minor`/`--major`) bumps version in `pyproject.toml`, runs `scripts/pre-bump.sh` (which updates `uv.lock`), commits, and creates a git tag.
2. Pushing the tag to `master` triggers the **Woodpecker CI** pipeline (`.woodpecker/release.yaml`).
3. CI builds the package with `uv build` and publishes to the Forgejo PyPI registry.

Do **not** push tags without ensuring `uv.lock` is in sync — the pre-bump hook handles this automatically.

## Code Style

- Python 3.14+, single quotes, ruff for linting/formatting
- Imports are reordered by `reorder-python-imports` (pre-commit hook)
- Trailing commas enforced by `add-trailing-comma`
