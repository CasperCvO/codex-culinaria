from pathlib import Path

from codex_culinaria.vault import REQUIRED_DIRS, missing_dirs


def _make_tree(root: Path, dirs: tuple[str, ...] = REQUIRED_DIRS) -> None:
    for d in dirs:
        (root / d).mkdir(parents=True)


def test_complete_tree_returns_nothing(tmp_path: Path) -> None:
    _make_tree(tmp_path)
    assert missing_dirs(tmp_path) == []


def test_missing_dirs_in_contract_order(tmp_path: Path) -> None:
    missing = ("00_context/skills", "03_reference/ingredients")
    _make_tree(tmp_path, tuple(d for d in REQUIRED_DIRS if d not in missing))
    assert missing_dirs(tmp_path) == [
        "00_context/skills",
        "03_reference/ingredients",
    ]


def test_file_where_dir_should_be_counts_as_missing(tmp_path: Path) -> None:
    _make_tree(tmp_path)
    target = tmp_path / "01_rd_lab"
    target.rmdir()
    target.touch()
    assert missing_dirs(tmp_path) == ["01_rd_lab"]
