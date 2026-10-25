import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from codex_culinaria.common import (
    Diagnostic,
    is_valid_id,
    parse_number_or_range,
    split_frontmatter,
)

VALID_INGREDIENT_CATEGORIES: frozenset[str] = frozenset(
    {
        "grain",
        "flour",
        "sugar",
        "dairy",
        "fat",
        "chocolate",
        "fruit",
        "hydrocolloid",
        "legume",
        "meat",
        "nut",
        "aromatic",
        "condiment",
        "alcohol",
    }
)

VALID_CALCULATORS: frozenset[str] = frozenset(
    {
        "ice_cream",
        "dough",
        "hydration",
        "safety",
    }
)

VALID_ROLES: frozenset[str] = frozenset({"flour", "grain", "inclusion"})
VALID_SOURCE_TYPES: frozenset[str] = frozenset({"datasheet", "database", "measured", "unverified"})
VALID_GLUTEN: frozenset[str] = frozenset({"strong", "medium", "weak", "none"})

SCALAR_NUMERIC_KEYS: frozenset[str] = frozenset(
    {
        "water_pct",
        "solids_pct",
        "carbs_pct",
        "sugars_pct",
        "sucrose_pct",
        "invert_sugar_pct",
        "lactose_pct",
        "protein_pct",
        "fat_pct",
        "saturated_fat_pct",
        "cocoa_butter_pct",
        "milk_fat_pct",
        "non_fat_cocoa_solids_pct",
        "msnf_pct",
        "fiber_pct",
        "salt_pct",
        "ash_pct",
        "pac",
        "pod",
        "de",
        "brix",
        "acidity_pct",
        "hydration_ratio",
        "amylose_pct",
        "absorption_pct",
    }
)

RANGE_NUMERIC_KEYS: frozenset[str] = frozenset({"steaming_min"})
NUMERIC_PROPERTY_KEYS: frozenset[str] = SCALAR_NUMERIC_KEYS | RANGE_NUMERIC_KEYS
INHERITED_PROPERTY_KEYS: frozenset[str] = NUMERIC_PROPERTY_KEYS | {"role", "gluten"}
META_KEYS: frozenset[str] = frozenset({"aliases", "brand", "source_type", "source", "unverified"})
ALLOWED_YAML_BLOCK_KEYS: frozenset[str] = INHERITED_PROPERTY_KEYS | META_KEYS

OVERVIEW_START = "<!-- culinaria:overview (generated - edits here are overwritten) -->"
OVERVIEW_END = "<!-- /culinaria:overview -->"

PropertyValue = float | tuple[float, float] | str


@dataclass(frozen=True, slots=True)
class ColumnSpec:
    key: str
    header: str
    align: str
    decimals: int | None = 1


COLUMN_SPECS: dict[str, ColumnSpec] = {
    "role": ColumnSpec("role", "Rol", ":---", None),
    "water_pct": ColumnSpec("water_pct", "Water (%)", "---:", 1),
    "solids_pct": ColumnSpec("solids_pct", "Droge stof (%)", "---:", 1),
    "carbs_pct": ColumnSpec("carbs_pct", "Koolhydraten (%)", "---:", 1),
    "sugars_pct": ColumnSpec("sugars_pct", "Suikers (%)", "---:", 1),
    "sucrose_pct": ColumnSpec("sucrose_pct", "Sacharose (%)", "---:", 1),
    "invert_sugar_pct": ColumnSpec("invert_sugar_pct", "Invertsuiker (%)", "---:", 1),
    "lactose_pct": ColumnSpec("lactose_pct", "Lactose (%)", "---:", 1),
    "protein_pct": ColumnSpec("protein_pct", "Eiwit (%)", "---:", 1),
    "fat_pct": ColumnSpec("fat_pct", "Vet (%)", "---:", 1),
    "saturated_fat_pct": ColumnSpec("saturated_fat_pct", "Verzadigd vet (%)", "---:", 1),
    "cocoa_butter_pct": ColumnSpec("cocoa_butter_pct", "Cacaoboter (%)", "---:", 1),
    "milk_fat_pct": ColumnSpec("milk_fat_pct", "Melkvet (%)", "---:", 1),
    "non_fat_cocoa_solids_pct": ColumnSpec(
        "non_fat_cocoa_solids_pct", "Vetvrije cacao (%)", "---:", 1
    ),
    "msnf_pct": ColumnSpec("msnf_pct", "MSNF (%)", "---:", 1),
    "fiber_pct": ColumnSpec("fiber_pct", "Vezels (%)", "---:", 1),
    "salt_pct": ColumnSpec("salt_pct", "Zout (%)", "---:", 2),
    "ash_pct": ColumnSpec("ash_pct", "Asgehalte (%)", "---:", 2),
    "pac": ColumnSpec("pac", "PAC", "---:", 0),
    "pod": ColumnSpec("pod", "POD", "---:", 0),
    "de": ColumnSpec("de", "DE", "---:", 0),
    "brix": ColumnSpec("brix", "Brix (°)", "---:", 1),
    "acidity_pct": ColumnSpec("acidity_pct", "Zuur (%)", "---:", 1),
    "amylose_pct": ColumnSpec("amylose_pct", "Amylose (%)", "---:", 1),
    "hydration_ratio": ColumnSpec("hydration_ratio", "Hydratatie", "---:", 2),
    "steaming_min": ColumnSpec("steaming_min", "Stoomtijd (min)", "---:", 0),
    "absorption_pct": ColumnSpec("absorption_pct", "Absorptie (%)", "---:", 1),
    "gluten": ColumnSpec("gluten", "Gluten", ":---", None),
}

