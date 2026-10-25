from pathlib import Path

from typer.testing import CliRunner

from codex_culinaria.cli import app
from codex_culinaria.equipment import parse_equipment
from codex_culinaria.ingredients import format_ingredient_family, parse_ingredient_family
from codex_culinaria.recipes import format_recipe, parse_recipe
from codex_culinaria.vault import REQUIRED_DIRS, check_vault

runner = CliRunner()


def _make_vault(root: Path) -> Path:
    for d in REQUIRED_DIRS:
        (root / d).mkdir(parents=True, exist_ok=True)
    return root


def test_ingredient_inheritance_and_provenance(tmp_path: Path) -> None:
    md = """---
kind: ingredient_family
category: grain
calculators:
  - hydration
---

# Rijst

Intro.

## Basmatirijst

```yaml
aliases:
  - Basmati
water_pct: 12.0
solids_pct: 88.0
carbs_pct: 77.7
protein_pct: 7.8
fat_pct: 0.8
amylose_pct: 22.0
hydration_ratio: 1.15
steaming_min: 15
source_type: datasheet
source: Tilda datasheet
unverified:
  - amylose_pct
```

### Rahman Superbasmati

```yaml
brand: Rahman
hydration_ratio: 1.10
steaming_min: [14, 16]
source_type: unverified
source: LLM chat
```
"""
    path = tmp_path / "rijst.md"
    formatted, diags = format_ingredient_family(md, path)
    assert diags == []

    family, check_diags = parse_ingredient_family(formatted, path)
    assert check_diags == []
    assert family is not None
    assert len(family.resolved) == 2

    parent, variant = family.resolved
    assert parent.name == "Basmatirijst"
    assert parent.aliases == ("Basmati",)
    assert parent.provenance["water_pct"].is_unverified is False
    assert parent.provenance["amylose_pct"].is_unverified is True

    assert variant.name == "Rahman Superbasmati"
    assert variant.aliases == ()
    assert variant.brand == "Rahman"
    assert variant.properties["water_pct"] == 12.0
    assert variant.properties["hydration_ratio"] == 1.10
    assert variant.properties["steaming_min"] == (14.0, 16.0)
    assert variant.provenance["water_pct"].source_type == "datasheet"
    assert variant.provenance["water_pct"].is_unverified is False
    assert variant.provenance["hydration_ratio"].source_type == "unverified"
    assert variant.provenance["hydration_ratio"].is_unverified is True


def test_recipe_fmt_computes_math_rewrites_aliases_and_adds_phases(tmp_path: Path) -> None:
    raw_recipe = """---
kind: dish
status: testing
version: "1.0"
domain: pastry
basis: flour
equipment:
  - Heteluchtoven
portion_g: 22
---

# Koek

## Formule

| Ingrediënt | Gewicht (g) | Schaling (%) | Batch (%) | Opmerking |
| :--- | ---: | ---: | ---: | :--- |
| **Deeg** | | | | |
| Franse bloem T55 | 100,0 | | | |
| Suiker | 50,0 | | | |
| Zout | q.s. | | | |
| → Na rusten | 148,0 | | | |
| **Totaal (inzet)** | **0.0** | **0.0%** | **100.0%** | |

## Bereiding

1. Meng alles en weeg porties van 22 g af.

## Iteratielog

### v1.0 - 2026-10-25

- Eerste test.
"""
    path = tmp_path / "koek.md"
    formatted, diags = format_recipe(
        raw_recipe,
        path,
        ingredient_aliases={"Franse bloem T55": "T55 bloem", "Suiker": "Kristalsuiker"},
        equipment_aliases={"Heteluchtoven": "Oven"},
        flour_names=frozenset({"T55 bloem"}),
    )
    assert diags == []
    assert "  - Oven\n" in formatted
    assert "| **T55 bloem** | 100.0 | 100.0% | 66.7% | |" in formatted
    assert "| Kristalsuiker | 50.0 | 50.0% | 33.3% | |" in formatted
    assert "| Zout | q.s. | | | |" in formatted
    assert "| → Na rusten | 148.0 | 148.0% | 98.7% | |" in formatted
    assert "| **Totaal (inzet)** | **150.0** | **150.0%** | **100.0%** | |" in formatted
    assert (
        "_Schaling: % van T55 bloem, 100.0 g. Batch: % van de totale inzet, 150.0 g._" in formatted
    )
    assert "### Deeg\n\n<!-- culinaria:phase" in formatted

    recipe, check_diags = parse_recipe(formatted, path, flour_names=frozenset({"T55 bloem"}))
    assert check_diags == []
    assert recipe is not None
    assert recipe.total_g == 150.0


