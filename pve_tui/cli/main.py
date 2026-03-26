from importlib.metadata import version as get_version
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from ..core.services.context import create_service_context
from .group import group_app
from .server import server_app
from .snapshot import snapshot_app
from .utils import AsyncTyper


def _version_callback(value: bool) -> None:
    if value:
        Console().print(f'pve-tui version {get_version("pve_tui")}')
        raise typer.Exit()


app = AsyncTyper()
app.add_typer(server_app)
app.add_typer(snapshot_app)
app.add_typer(group_app)
console = Console()


@app.callback(invoke_without_command=True)
def main(
    version: Annotated[
        bool,
        typer.Option(
            '--version',
            '-v',
            help='Show the version and exit.',
            callback=_version_callback,
            is_eager=True,
        ),
    ] = False,
) -> None:
    """Proxmox VE CLI tool."""


@app.command(name='list')
async def list_servers() -> None:
    """List all servers in the Proxmox cluster."""
    try:
        async with create_service_context() as ctx:
            servers = await ctx.discovery.fetch_all_servers()
    except FileNotFoundError as e:
        console.print(f'[red]Configuration error:[/red] {e}')
        raise SystemExit(1)
    except Exception as e:
        console.print(f'[red]Failed to fetch servers:[/red] {e}')
        raise SystemExit(1)

    servers.sort(key=lambda x: x.server_id)

    table = Table(title='Proxmox Servers')
    table.add_column('ID', justify='right', style='cyan')
    table.add_column('Name', style='magenta')
    table.add_column('Node', style='green')
    table.add_column('Type', style='yellow')
    table.add_column('Status', style='bold')
    table.add_column('CPU %', justify='right')
    table.add_column('Memory', justify='right')

    for s in servers:
        status_style = 'green' if s.status == 'running' else 'red'
        mem_mb = s.memory_used / (1024 * 1024)
        max_mem_mb = s.memory / (1024 * 1024)

        table.add_row(
            str(s.server_id),
            s.name,
            s.node,
            s.type.value,
            f'[{status_style}]{s.status.value}[/{status_style}]',
            f'{s.cpu_usage * 100:.1f}%',
            f'{mem_mb:.0f} / {max_mem_mb:.0f} MB',
        )

    console.print(table)
