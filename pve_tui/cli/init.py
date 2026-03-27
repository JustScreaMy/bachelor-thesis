import typer
from rich.console import Console

from ..core.utils import get_config_dir

console = Console()

SAMPLE_CONFIG = """\
[contexts.default]
base_url = "https://your-proxmox-host:8006"
token_id = "user@pam!token-name"
token = "your-token-secret"
verify_ssl = false
"""


def init() -> None:
    """Create a sample configuration file."""
    config_dir = get_config_dir('pve_tui')
    config_file = config_dir / 'config.toml'

    if config_file.exists():
        console.print(f'[yellow]Config already exists:[/yellow] {config_file}')
        raise typer.Exit()

    config_dir.mkdir(parents=True, exist_ok=True)
    config_file.write_text(SAMPLE_CONFIG)
    console.print(f'[green]Created config:[/green] {config_file}')
    console.print(
        'Edit it to add your Proxmox credentials, then run [bold]pve-tui[/bold].',
    )
