import datetime
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from codex_culinaria.common import (
    VALID_DOMAINS,
    Diagnostic,
    format_percentage,
    is_valid_id,
    parse_number_or_range,
    split_frontmatter,
)

RecipeKind = Literal["dish", "component"]
RecipeStatus = Literal["concept", "testing", "locked"]

VALID_RECIPE_KINDS: frozenset[str] = frozenset({"dish", "component"})
VALID_RECIPE_STATUSES: frozenset[str] = frozenset({"concept", "testing", "locked"})

ALLOWED_RECIPE_FRONTMATTER_KEYS: frozenset[str] = frozenset(
    {
        "kind",
        "status",
        "version",
        "domain",
        "basis",
        "cuisine",
        "techniques",
        "equipment",
        "portions",
        "portion_g",
        "yield_g",
        "variant_of",
        "variants",
        "time",
        "storage",
        "targets",
        "aliases",
        "source",
        "created",
    }
)

FORMULA_HEADERS: frozenset[str] = frozenset({"Formule", "Formula"})
METHOD_HEADERS: frozenset[str] = frozenset({"Bereiding", "Method"})
NOTES_HEADERS: frozenset[str] = frozenset({"Notities", "Notes"})
ITERATION_LOG_HEADERS: frozenset[str] = frozenset({"Iteratielog", "Iteration log"})

PHASE_START = "<!-- culinaria:phase (generated - edits here are overwritten) -->"
PHASE_END = "<!-- /culinaria:phase -->"

_H1_RE = re.compile(r"^# (.+)$", re.MULTILINE)
_H2_RE = re.compile(r"^## (.+)$", re.MULTILINE)
_H3_RE = re.compile(r"^### (.+)$", re.MULTILINE)
_PHASE_BLOCK_RE = re.compile(
    r"<!-- culinaria:phase(?:\s*\([^)]*\))?\s*-->\n?(.*?)\n?<!-- /culinaria:phase -->",
    re.DOTALL,
)
_BOLD_RE = re.compile(r"^\*\*(.+)\*\*$")
_STEP_LINE_RE = re.compile(r"^(\d+)\.\s+(.+)$")
_WEIGHT_IN_STEP_RE = re.compile(r"\b(\d+(?:[.,]\d+)?)\s*(?:g|gram)\b")
_ITERATION_HEADER_RE = re.compile(r"^v([0-9]+(?:\.[0-9]+)*)\s+-\s+(\d{4}-\d{2}-\d{2})$")
_THOUSANDS_SEP_RE = re.compile(r"\b\d{1,3}\.\d{3}\b")


@dataclass(frozen=True, slots=True)
class FormulaRow:
    name: str
    weight_g: float | None  # None when q.s.
    weight_str: str  # Normalized display weight (e.g. "390.0" or "q.s.")
    note: str
    group: str | None
    is_intermediate: bool
    is_qs: bool


@dataclass(frozen=True, slots=True)
class RecipePhase:
    name: str
    has_phase_block: bool
    phase_block_text: str | None
    step_numbers: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class Recipe:
    id: str
    path: Path
    title: str
    kind: str
    status: str
    version: str
    domain: str
    basis: str | tuple[str, ...]  # "flour", "total", or tuple of ingredient names
    cuisine: tuple[str, ...] = ()
    techniques: tuple[str, ...] = ()
    equipment: tuple[str, ...] = ()
    portions: float | tuple[float, float] | None = None
    portion_g: float | None = None
    yield_g: float | None = None
    variant_of: str | None = None
    variants: tuple[str, ...] = ()
    time: str | None = None
    storage: str | None = None
    targets: dict[str, float | tuple[float, float]] = field(default_factory=dict)
    aliases: tuple[str, ...] = ()
    source: str | None = None
    created: str | None = None
    groups: tuple[str, ...] = ()
    rows: tuple[FormulaRow, ...] = ()
    phases: tuple[RecipePhase, ...] = ()

    @property
    def total_g(self) -> float:
        return sum(
            r.weight_g
            for r in self.rows
            if r.weight_g is not None and not r.is_intermediate and not r.is_qs
        )


def _strip_bold(cell: str) -> tuple[str, bool]:
    m = _BOLD_RE.match(cell.strip())
    if m:
        return m.group(1).strip(), True
    return cell.strip(), False


def _parse_table_row(line: str) -> list[str] | None:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    inner = stripped[1:-1]
    return [c.strip() for c in inner.split("|")]


def _is_alignment_row(cells: list[str]) -> bool:
    return bool(cells) and all(bool(re.match(r"^:?-+:?$", c)) for c in cells if c != "")


