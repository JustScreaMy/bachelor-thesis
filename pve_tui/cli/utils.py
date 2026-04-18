from __future__ import annotations

import asyncio
import inspect
from functools import partial
from functools import wraps
from typing import Any
from typing import Callable

from rich.console import Console
from typer import Typer

from ..core.exceptions import AuthenticationError


class AsyncTyper(Typer):
    @staticmethod
    def maybe_run_async(decorator: Callable, func: Callable) -> Any:
        if inspect.iscoroutinefunction(func):

            @wraps(func)
            def runner(*args: Any, **kwargs: Any) -> Any:
                try:
                    return asyncio.run(func(*args, **kwargs))
                except FileNotFoundError as e:
                    console = Console()
                    console.print(f'[yellow]{e}[/yellow]')
                    console.print(
                        'Run [bold]pve init[/bold] to create a sample config.',
                    )
                    raise SystemExit(1)
                except AuthenticationError as e:
                    console = Console()
                    console.print(f'[bold red]Error:[/bold red] {e}')
                    raise SystemExit(1)

            decorator(runner)
        else:
            decorator(func)
        return func

    def callback(self, *args: Any, **kwargs: Any) -> Any:
        decorator = super().callback(*args, **kwargs)
        return partial(self.maybe_run_async, decorator)

    def command(self, *args: Any, **kwargs: Any) -> Any:
        decorator = super().command(*args, **kwargs)
        return partial(self.maybe_run_async, decorator)
