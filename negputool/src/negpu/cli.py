"""negpu command-line interface (Typer app).

This is the only entry point the user is expected to interact with directly:

    $ negpu                # interactive menu (planned for Phase 5)
    $ negpu --version      # version
    $ negpu doctor         # sanity checks (planned for Phase 2)
    $ negpu config-show    # show resolved config
    $ gpu-tool             # alias, same behaviour

All real work is delegated to sub-modules; this file only wires Typer commands
and contains no business logic.
"""

from __future__ import annotations

import asyncio
import sys
from typing import Annotated, Optional

import typer

from negpu._version import __version__

app = typer.Typer(
    name="negpu",
    help="negpu: async-first GPU/Server testing toolkit (reborn from gpu_tool).",
    no_args_is_help=True,
    rich_markup_mode="rich",
    add_completion=False,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"negpu {__version__} (Python {sys.version.split()[0]})")
        raise typer.Exit()


@app.callback()
def root(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            callback=_version_callback,
            is_eager=True,
            help="Show negpu version and exit.",
        ),
    ] = None,
    verbose: Annotated[
        int,
        typer.Option(
            "-v",
            "--verbose",
            count=True,
            help="Increase verbosity (-v, -vv).",
        ),
    ] = 0,
) -> None:
    """negpu root command (global options)."""


@app.command()
def doctor() -> None:
    """Print environment sanity checks (Phase 2 placeholder)."""
    typer.echo("negpu doctor: not yet implemented (scheduled for Phase 2).")


@app.command("config-show")
def config_show() -> None:
    """Show resolved configuration (Phase 2 placeholder)."""
    typer.echo("negpu config-show: not yet implemented (scheduled for Phase 2).")


@app.command()
def menu() -> None:
    """Launch the interactive async menu (Phase 5 placeholder)."""
    typer.echo("negpu menu: not yet implemented (scheduled for Phase 5).")


def main() -> None:
    """Console-script entry point."""
    try:
        app()
    except KeyboardInterrupt:  # pragma: no cover - interactive
        typer.echo("\n[Interrupted]", err=True)
        raise SystemExit(130) from None


if __name__ == "__main__":
    main()


# Re-export the symbol used by pyproject [project.scripts].
__all__ = ["app", "main"]


# Silence "imported but unused" for asyncio (used in later phases).
_ = asyncio