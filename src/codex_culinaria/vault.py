import difflib
from dataclasses import dataclass
from pathlib import Path

from codex_culinaria.common import VALID_DOMAINS, Diagnostic, is_valid_id, split_frontmatter
from codex_culinaria.equipment import Equipment, parse_equipment
from codex_culinaria.ingredients import (
    IngredientFamily,
    ResolvedIngredient,
    format_ingredient_family,
    parse_ingredient_family,
)
from codex_culinaria.recipes import Recipe, format_recipe, parse_recipe

REQUIRED_DIRS: tuple[str, ...] = (
    "00_context/equipment",
    "00_context/skills",
    "01_rd_lab",
    "02_library/components",
    "02_library/dishes",
    "03_reference/ingredients",
    "04_knowledge",
)

RECIPE_DIRS: tuple[str, ...] = (
    "01_rd_lab",
    "02_library/components",
    "02_library/dishes",
)


def missing_dirs(root: Path) -> list[str]:
    """Return the REQUIRED_DIRS entries that are not directories under ``root``."""
    return [d for d in REQUIRED_DIRS if not (root / d).is_dir()]


def _iter_md_files(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(p for p in directory.glob("*.md") if p.is_file())


@dataclass(frozen=True, slots=True)
class VaultIndex:
    equipment_by_name: dict[str, Equipment]
    equipment_aliases: dict[str, str]
    ingredients_by_name: dict[str, ResolvedIngredient]
    ingredient_aliases: dict[str, str]
    flour_names: frozenset[str]
    recipes_by_id: dict[str, Recipe]
    components_by_title: dict[str, Recipe]


def check_vault(root: Path) -> list[Diagnostic]:
    """Validate all equipment, ingredient families, recipes, and cross-references in ``root``."""
    diagnostics: list[Diagnostic] = []

    seen_ids: dict[str, Path] = {}
    scanned_dirs = (
        "00_context/equipment",
        "01_rd_lab",
        "02_library/components",
        "02_library/dishes",
        "03_reference/ingredients",
        "04_knowledge",
    )
    for rel_dir in scanned_dirs:
        for md_path in _iter_md_files(root / rel_dir):
            fid = md_path.stem
            if not is_valid_id(fid):
                diagnostics.append(
                    Diagnostic(
                        md_path,
                        f"Invalid file ID '{fid}': must be lowercase ASCII with hyphens.",
                    )
                )
            if fid in seen_ids:
                diagnostics.append(
                    Diagnostic(
                        md_path,
                        f"Duplicate file ID '{fid}' (also at {seen_ids[fid].relative_to(root)}).",
                    )
                )
            else:
                seen_ids[fid] = md_path

    for kn_path in _iter_md_files(root / "04_knowledge"):
        kn_text = kn_path.read_text(encoding="utf-8")
        kn_fm, _raw, kn_body, kn_diags = split_frontmatter(kn_text, kn_path)
        diagnostics.extend(kn_diags)
        if not kn_diags:
            if kn_fm.get("kind") != "knowledge":
                diagnostics.append(
                    Diagnostic(
                        kn_path,
                        f"Expected frontmatter 'kind: knowledge', got {kn_fm.get('kind')!r}.",
                    )
                )
            kn_domain = kn_fm.get("domain")
            if kn_domain is not None and (
                not isinstance(kn_domain, str) or kn_domain not in VALID_DOMAINS
            ):
                diagnostics.append(
                    Diagnostic(
                        kn_path,
                        f"Invalid 'domain' in knowledge note: {kn_domain!r}.",
                    )
                )
            if not kn_body.lstrip().startswith("# "):
                diagnostics.append(
                    Diagnostic(kn_path, "Knowledge note must start with a '# Title' H1 heading.")
                )

    equipment_by_name: dict[str, Equipment] = {}
    equipment_aliases: dict[str, str] = {}
    equipment_name_sources: dict[str, Path] = {}

    for eq_path in _iter_md_files(root / "00_context/equipment"):
        text = eq_path.read_text(encoding="utf-8")
        eq, eq_diags = parse_equipment(text, eq_path)
        diagnostics.extend(eq_diags)
        if eq is None:
            continue
        if eq.name in equipment_name_sources:
            diagnostics.append(
                Diagnostic(
                    eq_path,
                    f"Duplicate equipment name '{eq.name}' "
                    f"(also in {equipment_name_sources[eq.name].name}).",
                )
            )
        else:
            equipment_name_sources[eq.name] = eq_path
            equipment_by_name[eq.name] = eq

        for alias in eq.aliases:
            if alias in equipment_name_sources:
                diagnostics.append(
                    Diagnostic(
                        eq_path,
                        f"Equipment alias '{alias}' conflicts with existing name/alias in "
                        f"{equipment_name_sources[alias].name}.",
                    )
                )
            else:
                equipment_name_sources[alias] = eq_path
                equipment_aliases[alias] = eq.name

    families: list[IngredientFamily] = []
    ingredients_by_name: dict[str, ResolvedIngredient] = {}
    ingredient_aliases: dict[str, str] = {}
    ingredient_name_sources: dict[str, Path] = {}
    flour_names_set: set[str] = set()

    for ing_path in _iter_md_files(root / "03_reference/ingredients"):
        text = ing_path.read_text(encoding="utf-8")
        fam, fam_diags = parse_ingredient_family(text, ing_path)
        diagnostics.extend(fam_diags)
        if fam is None:
            continue
        families.append(fam)
        for res in fam.resolved:
            if res.role == "flour":
                flour_names_set.add(res.name)
            if res.name in ingredient_name_sources:
                diagnostics.append(
                    Diagnostic(
                        ing_path,
                        f"Duplicate ingredient name '{res.name}' "
                        f"(also in {ingredient_name_sources[res.name].name}).",
                    )
                )
            else:
                ingredient_name_sources[res.name] = ing_path
                ingredients_by_name[res.name] = res

            for alias in res.aliases:
                if alias in ingredient_name_sources:
                    diagnostics.append(
                        Diagnostic(
                            ing_path,
                            f"Ingredient alias '{alias}' conflicts with existing name/alias in "
                            f"{ingredient_name_sources[alias].name}.",
                        )
                    )
                else:
                    ingredient_name_sources[alias] = ing_path
                    ingredient_aliases[alias] = res.name
                    if res.role == "flour":
                        flour_names_set.add(alias)

    flour_names = frozenset(flour_names_set)
    recipes: list[Recipe] = []
    recipes_by_id: dict[str, Recipe] = {}
    components_by_title: dict[str, Recipe] = {}

    for rel_dir in RECIPE_DIRS:
        for rec_path in _iter_md_files(root / rel_dir):
            text = rec_path.read_text(encoding="utf-8")
            rec, rec_diags = parse_recipe(text, rec_path, flour_names=flour_names)
            diagnostics.extend(rec_diags)
            if rec is None:
                continue
            recipes.append(rec)
            recipes_by_id[rec.id] = rec

            if rel_dir == "02_library/components":
                if rec.kind != "component":
                    diagnostics.append(
                        Diagnostic(
                            rec_path,
                            f"Recipe in '02_library/components/' must have 'kind: component', "
                            f"got {rec.kind!r}.",
                        )
                    )
                if rec.status != "locked":
                    diagnostics.append(
                        Diagnostic(
                            rec_path,
                            f"Recipe in '02_library/components/' must have 'status: locked', "
                            f"got {rec.status!r}.",
                        )
                    )
            elif rel_dir == "02_library/dishes":
                if rec.kind != "dish":
                    diagnostics.append(
                        Diagnostic(
                            rec_path,
                            f"Recipe in '02_library/dishes/' must have 'kind: dish', "
                            f"got {rec.kind!r}.",
                        )
                    )
                if rec.status != "locked":
                    diagnostics.append(
                        Diagnostic(
                            rec_path,
                            f"Recipe in '02_library/dishes/' must have 'status: locked', "
                            f"got {rec.status!r}.",
                        )
                    )
            elif rel_dir == "01_rd_lab" and rec.status == "locked":
                diagnostics.append(
                    Diagnostic(
                        rec_path,
                        "Recipe in '01_rd_lab/' has 'status: locked'; promote it to '02_library/'.",
                    )
                )

            if rec.kind == "component":
                if rec.title in ingredient_name_sources:
                    diagnostics.append(
                        Diagnostic(
                            rec_path,
                            f"Component title '{rec.title}' conflicts with ingredient/component in "
                            f"{ingredient_name_sources[rec.title].name}.",
                        )
                    )
                else:
                    ingredient_name_sources[rec.title] = rec_path
                    components_by_title[rec.title] = rec
                for alias in rec.aliases:
                    if alias in ingredient_name_sources:
                        diagnostics.append(
                            Diagnostic(
                                rec_path,
                                f"Component alias '{alias}' conflicts with existing name/alias in "
                                f"{ingredient_name_sources[alias].name}.",
                            )
                        )
                    else:
                        ingredient_name_sources[alias] = rec_path
                        ingredient_aliases[alias] = rec.title

    all_known_ingredient_names = sorted(
        set(ingredients_by_name.keys())
        | set(components_by_title.keys())
        | set(ingredient_aliases.keys())
    )
    all_known_equipment_names = sorted(
        set(equipment_by_name.keys()) | set(equipment_aliases.keys())
    )

    for rec in recipes:
        if rec.variant_of is not None:
            parent_rec = recipes_by_id.get(rec.variant_of)
            if parent_rec is None:
                diagnostics.append(
                    Diagnostic(
                        rec.path,
                        f"'variant_of: {rec.variant_of}' references unknown recipe ID "
                        f"'{rec.variant_of}'.",
                    )
                )
            elif rec.id not in parent_rec.variants:
                diagnostics.append(
                    Diagnostic(
                        rec.path,
                        f"Recipe declares 'variant_of: {rec.variant_of}', but '{parent_rec.id}' "
                        f"does not list '{rec.id}' in 'variants'.",
                    )
                )

        for v_id in rec.variants:
            v_rec = recipes_by_id.get(v_id)
            if v_rec is None:
                diagnostics.append(
                    Diagnostic(
                        rec.path,
                        f"'variants' entry '{v_id}' references unknown recipe ID '{v_id}'.",
                    )
                )
            elif v_rec.variant_of != rec.id:
                diagnostics.append(
                    Diagnostic(
                        rec.path,
                        f"Recipe lists '{v_id}' in 'variants', but '{v_id}' does not declare "
                        f"'variant_of: {rec.id}'.",
                    )
                )

        if isinstance(rec.basis, tuple):
            for b_name in rec.basis:
                if b_name in ingredient_aliases:
                    canonical = ingredient_aliases[b_name]
                    diagnostics.append(
                        Diagnostic(
                            rec.path,
                            f"Basis ingredient '{b_name}' is an alias for '{canonical}'; "
                            f"run 'culinaria fmt'.",
                        )
                    )

        warned_ingredients: set[str] = set()
        for row in rec.rows:
            if row.is_intermediate:
                continue
            if row.name in ingredient_aliases:
                canonical = ingredient_aliases[row.name]
                diagnostics.append(
                    Diagnostic(
                        rec.path,
                        f"Ingredient '{row.name}' is an alias for '{canonical}'; "
                        f"run 'culinaria fmt'.",
                    )
                )
            elif row.name in ingredients_by_name:
                ing = ingredients_by_name[row.name]
                if ing.name not in warned_ingredients and (
                    ing.effective_source_type == "unverified" or ing.has_unverified_numeric
                ):
                    warned_ingredients.add(ing.name)
                    diagnostics.append(
                        Diagnostic(
                            rec.path,
                            f"Ingredient '{ing.name}' has unverified reference data "
                            f"({ing.bronstatus}).",
                            severity="warning",
                        )
                    )
            elif row.name not in components_by_title:
                suggestions = difflib.get_close_matches(
                    row.name, all_known_ingredient_names, n=3, cutoff=0.5
                )
                hint = f" Did you mean: {', '.join(suggestions)}?" if suggestions else ""
                diagnostics.append(
                    Diagnostic(
                        rec.path,
                        f"Unknown ingredient or component '{row.name}'.{hint}",
                    )
                )

        for eq_name in rec.equipment:
            if eq_name in equipment_aliases:
                canonical = equipment_aliases[eq_name]
                diagnostics.append(
                    Diagnostic(
                        rec.path,
                        f"Equipment '{eq_name}' is an alias for '{canonical}'; "
                        f"run 'culinaria fmt'.",
                    )
                )
                eq_obj = equipment_by_name.get(canonical)
            elif eq_name in equipment_by_name:
                eq_obj = equipment_by_name[eq_name]
            else:
                eq_obj = None
                suggestions = difflib.get_close_matches(
                    eq_name, all_known_equipment_names, n=3, cutoff=0.5
                )
                hint = f" Did you mean: {', '.join(suggestions)}?" if suggestions else ""
                diagnostics.append(
                    Diagnostic(
                        rec.path,
                        f"Unknown equipment '{eq_name}'.{hint}",
                    )
                )

            if (
                eq_obj is not None
                and eq_obj.max_batch_g is not None
                and rec.total_g > eq_obj.max_batch_g
            ):
                diagnostics.append(
                    Diagnostic(
                        rec.path,
                        f"Batch total ({rec.total_g:.1f} g) exceeds max batch "
                        f"({eq_obj.max_batch_g:.1f} g) of '{eq_obj.name}'.",
                        severity="warning",
                    )
                )

    return diagnostics


def format_vault(
    root: Path,
    *,
    check_only: bool = False,
) -> tuple[list[Path], list[Diagnostic]]:
    """Format all ingredient family and recipe files in ``root``.

    Returns ``(modified_paths, diagnostics)``. When ``check_only=True``, no files are written.
    """
    diagnostics: list[Diagnostic] = []
    modified: list[Path] = []

    equipment_aliases: dict[str, str] = {}
    for eq_path in _iter_md_files(root / "00_context/equipment"):
        eq, _ = parse_equipment(eq_path.read_text(encoding="utf-8"), eq_path)
        if eq is not None:
            for alias in eq.aliases:
                equipment_aliases[alias] = eq.name

    ingredient_aliases: dict[str, str] = {}
    flour_names_set: set[str] = set()

    for ing_path in _iter_md_files(root / "03_reference/ingredients"):
        orig_text = ing_path.read_text(encoding="utf-8")
        new_text, fmt_diags = format_ingredient_family(orig_text, ing_path)
        diagnostics.extend(fmt_diags)
        if not fmt_diags and new_text != orig_text:
            modified.append(ing_path)
            if not check_only:
                ing_path.write_text(new_text, encoding="utf-8")
        fam, _ = parse_ingredient_family(new_text, ing_path)
        if fam is not None:
            for res in fam.resolved:
                if res.role == "flour":
                    flour_names_set.add(res.name)
                for alias in res.aliases:
                    ingredient_aliases[alias] = res.name
                    if res.role == "flour":
                        flour_names_set.add(alias)

    for rel_dir in RECIPE_DIRS:
        for comp_path in _iter_md_files(root / rel_dir):
            rec, _ = parse_recipe(comp_path.read_text(encoding="utf-8"), comp_path)
            if rec is not None and rec.kind == "component":
                for alias in rec.aliases:
                    ingredient_aliases[alias] = rec.title

    flour_names = frozenset(flour_names_set)
    for rel_dir in RECIPE_DIRS:
        for rec_path in _iter_md_files(root / rel_dir):
            orig_text = rec_path.read_text(encoding="utf-8")
            new_text, fmt_diags = format_recipe(
                orig_text,
                rec_path,
                ingredient_aliases=ingredient_aliases,
                equipment_aliases=equipment_aliases,
                flour_names=flour_names,
            )
            diagnostics.extend(fmt_diags)
            if not fmt_diags and new_text != orig_text:
                modified.append(rec_path)
                if not check_only:
                    rec_path.write_text(new_text, encoding="utf-8")

    return modified, diagnostics