def _normalize_weight(raw: str, path: Path) -> tuple[float | None, str, bool, list[Diagnostic]]:
    """Return (weight_g, normalized_str, is_qs, diagnostics)."""
    diagnostics: list[Diagnostic] = []
    s = raw.strip()
    if s == "q.s.":
        return None, "q.s.", True, diagnostics

    has_comma = "," in s
    if has_comma:
        diagnostics.append(
            Diagnostic(
                path,
                f"Weight '{s}' uses a decimal comma; use a decimal point (or run 'culinaria fmt').",
            )
        )
    normalized = s.replace(",", ".")
    if _THOUSANDS_SEP_RE.match(normalized) and len(normalized.split(".")[1]) == 3:
        diagnostics.append(
            Diagnostic(
                path,
                f"Weight '{s}' looks like it contains a thousands separator; write plain numbers.",
            )
        )
    try:
        val = float(normalized)
    except ValueError:
        diagnostics.append(
            Diagnostic(path, f"Invalid weight '{s}': expected a number in grams or 'q.s.'.")
        )
        return None, s, False, diagnostics

    if val <= 0:
        diagnostics.append(Diagnostic(path, f"Weight must be positive, got '{s}'."))
    if "." not in normalized:
        normalized = f"{val:.1f}"
    return val, normalized, False, diagnostics


def _resolve_basis_lines(
    basis: str | tuple[str, ...],
    rows: tuple[FormulaRow, ...],
    flour_names: frozenset[str],
    path: Path,
) -> tuple[frozenset[str], str, float, list[Diagnostic]]:
    """Return (basis_ingredient_names, basis_caption_label, basis_total_g, diagnostics)."""
    diagnostics: list[Diagnostic] = []
    weighed_rows = [
        r for r in rows if r.weight_g is not None and not r.is_intermediate and not r.is_qs
    ]
    total_g = sum(r.weight_g for r in weighed_rows if r.weight_g is not None)

    if basis == "total":
        return frozenset(), "de totale inzet", total_g, diagnostics

    if basis == "flour":
        matched_names: list[str] = []
        for r in weighed_rows:
            if r.name in flour_names and r.name not in matched_names:
                matched_names.append(r.name)
        if not matched_names:
            diagnostics.append(
                Diagnostic(
                    path,
                    "Recipe declares 'basis: flour', "
                    "but no formula ingredients have 'role: flour'.",
                )
            )
            return frozenset(), "bloem", 0.0, diagnostics
        basis_set = frozenset(matched_names)
        basis_g = sum(
            r.weight_g for r in weighed_rows if r.name in basis_set and r.weight_g is not None
        )
        return basis_set, " + ".join(matched_names), basis_g, diagnostics

    assert isinstance(basis, tuple)
    for b_name in basis:
        if not any(r.name == b_name for r in weighed_rows):
            diagnostics.append(
                Diagnostic(
                    path,
                    f"Basis ingredient '{b_name}' was not found as a weighed row in '## Formule'.",
                )
            )
    basis_set = frozenset(basis)
    basis_g = sum(
        r.weight_g for r in weighed_rows if r.name in basis_set and r.weight_g is not None
    )
    return basis_set, " + ".join(basis), basis_g, diagnostics