CATEGORY_OVERVIEW_COLUMNS: dict[str, tuple[str, ...]] = {
    "grain": (
        "solids_pct",
        "carbs_pct",
        "protein_pct",
        "fat_pct",
        "amylose_pct",
        "hydration_ratio",
        "steaming_min",
    ),
    "flour": (
        "role",
        "solids_pct",
        "carbs_pct",
        "protein_pct",
        "fat_pct",
        "fiber_pct",
        "ash_pct",
        "gluten",
    ),
    "sugar": (
        "solids_pct",
        "carbs_pct",
        "sugars_pct",
        "sucrose_pct",
        "invert_sugar_pct",
        "pac",
        "pod",
        "de",
    ),
    "dairy": (
        "water_pct",
        "solids_pct",
        "fat_pct",
        "msnf_pct",
        "lactose_pct",
        "protein_pct",
    ),
    "chocolate": (
        "solids_pct",
        "fat_pct",
        "cocoa_butter_pct",
        "sugars_pct",
        "sucrose_pct",
        "msnf_pct",
        "protein_pct",
    ),
    "fruit": (
        "role",
        "water_pct",
        "solids_pct",
        "carbs_pct",
        "sugars_pct",
        "sucrose_pct",
        "brix",
    ),
    "fat": ("water_pct", "solids_pct", "fat_pct", "saturated_fat_pct", "protein_pct"),
    "hydrocolloid": ("solids_pct", "carbs_pct", "fiber_pct", "protein_pct"),
    "legume": ("water_pct", "solids_pct", "carbs_pct", "protein_pct", "fiber_pct", "fat_pct"),
    "meat": ("water_pct", "solids_pct", "protein_pct", "fat_pct", "saturated_fat_pct", "salt_pct"),
    "nut": ("role", "solids_pct", "fat_pct", "saturated_fat_pct", "protein_pct", "carbs_pct"),
    "aromatic": ("water_pct", "solids_pct", "carbs_pct", "sugars_pct", "protein_pct", "fat_pct"),
    "condiment": ("water_pct", "solids_pct", "carbs_pct", "sugars_pct", "acidity_pct", "salt_pct"),
    "alcohol": ("water_pct", "solids_pct", "sugars_pct"),
}


@dataclass(frozen=True, slots=True)
class PropertyProvenance:
    source_type: str
    source: str
    is_unverified: bool


