from typing import Annotated

import typer
from rich.console import Console

from ..core.models.server import ServerStatus
from ..core.services.context import create_service_context
from .resolve import report_bulk_result
from .resolve import resolve_targets
from .utils import AsyncTyper

server_app = AsyncTyper(name='server', help='Manage server power state.')
console = Console()


async def _run_status_action(
    targets: list[str],
    action_name: str,
    required_status: ServerStatus | None,
) -> None:
    """Common logic for all status commands."""
    async with create_service_context() as ctx:
        servers = await resolve_targets(ctx, targets)

        if required_status is not None:
            applicable = [s for s in servers if s.status == required_status]
            skipped = len(servers) - len(applicable)
            if skipped:
                console.print(
                    f'[yellow]Skipping {skipped} server(s) not in '
                    f'"{required_status.value}" state.[/yellow]',
                )
            servers = applicable

        if not servers:
            console.print(f'[yellow]No servers to {action_name}.[/yellow]')
            raise typer.Exit()

        action_func = getattr(ctx.actions.status, f'{action_name}_many')
        successes, failures = await action_func(servers)
        report_bulk_result(console, action_name.capitalize(), successes, failures)


@server_app.command()
async def start(
    targets: Annotated[
        list[str],
        typer.Argument(help='VMIDs or group names to start.'),
    ],
) -> None:
    """Start one or more servers."""
    await _run_status_action(targets, 'start', ServerStatus.Stopped)


@server_app.command()
async def stop(
    targets: Annotated[list[str], typer.Argument(help='VMIDs or group names to stop.')],
) -> None:
    """Stop one or more servers (hard power off)."""
    await _run_status_action(targets, 'stop', ServerStatus.Running)


@server_app.command()
async def shutdown(
    targets: Annotated[
        list[str],
        typer.Argument(help='VMIDs or group names to shut down.'),
    ],
) -> None:
    """Gracefully shut down one or more servers."""
    await _run_status_action(targets, 'shutdown', ServerStatus.Running)


@server_app.command()
async def reboot(
    targets: Annotated[
        list[str],
        typer.Argument(help='VMIDs or group names to reboot.'),
    ],
) -> None:
    """Reboot one or more servers."""
    await _run_status_action(targets, 'reboot', ServerStatus.Running)
