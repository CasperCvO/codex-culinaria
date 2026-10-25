import re
from pathlib import Path

import pytest

from codex_culinaria.equipment import parse_equipment
from codex_culinaria.ingredients import format_ingredient_family, parse_ingredient_family
from codex_culinaria.recipes import format_recipe, parse_recipe

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "docs" / "specs" / "examples"
EQUIPMENT_EXAMPLES = sorted((EXAMPLES_DIR / "equipment").glob("*.md"))
INGREDIENT_EXAMPLES = sorted((EXAMPLES_DIR / "ingredients").glob("*.md"))
RECIPE_EXAMPLES = sorted(EXAMPLES_DIR.glob("*.md"))


@pytest.mark.parametrize("path", EQUIPMENT_EXAMPLES, ids=lambda p: p.stem)
def test_equipment_examples_valid(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    eq, diagnostics = parse_equipment(text, path)
    assert diagnostics == []
    assert eq is not None
    assert eq.id == path.stem


@pytest.mark.parametrize("path", INGREDIENT_EXAMPLES, ids=lambda p: p.stem)
def test_ingredient_examples_valid_and_idempotent(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    family, diagnostics = parse_ingredient_family(text, path)
    assert diagnostics == []
    assert family is not None

    formatted, fmt_diags = format_ingredient_family(text, path)
    assert fmt_diags == []
    assert formatted == text

    stripped = re.sub(
        r"<!-- culinaria:overview.*?<!-- /culinaria:overview -->\n\n",
        "",
        text,
        flags=re.DOTALL,
    )
    regenerated, regen_diags = format_ingredient_family(stripped, path)
    assert regen_diags == []
    assert regenerated == text


@pytest.mark.parametrize("path", RECIPE_EXAMPLES, ids=lambda p: p.stem)
def test_recipe_examples_valid_and_idempotent(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    recipe, diagnostics = parse_recipe(text, path)
    assert diagnostics == []
    assert recipe is not None

    formatted, fmt_diags = format_recipe(text, path)
    assert fmt_diags == []
    assert formatted == text

    stripped_phases = re.sub(
        r"<!-- culinaria:phase.*?<!-- /culinaria:phase -->\n\n",
        "",
        text,
        flags=re.DOTALL,
    )
    regenerated, regen_diags = format_recipe(stripped_phases, path)
    assert regen_diags == []
    assert regenerated == text