@dataclass(frozen=True, slots=True)
class IngredientEntry:
    name: str
    level: int  # 2 for ## functional ingredient, 3 for ### variant
    parent_name: str | None
    aliases: tuple[str, ...]
    brand: str | None
    source_type: str | None
    source: str | None
    unverified: frozenset[str]
    properties: dict[str, PropertyValue] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ResolvedIngredient:
    name: str
    family_id: str
    family_path: Path
    category: str
    level: int
    parent_name: str | None
    aliases: tuple[str, ...]
    brand: str | None
    own_source_type: str | None
    effective_source_type: str
    properties: dict[str, PropertyValue]
    provenance: dict[str, PropertyProvenance]

    @property
    def role(self) -> str | None:
        val = self.properties.get("role")
        return val if isinstance(val, str) else None

    @property
    def has_unverified_numeric(self) -> bool:
        return any(
            prov.is_unverified
            for key, prov in self.provenance.items()
            if key in NUMERIC_PROPERTY_KEYS
        )

    @property
    def bronstatus(self) -> str:
        if self.own_source_type == "unverified" or self.effective_source_type == "unverified":
            return "unverified*"
        if self.has_unverified_numeric:
            return f"{self.effective_source_type} + unverified*"
        return self.effective_source_type


@dataclass(frozen=True, slots=True)
class IngredientFamily:
    id: str
    path: Path
    title: str
    category: str
    calculators: tuple[str, ...]
    entries: tuple[IngredientEntry, ...]
    resolved: tuple[ResolvedIngredient, ...]


_HEADING_RE = re.compile(r"^(#{1,6}) (.+)$", re.MULTILINE)
_YAML_BLOCK_RE = re.compile(r"^\s*```yaml\n(.*?)\n```\s*(?:\n|$)", re.DOTALL)
_OVERVIEW_BLOCK_RE = re.compile(
    r"<!-- culinaria:overview(?:\s*\([^)]*\))?\s*-->\n?(.*?)\n?<!-- /culinaria:overview -->",
    re.DOTALL,
)


def _parse_entry_yaml(
    raw_yaml: str,
    entry_name: str,
    level: int,
    parent_name: str | None,
    path: Path,
) -> tuple[IngredientEntry | None, list[Diagnostic]]:
    diagnostics: list[Diagnostic] = []
    try:
        loaded = yaml.safe_load(raw_yaml)
    except yaml.YAMLError as exc:
        diagnostics.append(Diagnostic(path, f"Invalid YAML block in section '{entry_name}': {exc}"))
        return None, diagnostics

    if not isinstance(loaded, dict):
        diagnostics.append(
            Diagnostic(path, f"YAML block in section '{entry_name}' must be a mapping.")
        )
        return None, diagnostics

    unknown = set(loaded.keys()) - ALLOWED_YAML_BLOCK_KEYS
    for k in sorted(unknown):
        diagnostics.append(
            Diagnostic(path, f"Unknown property key '{k}' in section '{entry_name}'.")
        )

    aliases: list[str] = []
    raw_aliases = loaded.get("aliases")
    if raw_aliases is not None:
        if not isinstance(raw_aliases, list) or not all(
            isinstance(a, str) and a.strip() for a in raw_aliases
        ):
            diagnostics.append(
                Diagnostic(path, f"'aliases' in '{entry_name}' must be a list of strings.")
            )
        else:
            aliases = [a.strip() for a in raw_aliases]

    brand = loaded.get("brand")
    if brand is not None and (not isinstance(brand, str) or not brand.strip()):
        diagnostics.append(
            Diagnostic(path, f"'brand' in '{entry_name}' must be a non-empty string.")
        )
        brand = None

    source_type = loaded.get("source_type")
    if source_type is not None and (
        not isinstance(source_type, str) or source_type not in VALID_SOURCE_TYPES
    ):
        diagnostics.append(
            Diagnostic(
                path,
                f"Invalid 'source_type' in '{entry_name}': expected one of "
                f"{sorted(VALID_SOURCE_TYPES)}, got {source_type!r}.",
            )
        )
        source_type = None

    source = loaded.get("source")
    if source is not None and (not isinstance(source, str) or not source.strip()):
        diagnostics.append(
            Diagnostic(path, f"'source' in '{entry_name}' must be a non-empty string.")
        )
        source = None

    unverified_set: set[str] = set()
    raw_unverified = loaded.get("unverified")
    if raw_unverified is not None:
        if not isinstance(raw_unverified, list) or not all(
            isinstance(u, str) for u in raw_unverified
        ):
            diagnostics.append(
                Diagnostic(path, f"'unverified' in '{entry_name}' must be a list of property keys.")
            )
        else:
            for u in raw_unverified:
                if u not in INHERITED_PROPERTY_KEYS:
                    diagnostics.append(
                        Diagnostic(
                            path,
                            f"Unknown property key '{u}' in 'unverified' of '{entry_name}'.",
                        )
                    )
                elif u not in loaded:
                    diagnostics.append(
                        Diagnostic(
                            path,
                            f"Key '{u}' in 'unverified' of '{entry_name}' is not defined in "
                            f"that section's YAML block.",
                        )
                    )
                else:
                    unverified_set.add(u)
            if source_type == "unverified":
                diagnostics.append(
                    Diagnostic(
                        path,
                        f"'unverified' list is redundant in '{entry_name}' when "
                        f"source_type is 'unverified'.",
                    )
                )

    properties: dict[str, PropertyValue] = {}
    for key in INHERITED_PROPERTY_KEYS:
        if key not in loaded:
            continue
        val = loaded[key]
        if key == "role":
            if not isinstance(val, str) or val not in VALID_ROLES:
                diagnostics.append(
                    Diagnostic(
                        path,
                        f"Invalid 'role' in '{entry_name}': expected one of "
                        f"{sorted(VALID_ROLES)}, got {val!r}.",
                    )
                )
            else:
                properties[key] = val
        elif key == "gluten":
            if not isinstance(val, str) or val not in VALID_GLUTEN:
                diagnostics.append(
                    Diagnostic(
                        path,
                        f"Invalid 'gluten' in '{entry_name}': expected one of "
                        f"{sorted(VALID_GLUTEN)}, got {val!r}.",
                    )
                )
            else:
                properties[key] = val
        else:
            parsed_num, num_diags = parse_number_or_range(
                val,
                f"{entry_name}.{key}",
                path,
                allow_range=key in RANGE_NUMERIC_KEYS,
            )
            diagnostics.extend(num_diags)
            if parsed_num is not None:
                properties[key] = parsed_num

    has_numeric_or_func = bool(set(properties.keys()) & NUMERIC_PROPERTY_KEYS) or level == 2
    if has_numeric_or_func and properties:
        if source_type is None:
            diagnostics.append(
                Diagnostic(path, f"Section '{entry_name}' is missing 'source_type'.")
            )
        if source is None:
            diagnostics.append(Diagnostic(path, f"Section '{entry_name}' is missing 'source'."))
    elif (source_type is None) != (source is None):
        diagnostics.append(
            Diagnostic(
                path,
                f"Section '{entry_name}' must specify both 'source_type' and 'source' together.",
            )
        )

    entry = IngredientEntry(
        name=entry_name,
        level=level,
        parent_name=parent_name,
        aliases=tuple(aliases),
        brand=brand,
        source_type=source_type,
        source=source,
        unverified=frozenset(unverified_set),
        properties=properties,
    )
    return entry, diagnostics