def test_recipe_total_basis_omits_schaling_column(tmp_path: Path) -> None:
    raw_recipe = """---
kind: component
status: testing
version: "1.0"
domain: savory
basis: total
---

# Kruidenmix

## Formule

| Ingrediënt | Gewicht (g) | Batch (%) | Opmerking |
| :--- | ---: | ---: | :--- |
| Zout | 80.0 | | |
| Zwarte peper | 20.0 | | |
| **Totaal (inzet)** | **100.0** | **100.0%** | |

## Bereiding

1. Meng het zout en de peper.

## Iteratielog

### v1.0 - 2026-10-25

- Eerste versie.
"""
    path = tmp_path / "kruidenmix.md"
    formatted, diags = format_recipe(raw_recipe, path)
    assert diags == []
    assert "| Zout | 80.0 | 80.0% | |" in formatted
    assert "_Batch: % van de totale inzet, 100.0 g._" in formatted

    _, check_diags = parse_recipe(formatted, path)
    assert check_diags == []


def test_recipe_validation_errors(tmp_path: Path) -> None:
    bad_recipe = """---
kind: dish
status: testing
version: 1.0
domain: savory
basis:
  - Water
portions: 4
portion_g: 50
---

# Fout recept

## Formule

| Ingrediënt | Gewicht (g) | Schaling (%) | Batch (%) | Opmerking |
| :--- | ---: | ---: | ---: | :--- |
| **Water** | 100.0 | 100.0% | 100.0% | |
| **Totaal (inzet)** | **100.0** | **100.0%** | **100.0%** | |

_Schaling: % van Water, 100.0 g. Batch: % van de totale inzet, 100.0 g._

## Bereiding

1. Voeg 25 g zout toe.
3. Kook het water.

## Iteratielog

### v2.0 - 2026-10-25

- Versie klopt niet.
"""
    _, diags = parse_recipe(bad_recipe, tmp_path / "Bad_ID.md")
    messages = "\n".join(d.message for d in diags)
    assert "Invalid recipe file ID" in messages
    assert "'version' must be a quoted string" in messages
    assert "Omit 'portions' when 'portion_g' is set" in messages
    assert "contains weight '25 g'" in messages
    assert "numbered continuously" in messages
    assert "does not match newest iteration log entry" in messages


def test_equipment_validation_errors(tmp_path: Path) -> None:
    bad_eq = """---
kind: equipment
category: invalid_cat
limits:
  batch_g: [700, 300]
---

# Oven
"""
    _, diags = parse_equipment(bad_eq, tmp_path / "oven.md")
    messages = "\n".join(d.message for d in diags)
    assert "Invalid or missing 'category'" in messages
    assert "range minimum (700) exceeds maximum (300)" in messages
    assert "Missing intro paragraph" in messages


def test_vault_cross_references_and_cli_fmt(tmp_path: Path) -> None:
    vault = _make_vault(tmp_path / "vault")

    (vault / "00_context/equipment/kitchenaid-ijsmaker.md").write_text(
        """---
kind: equipment
category: cold
aliases:
  - IJsmachine
limits:
  batch_g: [350, 650]
---

# KitchenAid ijsmaker

Passieve vrieskom.
""",
        encoding="utf-8",
    )

    ing_raw = """---
kind: ingredient_family
category: sugar
---

# Suikers

Suikers.

## Kristalsuiker

```yaml
aliases:
  - Suiker
water_pct: 0.0
solids_pct: 100.0
carbs_pct: 100.0
sugars_pct: 100.0
sucrose_pct: 100.0
invert_sugar_pct: 0.0
pac: 100
pod: 100
source_type: datasheet
source: Referentie
```
"""
    (vault / "03_reference/ingredients/suikers.md").write_text(ing_raw, encoding="utf-8")

    rec_raw = """---
kind: dish
status: testing
version: "1.0"
domain: frozen
basis:
  - Suiker
equipment:
  - IJsmachine
---

# Suikersiroop

## Formule

| Ingrediënt | Gewicht (g) | Schaling (%) | Batch (%) | Opmerking |
| :--- | ---: | ---: | ---: | :--- |
| Suiker | 700,0 | | | |
| **Totaal (inzet)** | **0.0** | **0.0%** | **100.0%** | |

## Bereiding

1. Meng alles.

## Iteratielog

### v1.0 - 2026-10-25

- Start.
"""
    (vault / "01_rd_lab/suikersiroop.md").write_text(rec_raw, encoding="utf-8")

    res_check_before = runner.invoke(app, ["check", "--vault", str(vault)])
    assert res_check_before.exit_code == 1

    res_fmt_check = runner.invoke(app, ["fmt", "--check", "--vault", str(vault)])
    assert res_fmt_check.exit_code == 1
    assert "Would reformat" in res_fmt_check.output

    res_fmt = runner.invoke(app, ["fmt", "--vault", str(vault)])
    assert res_fmt.exit_code == 0
    assert "Formatted 2 file(s)" in res_fmt.output

    res_fmt_check_after = runner.invoke(app, ["fmt", "--check", "--vault", str(vault)])
    assert res_fmt_check_after.exit_code == 0

    res_check_after = runner.invoke(app, ["check", "--vault", str(vault)])
    assert res_check_after.exit_code == 0
    assert "WARN:" in res_check_after.output
    assert "exceeds max batch (650.0 g)" in res_check_after.output
    assert "Vault OK" in res_check_after.output

    diags = check_vault(vault)
    assert [d for d in diags if d.severity == "error"] == []
    assert len([d for d in diags if d.severity == "warning"]) == 1