def generate_formula_section(
    rows: tuple[FormulaRow, ...],
    basis: str | tuple[str, ...],
    flour_names: frozenset[str],
    path: Path,
) -> tuple[str, list[Diagnostic]]:
    """Generate the canonical Markdown table and caption for ``## Formule``."""
    basis_set, basis_label, basis_g, diags = _resolve_basis_lines(basis, rows, flour_names, path)
    total_g = sum(
        r.weight_g for r in rows if r.weight_g is not None and not r.is_intermediate and not r.is_qs
    )
    is_total_basis = basis == "total"

    if is_total_basis:
        lines = [
            "| Ingrediënt | Gewicht (g) | Batch (%) | Opmerking |",
            "| :--- | ---: | ---: | :--- |",
        ]
    else:
        lines = [
            "| Ingrediënt | Gewicht (g) | Schaling (%) | Batch (%) | Opmerking |",
            "| :--- | ---: | ---: | ---: | :--- |",
        ]

    current_group: str | None = None
    for r in rows:
        if r.group is not None and r.group != current_group:
            current_group = r.group
            if is_total_basis:
                lines.append(f"| **{current_group}** | | | |")
            else:
                lines.append(f"| **{current_group}** | | | | |")

        name_cell = f"**{r.name}**" if (r.name in basis_set and not r.is_intermediate) else r.name
        note_cell = f" {r.note} " if r.note else " "

        if r.is_qs or r.weight_g is None:
            if is_total_basis:
                lines.append(f"| {name_cell} | q.s. | |{note_cell}|")
            else:
                lines.append(f"| {name_cell} | q.s. | | |{note_cell}|")
        else:
            batch_pct_str = format_percentage((r.weight_g / total_g) * 100.0) if total_g > 0 else ""
            if is_total_basis:
                lines.append(f"| {name_cell} | {r.weight_str} | {batch_pct_str} |{note_cell}|")
            else:
                scale_pct_str = (
                    format_percentage((r.weight_g / basis_g) * 100.0) if basis_g > 0 else ""
                )
                lines.append(
                    f"| {name_cell} | {r.weight_str} | {scale_pct_str} | "
                    f"{batch_pct_str} |{note_cell}|"
                )

    if is_total_basis:
        lines.append(f"| **Totaal (inzet)** | **{total_g:.1f}** | **100.0%** | |")
        caption = f"_Batch: % van de totale inzet, {total_g:.1f} g._"
    else:
        total_scale_str = (
            f"**{format_percentage((total_g / basis_g) * 100.0)}**" if basis_g > 0 else ""
        )
        lines.append(
            f"| **Totaal (inzet)** | **{total_g:.1f}** | {total_scale_str} | **100.0%** | |"
        )
        caption = (
            f"_Schaling: % van {basis_label}, {basis_g:.1f} g. "
            f"Batch: % van de totale inzet, {total_g:.1f} g._"
        )

    return "\n".join(lines) + "\n\n" + caption, diags


def generate_phase_block(group_rows: list[FormulaRow]) -> str:
    lines = [
        PHASE_START,
        "| Ingrediënt | Gewicht (g) | Opmerking |",
        "| :--- | ---: | :--- |",
    ]
    for r in group_rows:
        note_cell = f" {r.note} " if r.note else " "
        lines.append(f"| {r.name} | {r.weight_str} |{note_cell}|")
    lines.append(PHASE_END)
    return "\n".join(lines)


def _parse_formula_section(
    section_body: str,
    path: Path,
) -> tuple[list[str], list[FormulaRow], str, list[Diagnostic]]:
    """Parse ``## Formule`` into (groups, rows, normalized_existing_section, diagnostics)."""
    diagnostics: list[Diagnostic] = []
    lines = [ln for ln in section_body.strip().splitlines() if ln.strip()]
    table_lines = [ln for ln in lines if ln.strip().startswith("|")]

    if len(table_lines) < 3:
        diagnostics.append(Diagnostic(path, "Missing or incomplete table under '## Formule'."))
        return [], [], section_body.strip(), diagnostics

    header_cells = _parse_table_row(table_lines[0])
    align_cells = _parse_table_row(table_lines[1])
    if header_cells is None or align_cells is None or not _is_alignment_row(align_cells):
        diagnostics.append(Diagnostic(path, "Invalid table header under '## Formule'."))
        return [], [], section_body.strip(), diagnostics

    num_cols = len(header_cells)
    if num_cols not in (4, 5):
        diagnostics.append(
            Diagnostic(
                path,
                f"Formula table must have 4 or 5 columns, found {num_cols}.",
            )
        )
        return [], [], section_body.strip(), diagnostics

    groups: list[str] = []
    rows: list[FormulaRow] = []
    current_group: str | None = None
    saw_ungrouped_row = False
    saw_total_row = False

    for raw_line in table_lines[2:]:
        cells = _parse_table_row(raw_line)
        if cells is None or len(cells) != num_cols:
            diagnostics.append(
                Diagnostic(path, f"Malformed row in '## Formule': {raw_line.strip()}")
            )
            continue

        first_clean, first_bold = _strip_bold(cells[0])
        rest_empty = all(c == "" for c in cells[1:])

        if first_bold and rest_empty:
            if saw_ungrouped_row:
                diagnostics.append(
                    Diagnostic(
                        path,
                        f"Group '{first_clean}' appears after ungrouped ingredient rows; "
                        f"once a recipe has groups, every ingredient row must be in one.",
                    )
                )
            if first_clean in groups:
                diagnostics.append(
                    Diagnostic(path, f"Duplicate group '{first_clean}' in '## Formule'.")
                )
            groups.append(first_clean)
            current_group = first_clean
            continue

        if first_clean in ("Totaal (inzet)", "Total (input)"):
            saw_total_row = True
            continue

        if current_group is None:
            saw_ungrouped_row = True

        weight_cell = cells[1]
        note_cell = cells[-1]
        weight_g, weight_str, is_qs, w_diags = _normalize_weight(weight_cell, path)
        diagnostics.extend(w_diags)

        if is_qs and any(c != "" for c in cells[2:-1]):
            diagnostics.append(
                Diagnostic(
                    path,
                    f"Row '{first_clean}' is 'q.s.' and must not have percentage values.",
                )
            )

        is_intermediate = first_clean.startswith("→")
        if is_intermediate and is_qs:
            diagnostics.append(
                Diagnostic(
                    path,
                    f"Intermediate row '{first_clean}' cannot use 'q.s.'.",
                )
            )

        rows.append(
            FormulaRow(
                name=first_clean,
                weight_g=weight_g,
                weight_str=weight_str,
                note=note_cell,
                group=current_group,
                is_intermediate=is_intermediate,
                is_qs=is_qs,
            )
        )

    if not saw_total_row:
        diagnostics.append(
            Diagnostic(path, "Missing '**Totaal (inzet)**' row at end of '## Formule' table.")
        )

    return groups, rows, section_body.strip(), diagnostics