def _resolve_entries(
    entries: list[IngredientEntry],
    family_id: str,
    family_path: Path,
    category: str,
) -> tuple[list[ResolvedIngredient], list[Diagnostic]]:
    diagnostics: list[Diagnostic] = []
    resolved_list: list[ResolvedIngredient] = []
    parents_by_name: dict[str, ResolvedIngredient] = {}

    for entry in entries:
        if entry.level == 2:
            st = entry.source_type or "unverified"
            src = entry.source or ""
            prov: dict[str, PropertyProvenance] = {}
            for k in entry.properties:
                prov[k] = PropertyProvenance(
                    source_type=st,
                    source=src,
                    is_unverified=(st == "unverified" or k in entry.unverified),
                )
            res = ResolvedIngredient(
                name=entry.name,
                family_id=family_id,
                family_path=family_path,
                category=category,
                level=2,
                parent_name=None,
                aliases=entry.aliases,
                brand=entry.brand,
                own_source_type=entry.source_type,
                effective_source_type=st,
                properties=dict(entry.properties),
                provenance=prov,
            )
            parents_by_name[entry.name] = res
            resolved_list.append(res)
        else:
            assert entry.parent_name is not None
            parent = parents_by_name.get(entry.parent_name)
            if parent is None:
                continue
            merged_props = dict(parent.properties)
            merged_prov = dict(parent.provenance)
            eff_st = entry.source_type or parent.effective_source_type
            eff_src = entry.source or ""
            for k, v in entry.properties.items():
                merged_props[k] = v
                merged_prov[k] = PropertyProvenance(
                    source_type=eff_st,
                    source=eff_src,
                    is_unverified=(eff_st == "unverified" or k in entry.unverified),
                )
            res = ResolvedIngredient(
                name=entry.name,
                family_id=family_id,
                family_path=family_path,
                category=category,
                level=3,
                parent_name=entry.parent_name,
                aliases=entry.aliases,
                brand=entry.brand,
                own_source_type=entry.source_type,
                effective_source_type=eff_st,
                properties=merged_props,
                provenance=merged_prov,
            )
            resolved_list.append(res)

        water = res.properties.get("water_pct")
        solids = res.properties.get("solids_pct")
        if (
            isinstance(water, float)
            and isinstance(solids, float)
            and abs((water + solids) - 100.0) > 0.15
        ):
            diagnostics.append(
                Diagnostic(
                    family_path,
                    f"In '{res.name}', water_pct ({water}) + solids_pct ({solids}) != 100.0.",
                )
            )

    return resolved_list, diagnostics


