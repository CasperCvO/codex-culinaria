import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import yaml

Severity = Literal["error", "warning"]

ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

VALID_DOMAINS: frozenset[str] = frozenset(
    {
        "frozen",
        "pastry",
        "bread",
        "savory",
        "preserves",
        "confectionery",
        "beverage",
    }
)


@dataclass(frozen=True, slots=True)
class Diagnostic:
    path: Path
    message: str
    severity: Severity = "error"

    def format(self, vault_root: Path | None = None) -> str:
        rel = self.path
        if vault_root is not None:
            try:
                rel = self.path.relative_to(vault_root)
            except ValueError:
                rel = self.path
        prefix = "ERROR" if self.severity == "error" else "WARN"
        return f"{prefix}: {rel}: {self.message}"


def is_valid_id(value: str) -> bool:
    return bool(ID_PATTERN.match(value))


def split_frontmatter(text: str, path: Path) -> tuple[dict[str, Any], str, str, list[Diagnostic]]:
    """Split a Markdown file into (parsed_frontmatter, raw_frontmatter_block, body, diagnostics).

    ``raw_frontmatter_block`` includes the opening and closing ``---`` lines and trailing newline.
    """
    diagnostics: list[Diagnostic] = []
    if not text.startswith("---\n"):
        diagnostics.append(Diagnostic(path, "Missing YAML frontmatter at start of file."))
        return {}, "", text, diagnostics

    end_idx = text.find("\n---\n", 4)
    if end_idx == -1:
        if text.endswith("\n---"):
            end_idx = len(text) - 4
            raw_yaml = text[4:end_idx]
            raw_block = text
            body = ""
        else:
            diagnostics.append(Diagnostic(path, "Unclosed YAML frontmatter block."))
            return {}, "", text, diagnostics
    else:
        raw_yaml = text[4:end_idx]
        raw_block = text[: end_idx + 5]
        body = text[end_idx + 5 :]

    try:
        loaded = yaml.safe_load(raw_yaml)
    except yaml.YAMLError as exc:
        diagnostics.append(Diagnostic(path, f"Invalid YAML frontmatter: {exc}"))
        return {}, raw_block, body, diagnostics

    if loaded is None:
        loaded = {}
    if not isinstance(loaded, dict):
        diagnostics.append(Diagnostic(path, "YAML frontmatter must be a mapping."))
        return {}, raw_block, body, diagnostics

    return loaded, raw_block, body, diagnostics


def parse_number_or_range(
    value: Any,
    key: str,
    path: Path,
    *,
    allow_range: bool = True,
) -> tuple[float | tuple[float, float] | None, list[Diagnostic]]:
    """Validate a plain number or [min, max] range from YAML."""
    diagnostics: list[Diagnostic] = []
    if isinstance(value, bool):
        diagnostics.append(Diagnostic(path, f"'{key}' must be a number, got boolean."))
        return None, diagnostics
    if isinstance(value, (int, float)):
        return float(value), diagnostics
    if allow_range and isinstance(value, list) and len(value) == 2:
        low, high = value
        if (
            not isinstance(low, bool)
            and not isinstance(high, bool)
            and isinstance(low, (int, float))
            and isinstance(high, (int, float))
        ):
            if float(low) > float(high):
                diagnostics.append(
                    Diagnostic(path, f"'{key}' range minimum ({low}) exceeds maximum ({high}).")
                )
            return (float(low), float(high)), diagnostics
    expected = "a number or [min, max] range" if allow_range else "a number"
    diagnostics.append(Diagnostic(path, f"'{key}' must be {expected}, got {value!r}."))
    return None, diagnostics


def format_percentage(pct: float) -> str:
    """Format a percentage according to recipe-format.md:
    - >= 1%: 1 decimal
    - 0.1% to < 1%: 2 decimals
    - < 0.1%: 3 decimals
    """
    if round(pct, 2) >= 1.0:
        return f"{pct:.1f}%"
    if round(pct, 3) >= 0.1:
        return f"{pct:.2f}%"
    return f"{pct:.3f}%"
