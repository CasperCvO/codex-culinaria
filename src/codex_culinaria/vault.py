from pathlib import Path

REQUIRED_DIRS: tuple[str, ...] = (
    "00_context/equipment",
    "00_context/skills",
    "01_rd_lab",
    "02_library/components",
    "02_library/dishes",
    "03_reference/ingredients",
    "04_knowledge",
)


def missing_dirs(root: Path) -> list[str]:
    """Return the REQUIRED_DIRS entries that are not directories under ``root``."""
    return [d for d in REQUIRED_DIRS if not (root / d).is_dir()]
