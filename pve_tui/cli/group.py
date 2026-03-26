from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from ..core.services.context import create_service_context
from .resolve import _get_groups
from .resolve import report_bulk_result
from .resolve import resolve_targets
from .utils import AsyncTyper

group_app = AsyncTyper(name='group', help='Manage server groups.')
console = Console()


@group_app.command(name='list')
async def list_groups() -> None:
    """List all groups and their members."""
    async with create_service_context() as ctx:
        servers = await ctx.discovery.fetch_all_servers()

    groups = _get_groups(servers)

    if not groups:
        console.print('No groups found.')
        raise typer.Exit()

    table = Table(title='Server Groups')
    table.add_column('Group', style='cyan')
    table.add_column('Members', justify='right', style='green')
    table.add_column('VMIDs', style='white')

    for g in groups:
        vmids = ', '.join(str(v) for v in sorted(g.server_ids))
        table.add_row(g.name, str(len(g.servers)), vmids)

    console.print(table)


@group_app.command()
async def add(
    group_name: Annotated[
        str,
        typer.Argument(help='Name of the group to add servers to.'),
    ],
    targets: Annotated[list[str], typer.Argument(help='VMIDs or group names to add.')],
) -> None:
    """Add servers to a group (creates it if it doesn't exist)."""
    async with create_service_context() as ctx:
        servers = await resolve_targets(ctx, targets)
        successes, failures = await ctx.actions.groups.create_group_with_servers(
            servers,
            group_name,
        )
        report_bulk_result(console, f'Add to group "{group_name}"', successes, failures)


@group_app.command()
async def remove(
    group_name: Annotated[str, typer.Argument(help='Name of the group to remove.')],
) -> None:
    """Remove an entire group (untags all member servers)."""
    async with create_service_context() as ctx:
        servers = await ctx.discovery.fetch_all_servers()
        groups = _get_groups(servers)
        group_by_name = {g.name: g for g in groups}

        if group_name not in group_by_name:
            console.print(f'[red]Group "{group_name}" not found.[/red]')
            raise typer.Exit(code=1)

        target_group = group_by_name[group_name]
        successes, failures = await ctx.actions.groups.remove_groups([target_group])
        report_bulk_result(console, f'Remove group "{group_name}"', successes, failures)


@group_app.command()
async def detach(
    group_name: Annotated[str, typer.Argument(help='Group to detach servers from.')],
    targets: Annotated[
        list[str],
        typer.Argument(help='VMIDs or group names to detach.'),
    ],
) -> None:
    """Detach specific servers from a group."""
    async with create_service_context() as ctx:
        servers = await resolve_targets(ctx, targets)

        successes: dict[int, str] = {}
        failures: dict[int, Exception] = {}

        for server in servers:
            try:
                result = await ctx.actions.groups.remove_from_group(server, group_name)
                successes[server.server_id] = result
            except Exception as exc:
                failures[server.server_id] = exc

        report_bulk_result(console, f'Detach from "{group_name}"', successes, failures)
