from pathlib import Path
from typing import Annotated

import typer

from codex_culinaria import __version__
from codex_culinaria.vault import check_vault, format_vault, missing_dirs

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


def _ensure_vault_dirs(vault: Path) -> None:
    if not vault.is_dir():
        typer.echo(f"Vault not found: {vault}", err=True)
        raise typer.Exit(1)
    missing = missing_dirs(vault)
    if missing:
        for d in missing:
            typer.echo(f"Missing directory: {d}", err=True)
        raise typer.Exit(1)


@app.command()
def check(vault: VaultOption = Path("vault")) -> None:
    """Check that the vault layout, schemas, math and cross-references are valid."""
    _ensure_vault_dirs(vault)
    diagnostics = check_vault(vault)
    errors = [d for d in diagnostics if d.severity == "error"]
    warnings = [d for d in diagnostics if d.severity == "warning"]

    for d in warnings:
        typer.echo(d.format(vault), err=True)
    for d in errors:
        typer.echo(d.format(vault), err=True)

    if errors:
        raise typer.Exit(1)
    typer.echo(f"Vault OK: {vault}")


@app.command()
def fmt(
    vault: VaultOption = Path("vault"),
    check_only: Annotated[
        bool,
        typer.Option(
            "--check",
            help="Report files that would be reformatted without writing changes.",
        ),
    ] = False,
) -> None:
    """Normalize recipe formulas, phase tables, ingredient overview tables and aliases."""
    _ensure_vault_dirs(vault)
    modified, diagnostics = format_vault(vault, check_only=check_only)
    for d in diagnostics:
        typer.echo(d.format(vault), err=True)
    if diagnostics:
        raise typer.Exit(1)

    if check_only:
        if modified:
            for p in modified:
                rel = p.relative_to(vault) if p.is_relative_to(vault) else p
                typer.echo(f"Would reformat: {rel}", err=True)
            raise typer.Exit(1)
        typer.echo(f"All files formatted: {vault}")
        return

    for p in modified:
        rel = p.relative_to(vault) if p.is_relative_to(vault) else p
        typer.echo(f"Formatted: {rel}")
    typer.echo(f"Formatted {len(modified)} file(s) in {vault}")
