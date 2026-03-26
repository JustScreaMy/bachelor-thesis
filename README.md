# pve_tui

A terminal-based tool for managing Proxmox VE clusters. Provides both an interactive TUI and a CLI.

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) package manager

## Installation

```bash
uv sync
```

## Configuration

Create a config file at one of these locations (checked in order):

1. `./config.toml` (current directory)
2. `~/.config/pve_tui/config.toml` (Linux)
3. `~/Library/Application Support/pve_tui/config.toml` (macOS)
4. `%APPDATA%/pve_tui/config.toml` (Windows)

```toml
[contexts.my-cluster]
base_url = "https://proxmox.example.com"
token_id = "your_token_id"
token = "your_secret_token"
```

Multiple contexts are supported for managing several clusters. See `config.example.toml` for reference.

Environment variables `PVE_TOKEN_ID` and `PVE_TOKEN` override config values.

## Usage

### TUI

```bash
uv run pve-tui
```

Interactive split-view interface with server/group list on the left and details/actions on the right.

**Keybindings:**

| Key       | Action                     |
| --------- | -------------------------- |
| `r`       | Refresh server list        |
| `g`       | Toggle servers/groups view |
| `Up/Down` | Navigate list              |
| `Space`   | Select/deselect item       |
| `Tab`     | Switch panes               |
| `q`       | Quit                       |

### CLI

```bash
uv run pve [command]
```

All commands accept VMIDs or group names as targets.

**Server management:**

```bash
pve list                        # List all servers
pve server start <targets...>   # Start servers
pve server stop <targets...>    # Hard power off
pve server shutdown <targets...> # Graceful shutdown
pve server reboot <targets...>  # Reboot
```

**Snapshots:**

```bash
pve snapshot list <target>                      # List snapshots
pve snapshot create <targets...> [--name NAME]  # Create snapshot
pve snapshot rollback <targets...>              # Rollback to latest
pve snapshot rollback <targets...> --snapshot NAME  # Rollback to specific
```

**Groups:**

Groups are stored as Proxmox tags with a `pve-tui-` prefix.

```bash
pve group list                          # List all groups
pve group add <group> <targets...>      # Add servers to group
pve group remove <group>                # Remove entire group
pve group detach <group> <targets...>   # Detach servers from group
```

## Development

```bash
# Lint
uv run ruff check .

# Format
uv run ruff format .

# Pre-commit hooks
prek run --all-files
```