def _parse_method_section(
    section_body: str,
    groups: list[str],
    rows: list[FormulaRow],
    portion_g: float | None,
    path: Path,
) -> tuple[list[RecipePhase], list[Diagnostic]]:
    diagnostics: list[Diagnostic] = []
    h3_matches = list(_H3_RE.finditer(section_body))
    phases: list[RecipePhase] = []
    all_step_numbers: list[int] = []

    def _scan_steps(text_chunk: str, phase_label: str) -> list[int]:
        without_phase = _PHASE_BLOCK_RE.sub("", text_chunk)
        nums: list[int] = []
        for line in without_phase.splitlines():
            m = _STEP_LINE_RE.match(line)
            if m:
                nums.append(int(m.group(1)))
                step_text = m.group(2)
            elif line.startswith("   ") and not line.strip().startswith("|"):
                step_text = line.strip()
            else:
                continue

            for wm in _WEIGHT_IN_STEP_RE.finditer(step_text):
                raw_num = wm.group(1).replace(",", ".")
                try:
                    w_val = float(raw_num)
                except ValueError:
                    continue
                if portion_g is not None and abs(w_val - portion_g) < 1e-6:
                    continue
                diagnostics.append(
                    Diagnostic(
                        path,
                        f"Step in '{phase_label}' contains weight '{wm.group(0)}'; "
                        f"ingredient weights belong only in '## Formule'.",
                    )
                )
        return nums

    if not h3_matches:
        step_nums = _scan_steps(section_body, "Bereiding")
        all_step_numbers.extend(step_nums)
    else:
        for idx, m in enumerate(h3_matches):
            p_name = m.group(1).strip()
            p_start = m.end()
            p_end = h3_matches[idx + 1].start() if idx + 1 < len(h3_matches) else len(section_body)
            p_body = section_body[p_start:p_end]

            pb_match = _PHASE_BLOCK_RE.search(p_body)
            step_nums = _scan_steps(p_body, p_name)
            all_step_numbers.extend(step_nums)

            phases.append(
                RecipePhase(
                    name=p_name,
                    has_phase_block=pb_match is not None,
                    phase_block_text=pb_match.group(0) if pb_match is not None else None,
                    step_numbers=tuple(step_nums),
                )
            )

    expected_steps = list(range(1, len(all_step_numbers) + 1))
    if not all_step_numbers:
        diagnostics.append(Diagnostic(path, "No numbered steps found under '## Bereiding'."))
    elif all_step_numbers != expected_steps:
        diagnostics.append(
            Diagnostic(
                path,
                f"Steps under '## Bereiding' must be numbered continuously "
                f"1..{len(all_step_numbers)}, found {all_step_numbers}.",
            )
        )

    phase_names = [p.name for p in phases]
    matched_group_phases = [p for p in phase_names if p in groups]
    for g in groups:
        if g not in phase_names:
            diagnostics.append(
                Diagnostic(
                    path,
                    f"Formula group '{g}' has no matching '### {g}' section under '## Bereiding'.",
                )
            )

    expected_order = [g for g in groups if g in matched_group_phases]
    if matched_group_phases != expected_order:
        diagnostics.append(
            Diagnostic(
                path,
                f"Grouped phases under '## Bereiding' ({matched_group_phases}) do not match "
                f"the order in '## Formule' ({expected_order}).",
            )
        )

    for p in phases:
        if p.name in groups:
            g_rows = [r for r in rows if r.group == p.name]
            expected_pb = generate_phase_block(g_rows)
            if not p.has_phase_block:
                diagnostics.append(
                    Diagnostic(
                        path,
                        f"Phase '### {p.name}' is missing its generated '<!-- culinaria:phase -->' "
                        f"table; run 'culinaria fmt'.",
                    )
                )
            elif p.phase_block_text != expected_pb:
                diagnostics.append(
                    Diagnostic(
                        path,
                        f"Phase table in '### {p.name}' is out of date with '## Formule'; "
                        f"run 'culinaria fmt'.",
                    )
                )
        elif p.has_phase_block:
            diagnostics.append(
                Diagnostic(
                    path,
                    f"Phase '### {p.name}' has a '<!-- culinaria:phase -->' table, "
                    f"but '{p.name}' is not a group in '## Formule'.",
                )
            )

    return phases, diagnostics


