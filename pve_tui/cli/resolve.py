from rich.console import Console

from ..core.models.server import ServerBrief
from ..core.models.server import ServerGroupBrief
from ..core.services.context import ServiceContext


def _get_groups(servers: list[ServerBrief]) -> list[ServerGroupBrief]:
    """Derives groups from servers using the pve-tui- tag convention."""
    groups_dict: dict[str, list[ServerBrief]] = {}
    for server in servers:
        for tag in server.tags:
            if tag.startswith('pve-tui-'):
                group_name = tag[len('pve-tui-') :]
                if group_name not in groups_dict:
                    groups_dict[group_name] = []
                groups_dict[group_name].append(server)

    return [
        ServerGroupBrief(name=name, servers=members)
        for name, members in sorted(groups_dict.items())
    ]


async def resolve_targets(
    ctx: ServiceContext,
    targets: list[str],
) -> list[ServerBrief]:
    """Resolve a mixed list of VMIDs and group names to a deduplicated list of servers.

    Numeric targets are matched by VMID; non-numeric targets are matched by group name.
    Raises typer.BadParameter if any target cannot be resolved.
    """
    import typer

    servers = await ctx.discovery.fetch_all_servers()
    server_by_id = {s.server_id: s for s in servers}
    groups = _get_groups(servers)
    group_by_name = {g.name: g for g in groups}

    resolved: dict[int, ServerBrief] = {}
    errors: list[str] = []

    for target in targets:
        if target.isdigit():
            vmid = int(target)
            if vmid in server_by_id:
                resolved[vmid] = server_by_id[vmid]
            else:
                errors.append(f'VMID {vmid} not found')
        else:
            if target in group_by_name:
                for s in group_by_name[target].servers:
                    resolved[s.server_id] = s
            else:
                errors.append(f'Group "{target}" not found')

    if errors:
        raise typer.BadParameter('; '.join(errors))

    return list(resolved.values())


def report_bulk_result(
    console: Console,
    action_name: str,
    successes: dict[int, str],
    failures: dict[int, Exception],
) -> None:
    """Prints a summary of a bulk action result."""
    if successes:
        console.print(
            f'[green]{action_name} succeeded for {len(successes)} server(s): '
            f'{", ".join(str(v) for v in successes)}[/green]',
        )
    if failures:
        for vmid, exc in failures.items():
            console.print(f'[red]{action_name} failed for {vmid}: {exc}[/red]')
    if not successes and not failures:
        console.print(f'[yellow]No servers to {action_name.lower()}.[/yellow]')
