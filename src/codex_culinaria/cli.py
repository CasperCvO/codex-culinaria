from pathlib import Path
from typing import Annotated

import typer

from codex_culinaria import __version__
from codex_culinaria.vault import missing_dirs

VaultOption = Annotated[
    Path,
    typer.Option(
        "--vault",
        envvar="CULINARIA_VAULT",
        help="Path to the culinary vault.",
    ),
]


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"culinaria {__version__}")
        raise typer.Exit()


app = typer.Typer(
    no_args_is_help=True,
    help="Local-first culinary R&D vault tooling.",
)


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            callback=_version_callback,
            is_eager=True,
            help="Show the version and exit.",
        ),
    ] = False,
) -> None:
    pass


@app.command()
def check(vault: VaultOption = Path("vault")) -> None:
    """Check that the vault exists and has the required layout."""
    if not vault.is_dir():
        typer.echo(f"Vault not found: {vault}", err=True)
        raise typer.Exit(1)
    missing = missing_dirs(vault)
    if missing:
        for d in missing:
            typer.echo(f"Missing directory: {d}", err=True)
        raise typer.Exit(1)
    typer.echo(f"Vault OK: {vault}")