def format_overview_cell(
    item: ResolvedIngredient,
    spec: ColumnSpec,
) -> str:
    val = item.properties.get(spec.key)
    if val is None:
        return "-"
    if isinstance(val, str):
        return val
    if isinstance(val, tuple):
        low, high = val
        if spec.decimals == 0:
            formatted = f"{round(low)}-{round(high)}"
        else:
            d = spec.decimals or 1
            formatted = f"{low:.{d}f}-{high:.{d}f}"
    else:
        if spec.decimals == 0:
            formatted = f"{round(val)}" if float(val).is_integer() else f"{val:.1f}"
        else:
            d = spec.decimals or 1
            formatted = f"{val:.{d}f}"

    prov = item.provenance.get(spec.key)
    if prov is not None and prov.is_unverified and spec.key in NUMERIC_PROPERTY_KEYS:
        return f"{formatted}*"
    return formatted


def generate_overview_table(family: IngredientFamily) -> str:
    col_keys = CATEGORY_OVERVIEW_COLUMNS.get(family.category, ("water_pct", "solids_pct"))
    specs = [COLUMN_SPECS[k] for k in col_keys]

    headers = ["Ingrediënt", *[s.header for s in specs], "Bronstatus"]
    aligns = [":---", *[s.align for s in specs], ":---"]

    lines = [
        OVERVIEW_START,
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(aligns) + " |",
    ]
    for item in family.resolved:
        name_cell = f"**{item.name}**" if item.level == 2 else f"↳ {item.name}"
        cells = [name_cell, *[format_overview_cell(item, s) for s in specs], item.bronstatus]
        lines.append("| " + " | ".join(cells) + " |")
    lines.append(OVERVIEW_END)
    return "\n".join(lines)


