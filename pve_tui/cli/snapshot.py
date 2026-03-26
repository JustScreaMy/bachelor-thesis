from datetime import datetime
from datetime import timezone
from typing import Annotated
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ..core.services.context import create_service_context
from .resolve import report_bulk_result
from .resolve import resolve_targets
from .utils import AsyncTyper

snapshot_app = AsyncTyper(name='snapshot', help='Manage server snapshots.')
console = Console()


@snapshot_app.command(name='list')
async def list_snapshots(
    target: Annotated[
        str,
        typer.Argument(help='VMID or group name to list snapshots for.'),
    ],
) -> None:
    """List snapshots for a single server."""
    async with create_service_context() as ctx:
        servers = await resolve_targets(ctx, [target])

        if len(servers) > 1:
            console.print(
                '[yellow]Multiple servers resolved; showing snapshots for each.[/yellow]',
            )

        for server in servers:
            snapshots = await ctx.actions.snapshots.list_snapshots(server)
            valid = [s for s in snapshots if s.get('name') != 'current']
            valid.sort(key=lambda x: x.get('snaptime', 0), reverse=True)

            table = Table(title=f'Snapshots for {server.name} ({server.server_id})')
            table.add_column('Name', style='cyan')
            table.add_column('Description', style='white')
            table.add_column('Date', style='green')

            for snap in valid:
                snap_time = snap.get('snaptime', 0)
                date_str = (
                    datetime.fromtimestamp(snap_time, tz=timezone.utc).strftime(
                        '%Y-%m-%d %H:%M:%S',
                    )
                    if snap_time
                    else 'N/A'
                )
                table.add_row(
                    snap.get('name', ''),
                    snap.get('description', ''),
                    date_str,
                )

            if not valid:
                console.print(
                    f'No snapshots found for {server.name} ({server.server_id}).',
                )
            else:
                console.print(table)


@snapshot_app.command()
async def create(
    targets: Annotated[
        list[str],
        typer.Argument(help='VMIDs or group names to snapshot.'),
    ],
    name: Annotated[
        Optional[str],
        typer.Option('--name', '-n', help='Snapshot name (defaults to timestamp).'),
    ] = None,
    description: Annotated[
        str,
        typer.Option('--description', '-d', help='Snapshot description.'),
    ] = '',
) -> None:
    """Create a snapshot for one or more servers."""
    if name is None:
        name = datetime.now(tz=timezone.utc).strftime('snap-%Y%m%d-%H%M%S')

    async with create_service_context() as ctx:
        servers = await resolve_targets(ctx, targets)
        successes, failures = await ctx.actions.snapshots.create_many(
            servers,
            name,
            description,
        )
        report_bulk_result(console, 'Snapshot create', successes, failures)


@snapshot_app.command()
async def rollback(
    targets: Annotated[
        list[str],
        typer.Argument(help='VMIDs or group names to rollback.'),
    ],
) -> None:
    """Rollback one or more servers to their latest snapshot."""
    async with create_service_context() as ctx:
        servers = await resolve_targets(ctx, targets)
        successes, failures = await ctx.actions.snapshots.rollback_to_latest_many(
            servers,
        )
        report_bulk_result(console, 'Snapshot rollback', successes, failures)