def _validate_iteration_log(
    section_body: str,
    version: str,
    path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    h3_matches = list(_H3_RE.finditer(section_body))
    if not h3_matches:
        diagnostics.append(
            Diagnostic(
                path, "'## Iteratielog' must contain at least one '### vX.Y - YYYY-MM-DD' entry."
            )
        )
        return diagnostics

    versions: list[str] = []
    for m in h3_matches:
        header_text = m.group(1).strip()
        im = _ITERATION_HEADER_RE.match(header_text)
        if not im:
            diagnostics.append(
                Diagnostic(
                    path,
                    f"Invalid iteration log heading '### {header_text}': "
                    f"expected '### v<version> - <YYYY-MM-DD>'.",
                )
            )
        else:
            versions.append(im.group(1))

    if versions and version and versions[0] != version:
        diagnostics.append(
            Diagnostic(
                path,
                f"Frontmatter version '{version}' does not match newest iteration log entry "
                f"'v{versions[0]}'.",
            )
        )
    return diagnostics


def parse_recipe(
    text: str,
    path: Path,
    *,
    flour_names: frozenset[str] = frozenset(),
) -> tuple[Recipe | None, list[Diagnostic]]:
    diagnostics: list[Diagnostic] = []
    file_id = path.stem
    if not is_valid_id(file_id):
        diagnostics.append(
            Diagnostic(
                path,
                f"Invalid recipe file ID '{file_id}': must be lowercase ASCII with hyphens.",
            )
        )

    fm, _raw_fm, body, fm_diags = split_frontmatter(text, path)
    diagnostics.extend(fm_diags)
    if fm_diags:
        return None, diagnostics

    for key in sorted(set(fm.keys()) - ALLOWED_RECIPE_FRONTMATTER_KEYS):
        diagnostics.append(Diagnostic(path, f"Unknown frontmatter key '{key}'."))

    kind = fm.get("kind")
    if not isinstance(kind, str) or kind not in VALID_RECIPE_KINDS:
        diagnostics.append(
            Diagnostic(
                path,
                f"Invalid or missing 'kind': expected one of {sorted(VALID_RECIPE_KINDS)}, "
                f"got {kind!r}.",
            )
        )
        kind_str = ""
    else:
        kind_str = kind

    status = fm.get("status")
    if not isinstance(status, str) or status not in VALID_RECIPE_STATUSES:
        diagnostics.append(
            Diagnostic(
                path,
                f"Invalid or missing 'status': expected one of {sorted(VALID_RECIPE_STATUSES)}, "
                f"got {status!r}.",
            )
        )
        status_str = ""
    else:
        status_str = status

    raw_version = fm.get("version")
    if not isinstance(raw_version, str) or not raw_version.strip():
        diagnostics.append(
            Diagnostic(
                path,
                f"'version' must be a quoted string (e.g. \"1.0\"), got {raw_version!r}.",
            )
        )
        version_str = str(raw_version) if raw_version is not None else ""
    else:
        version_str = raw_version.strip()

    domain = fm.get("domain")
    if not isinstance(domain, str) or domain not in VALID_DOMAINS:
        diagnostics.append(
            Diagnostic(
                path,
                f"Invalid or missing 'domain': expected one of {sorted(VALID_DOMAINS)}, "
                f"got {domain!r}.",
            )
        )
        domain_str = ""
    else:
        domain_str = domain

    raw_basis = fm.get("basis")
    basis: str | tuple[str, ...]
    if raw_basis in ("flour", "total"):
        basis = str(raw_basis)
    elif (
        isinstance(raw_basis, list)
        and len(raw_basis) > 0
        and all(isinstance(b, str) and b.strip() for b in raw_basis)
    ):
        basis = tuple(b.strip() for b in raw_basis)
    else:
        diagnostics.append(
            Diagnostic(
                path,
                f"Invalid or missing 'basis': expected a non-empty list of ingredient names, "
                f"'flour', or 'total', got {raw_basis!r}.",
            )
        )
        basis = ()

    def _parse_str_list(key: str) -> tuple[str, ...]:
        val = fm.get(key)
        if val is None:
            return ()
        if not isinstance(val, list) or not all(isinstance(x, str) and x.strip() for x in val):
            diagnostics.append(Diagnostic(path, f"'{key}' must be a list of non-empty strings."))
            return ()
        return tuple(x.strip() for x in val)

    cuisine = _parse_str_list("cuisine")
    techniques = _parse_str_list("techniques")
    equipment = _parse_str_list("equipment")
    variants = _parse_str_list("variants")
    aliases = _parse_str_list("aliases")

    portions: float | tuple[float, float] | None = None
    if "portions" in fm and fm["portions"] is not None:
        portions, p_diags = parse_number_or_range(fm["portions"], "portions", path)
        diagnostics.extend(p_diags)

    portion_g: float | None = None
    if "portion_g" in fm and fm["portion_g"] is not None:
        pg, pg_diags = parse_number_or_range(fm["portion_g"], "portion_g", path, allow_range=False)
        diagnostics.extend(pg_diags)
        if isinstance(pg, float):
            portion_g = pg

    if portions is not None and portion_g is not None:
        diagnostics.append(
            Diagnostic(
                path,
                "Omit 'portions' when 'portion_g' is set, "
                "since portion count follows from the batch.",
            )
        )

    yield_g: float | None = None
    if "yield_g" in fm and fm["yield_g"] is not None:
        yg, yg_diags = parse_number_or_range(fm["yield_g"], "yield_g", path, allow_range=False)
        diagnostics.extend(yg_diags)
        if isinstance(yg, float):
            yield_g = yg

    variant_of = fm.get("variant_of")
    if variant_of is not None and (not isinstance(variant_of, str) or not is_valid_id(variant_of)):
        diagnostics.append(
            Diagnostic(path, f"'variant_of' must be a valid recipe ID, got {variant_of!r}.")
        )
        variant_of = None

    for v_id in variants:
        if not is_valid_id(v_id):
            diagnostics.append(
                Diagnostic(path, f"Entry '{v_id}' in 'variants' is not a valid recipe ID.")
            )

    targets: dict[str, float | tuple[float, float]] = {}
    raw_targets = fm.get("targets")
    if raw_targets is not None:
        if not isinstance(raw_targets, dict):
            diagnostics.append(Diagnostic(path, "'targets' must be a mapping."))
        else:
            for tk, tv in raw_targets.items():
                t_val, t_diags = parse_number_or_range(tv, f"targets.{tk}", path)
                diagnostics.extend(t_diags)
                if t_val is not None:
                    targets[str(tk)] = t_val

    created_val = fm.get("created")
    created_str: str | None = None
    if created_val is not None:
        if isinstance(created_val, datetime.date):
            created_str = created_val.isoformat()
        elif isinstance(created_val, str) and re.match(r"^\d{4}-\d{2}-\d{2}$", created_val):
            created_str = created_val
        else:
            diagnostics.append(
                Diagnostic(path, f"'created' must be YYYY-MM-DD, got {created_val!r}.")
            )

    h1_matches = list(_H1_RE.finditer(body))
    if not h1_matches:
        diagnostics.append(Diagnostic(path, "Missing '# Title' H1 heading."))
        return None, diagnostics
    if len(h1_matches) > 1:
        diagnostics.append(Diagnostic(path, "Multiple '# ' H1 headings found; expected only one."))
    title = h1_matches[0].group(1).strip()

    h2_matches = list(_H2_RE.finditer(body))
    sections: list[tuple[str, str]] = []
    for idx, m in enumerate(h2_matches):
        s_name = m.group(1).strip()
        s_start = m.end()
        s_end = h2_matches[idx + 1].start() if idx + 1 < len(h2_matches) else len(body)
        sections.append((s_name, body[s_start:s_end]))

    sec_names = [s[0] for s in sections]
    formula_sec = next((s for s in sections if s[0] in FORMULA_HEADERS), None)
    method_sec = next((s for s in sections if s[0] in METHOD_HEADERS), None)
    iter_sec = next((s for s in sections if s[0] in ITERATION_LOG_HEADERS), None)

    if formula_sec is None:
        diagnostics.append(Diagnostic(path, "Missing '## Formule' section."))
    if method_sec is None:
        diagnostics.append(Diagnostic(path, "Missing '## Bereiding' section."))
    if iter_sec is None:
        diagnostics.append(Diagnostic(path, "Missing '## Iteratielog' section."))

    if (
        formula_sec is not None
        and method_sec is not None
        and sec_names.index(formula_sec[0]) > sec_names.index(method_sec[0])
    ):
        diagnostics.append(Diagnostic(path, "'## Formule' must appear before '## Bereiding'."))

    groups: list[str] = []
    rows: list[FormulaRow] = []
    if formula_sec is not None:
        groups, rows, existing_formula_text, f_diags = _parse_formula_section(formula_sec[1], path)
        diagnostics.extend(f_diags)
        if not f_diags and basis != () and not (basis == "flour" and not flour_names):
            expected_formula, b_diags = generate_formula_section(
                tuple(rows), basis, flour_names, path
            )
            diagnostics.extend(b_diags)
            if not b_diags and existing_formula_text != expected_formula:
                diagnostics.append(
                    Diagnostic(
                        path,
                        "'## Formule' table or caption is out of date; run 'culinaria fmt'.",
                    )
                )

    phases: list[RecipePhase] = []
    if method_sec is not None:
        phases, m_diags = _parse_method_section(method_sec[1], groups, rows, portion_g, path)
        diagnostics.extend(m_diags)

    if iter_sec is not None:
        diagnostics.extend(_validate_iteration_log(iter_sec[1], version_str, path))

    recipe = Recipe(
        id=file_id,
        path=path,
        title=title,
        kind=kind_str,
        status=status_str,
        version=version_str,
        domain=domain_str,
        basis=basis,
        cuisine=cuisine,
        techniques=techniques,
        equipment=equipment,
        portions=portions,
        portion_g=portion_g,
        yield_g=yield_g,
        variant_of=variant_of,
        variants=variants,
        time=fm.get("time") if isinstance(fm.get("time"), str) else None,
        storage=fm.get("storage") if isinstance(fm.get("storage"), str) else None,
        targets=targets,
        aliases=aliases,
        source=fm.get("source") if isinstance(fm.get("source"), str) else None,
        created=created_str,
        groups=tuple(groups),
        rows=tuple(rows),
        phases=tuple(phases),
    )
    return recipe, diagnostics


def _rewrite_frontmatter_aliases(
    raw_fm: str,
    ingredient_aliases: dict[str, str],
    equipment_aliases: dict[str, str],
) -> str:
    """Rewrite aliased basis ingredients and equipment names in the raw YAML frontmatter block."""
    if not ingredient_aliases and not equipment_aliases:
        return raw_fm

    lines = raw_fm.splitlines(keepends=True)
    current_key: str | None = None
    out: list[str] = []
    for line in lines:
        key_match = re.match(r"^([a-z_]+):", line)
        if key_match:
            current_key = key_match.group(1)
        elif current_key in ("basis", "equipment"):
            item_match = re.match(r"^(\s*-\s+)(.+?)(\r?\n)$", line)
            if item_match:
                prefix, item_val, newline = item_match.groups()
                clean = item_val.strip()
                lookup = ingredient_aliases if current_key == "basis" else equipment_aliases
                if clean in lookup:
                    line = f"{prefix}{lookup[clean]}{newline}"
        out.append(line)
    return "".join(out)


def _format_method_section(
    method_body: str,
    groups: tuple[str, ...],
    rows: tuple[FormulaRow, ...],
) -> str:
    """Update or insert ``<!-- culinaria:phase -->`` blocks under ``## Bereiding``."""
    if not groups:
        return method_body

    for group_name in groups:
        h3_pattern = re.compile(rf"^### {re.escape(group_name)}$", re.MULTILINE)
        if not h3_pattern.search(method_body):
            group_idx = groups.index(group_name)
            g_rows = [r for r in rows if r.group == group_name]
            pb = generate_phase_block(g_rows)
            new_sec = f"\n\n### {group_name}\n\n{pb}\n"
            if group_idx == 0:
                method_body = f"\n\n### {group_name}\n\n{pb}\n\n" + method_body.lstrip()
            else:
                prev_group = groups[group_idx - 1]
                prev_m = re.search(rf"^### {re.escape(prev_group)}$", method_body, re.MULTILINE)
                if prev_m:
                    next_h3 = _H3_RE.search(method_body, prev_m.end())
                    insert_pos = next_h3.start() if next_h3 else len(method_body)
                    method_body = (
                        method_body[:insert_pos].rstrip()
                        + new_sec
                        + ("\n" + method_body[insert_pos:].lstrip() if next_h3 else "\n")
                    )

    h3_matches = list(_H3_RE.finditer(method_body))
    if not h3_matches:
        return method_body

    parts: list[str] = [method_body[: h3_matches[0].start()]]
    for idx, m in enumerate(h3_matches):
        p_name = m.group(1).strip()
        p_start = m.start()
        p_end = h3_matches[idx + 1].start() if idx + 1 < len(h3_matches) else len(method_body)
        chunk = method_body[p_start:p_end]

        if p_name in groups:
            g_rows = [r for r in rows if r.group == p_name]
            expected_pb = generate_phase_block(g_rows)
            if _PHASE_BLOCK_RE.search(chunk):
                chunk = _PHASE_BLOCK_RE.sub(expected_pb, chunk, count=1)
            else:
                heading_line_end = chunk.find("\n")
                if heading_line_end == -1:
                    chunk = f"{chunk}\n\n{expected_pb}\n"
                else:
                    rest = chunk[heading_line_end + 1 :].lstrip("\n")
                    chunk = f"{chunk[: heading_line_end + 1]}\n{expected_pb}\n\n{rest}"
        parts.append(chunk)

    return "".join(parts)


def format_recipe(
    text: str,
    path: Path,
    *,
    ingredient_aliases: dict[str, str] | None = None,
    equipment_aliases: dict[str, str] | None = None,
    flour_names: frozenset[str] = frozenset(),
) -> tuple[str, list[Diagnostic]]:
    """Format a recipe file idempotently:
    - rewrite ingredient and equipment aliases to canonical names;
    - normalize decimal commas in weights;
    - recompute Schaling (%), Batch (%), Totaal (inzet), basis bolding, and table caption;
    - regenerate or insert ``<!-- culinaria:phase -->`` tables under ``## Bereiding``.
    """
    ing_map = ingredient_aliases or {}
    eq_map = equipment_aliases or {}

    _fm, raw_fm, body, fm_diags = split_frontmatter(text, path)
    if fm_diags:
        return text, fm_diags

    raw_fm = _rewrite_frontmatter_aliases(raw_fm, ing_map, eq_map)
    updated_text = raw_fm + body

    recipe, diagnostics = parse_recipe(updated_text, path, flour_names=flour_names)
    recoverable_phrases = (
        "uses a decimal comma",
        "table or caption is out of date",
        "is missing its generated '<!-- culinaria:phase -->'",
        "Phase table in '### ",
        "has no matching '### ",
    )
    hard_errors = [d for d in diagnostics if not any(p in d.message for p in recoverable_phrases)]
    if recipe is None or hard_errors:
        return text, hard_errors

    canonical_rows = tuple(
        FormulaRow(
            name=ing_map.get(r.name, r.name) if not r.is_intermediate else r.name,
            weight_g=r.weight_g,
            weight_str=r.weight_str,
            note=r.note,
            group=r.group,
            is_intermediate=r.is_intermediate,
            is_qs=r.is_qs,
        )
        for r in recipe.rows
    )
    canonical_basis: str | tuple[str, ...]
    if isinstance(recipe.basis, tuple):
        canonical_basis = tuple(ing_map.get(b, b) for b in recipe.basis)
    else:
        canonical_basis = recipe.basis

    formula_md, b_diags = generate_formula_section(
        canonical_rows, canonical_basis, flour_names, path
    )
    if b_diags:
        return text, b_diags

    h2_matches = list(_H2_RE.finditer(body))
    if not h2_matches:
        return text, diagnostics

    new_body_parts: list[str] = [body[: h2_matches[0].start()]]
    for idx, m in enumerate(h2_matches):
        s_name = m.group(1).strip()
        s_end = h2_matches[idx + 1].start() if idx + 1 < len(h2_matches) else len(body)
        s_content = body[m.end() : s_end]

        if s_name in FORMULA_HEADERS:
            new_body_parts.append(f"## {s_name}\n\n{formula_md}\n\n")
        elif s_name in METHOD_HEADERS:
            formatted_method = _format_method_section(s_content, recipe.groups, canonical_rows)
            new_body_parts.append(f"## {s_name}{formatted_method}")
        else:
            new_body_parts.append(body[m.start() : s_end])

    result = raw_fm + "".join(new_body_parts)
    if not result.endswith("\n"):
        result += "\n"
    return result, []
