from pathlib import Path

from typer.testing import CliRunner

from codex_culinaria import __version__
from codex_culinaria.cli import app
from codex_culinaria.vault import REQUIRED_DIRS

runner = CliRunner()


def _make_vault(root: Path, skip: tuple[str, ...] = ()) -> Path:
    for d in REQUIRED_DIRS:
        if d not in skip:
            (root / d).mkdir(parents=True)
    return root


def test_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert f"culinaria {__version__}" in result.output


def test_check_complete_vault(tmp_path: Path) -> None:
    vault = _make_vault(tmp_path / "vault")
    result = runner.invoke(app, ["check", "--vault", str(vault)])
    assert result.exit_code == 0
    assert "Vault OK" in result.output


def test_check_missing_dir(tmp_path: Path) -> None:
    vault = _make_vault(tmp_path / "vault", skip=("04_knowledge",))
    result = runner.invoke(app, ["check", "--vault", str(vault)])
    assert result.exit_code == 1
    assert "04_knowledge" in result.output


def test_check_nonexistent_vault(tmp_path: Path) -> None:
    result = runner.invoke(app, ["check", "--vault", str(tmp_path / "nope")])
    assert result.exit_code == 1
    assert "Vault not found" in result.output


def test_check_envvar_used_when_option_absent(tmp_path: Path) -> None:
    vault = _make_vault(tmp_path / "env_vault")
    result = runner.invoke(app, ["check"], env={"CULINARIA_VAULT": str(vault)})
    assert result.exit_code == 0
    assert "Vault OK" in result.output


def test_check_option_beats_envvar(tmp_path: Path) -> None:
    good = _make_vault(tmp_path / "good")
    missing = _make_vault(tmp_path / "missing", skip=("01_rd_lab",))
    result = runner.invoke(
        app,
        ["check", "--vault", str(good)],
        env={"CULINARIA_VAULT": str(missing)},
    )
    assert result.exit_code == 0
    assert "Vault OK" in result.output
