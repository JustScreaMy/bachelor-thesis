from rich.console import Console
from rich.table import Table

from ..core.services.api import ProxmoxClient
from ..core.services.cluster import ClusterService
from ..core.utils import load_config
from .utils import AsyncTyper

app = AsyncTyper()
console = Console()


@app.command(name='list')
async def list_servers() -> None:
    """List all servers in the Proxmox cluster."""
    config = load_config()
    client = ProxmoxClient.from_config(config)
    service = ClusterService(client)

    try:
        servers = await service.fetch_servers_brief()
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
    finally:
        await client.close()


@app.command()
def version() -> None:
    """Show the version of pve-tui."""
    console.print('pve-tui version 0.1.0')


if __name__ == '__main__':
    app()