def parse_ingredient_family(
    text: str, path: Path
) -> tuple[IngredientFamily | None, list[Diagnostic]]:
    diagnostics: list[Diagnostic] = []
    file_id = path.stem
    if not is_valid_id(file_id):
        diagnostics.append(
            Diagnostic(
                path,
                f"Invalid ingredient family file ID '{file_id}': "
                f"must be lowercase ASCII with hyphens.",
            )
        )

    fm, _raw_fm, body, fm_diags = split_frontmatter(text, path)
    diagnostics.extend(fm_diags)
    if fm_diags:
        return None, diagnostics

    allowed_fm = {"kind", "category", "calculators"}
    for key in sorted(set(fm.keys()) - allowed_fm):
        diagnostics.append(Diagnostic(path, f"Unknown frontmatter key '{key}'."))

    if fm.get("kind") != "ingredient_family":
        diagnostics.append(
            Diagnostic(
                path, f"Expected frontmatter 'kind: ingredient_family', got {fm.get('kind')!r}."
            )
        )

    category = fm.get("category")
    if not isinstance(category, str) or category not in VALID_INGREDIENT_CATEGORIES:
        diagnostics.append(
            Diagnostic(
                path,
                f"Invalid or missing 'category': expected one of "
                f"{sorted(VALID_INGREDIENT_CATEGORIES)}, got {category!r}.",
            )
        )
        category_str = ""
    else:
        category_str = category

    calculators: list[str] = []
    raw_calcs = fm.get("calculators")
    if raw_calcs is not None:
        if not isinstance(raw_calcs, list) or not all(isinstance(c, str) for c in raw_calcs):
            diagnostics.append(Diagnostic(path, "'calculators' must be a list of strings."))
        else:
            for c in raw_calcs:
                if c not in VALID_CALCULATORS:
                    diagnostics.append(
                        Diagnostic(
                            path,
                            f"Unknown calculator '{c}'; expected one of "
                            f"{sorted(VALID_CALCULATORS)}.",
                        )
                    )
                else:
                    calculators.append(c)

    headings = list(_HEADING_RE.finditer(body))
    if not headings or len(headings[0].group(1)) != 1:
        diagnostics.append(Diagnostic(path, "Missing '# Family' H1 heading at start of body."))
        return None, diagnostics

    title = headings[0].group(2).strip()
    entries: list[IngredientEntry] = []
    current_h2: str | None = None

    for idx, match in enumerate(headings[1:], start=1):
        hashes = match.group(1)
        level = len(hashes)
        sec_name = match.group(2).strip()
        sec_start = match.end()
        sec_end = headings[idx + 1].start() if idx + 1 < len(headings) else len(body)
        sec_body = body[sec_start:sec_end]

        if level == 1:
            diagnostics.append(Diagnostic(path, f"Unexpected second H1 heading '# {sec_name}'."))
            continue
        if level > 3:
            diagnostics.append(
                Diagnostic(
                    path,
                    f"Unexpected heading level '{hashes} {sec_name}'; only ## and ### are allowed.",
                )
            )
            continue
        if level == 3 and current_h2 is None:
            diagnostics.append(
                Diagnostic(
                    path,
                    f"Variant '### {sec_name}' appears before any '## ' functional ingredient.",
                )
            )
            continue
        if level == 2:
            current_h2 = sec_name

        yaml_match = _YAML_BLOCK_RE.match(sec_body)
        if yaml_match is None:
            diagnostics.append(
                Diagnostic(
                    path,
                    f"Section '{hashes} {sec_name}' must start with a fenced ```yaml block.",
                )
            )
            continue

        entry, entry_diags = _parse_entry_yaml(
            yaml_match.group(1),
            sec_name,
            level=level,
            parent_name=None if level == 2 else current_h2,
            path=path,
        )
        diagnostics.extend(entry_diags)
        if entry is not None:
            entries.append(entry)

    if not entries:
        diagnostics.append(
            Diagnostic(path, "Ingredient family file must contain at least one '## ' ingredient.")
        )

    resolved, res_diags = _resolve_entries(entries, file_id, path, category_str)
    diagnostics.extend(res_diags)

    family = IngredientFamily(
        id=file_id,
        path=path,
        title=title,
        category=category_str,
        calculators=tuple(calculators),
        entries=tuple(entries),
        resolved=tuple(resolved),
    )

    if not diagnostics:
        expected_overview = generate_overview_table(family)
        ov_match = _OVERVIEW_BLOCK_RE.search(body)
        if ov_match is None:
            diagnostics.append(
                Diagnostic(
                    path,
                    "Missing generated '<!-- culinaria:overview -->' block; run 'culinaria fmt'.",
                )
            )
        elif ov_match.group(0) != expected_overview:
            diagnostics.append(
                Diagnostic(
                    path,
                    "Overview table is out of date with ingredient YAML blocks; "
                    "run 'culinaria fmt'.",
                )
            )

    return family, diagnostics


def format_ingredient_family(text: str, path: Path) -> tuple[str, list[Diagnostic]]:
    """Format an ingredient family file by regenerating its overview table."""
    family, diagnostics = parse_ingredient_family(text, path)
    hard_errors = [
        d
        for d in diagnostics
        if "culinaria:overview" not in d.message
        and "Overview table is out of date" not in d.message
    ]
    if family is None or hard_errors:
        return text, hard_errors

    overview_block = generate_overview_table(family)
    if _OVERVIEW_BLOCK_RE.search(text):
        formatted = _OVERVIEW_BLOCK_RE.sub(overview_block, text, count=1)
        return formatted, []

    _fm, raw_fm, body, _ = split_frontmatter(text, path)
    headings = list(_HEADING_RE.finditer(body))
    if len(headings) >= 2:
        h2_start = headings[1].start()
        intro_part = body[:h2_start].rstrip()
        rest_part = body[h2_start:]
        new_body = f"{intro_part}\n\n{overview_block}\n\n{rest_part}"
    else:
        new_body = f"{body.rstrip()}\n\n{overview_block}\n"
    return raw_fm + new_body, []
