import re
from dataclasses import dataclass, field
from pathlib import Path

from codex_culinaria.common import (
    VALID_DOMAINS,
    Diagnostic,
    is_valid_id,
    parse_number_or_range,
    split_frontmatter,
)

VALID_EQUIPMENT_CATEGORIES: frozenset[str] = frozenset(
    {
        "thermal",
        "cold",
        "mechanical",
        "vacuum",
        "cookware",
        "measuring",
    }
)

ALLOWED_FRONTMATTER_KEYS: frozenset[str] = frozenset(
    {
        "kind",
        "category",
        "brand",
        "model",
        "aliases",
        "domains",
        "limits",
    }
)

RANGE_LIMIT_KEYS: frozenset[str] = frozenset({"batch_g", "temp_c"})
SCALAR_LIMIT_KEYS: frozenset[str] = frozenset(
    {
        "volume_ml",
        "max_input_temp_c",
        "prechill_temp_c",
        "prechill_h",
        "max_run_min",
        "vacuum_pct",
    }
)
ALLOWED_LIMIT_KEYS: frozenset[str] = RANGE_LIMIT_KEYS | SCALAR_LIMIT_KEYS

ALLOWED_SECTIONS: frozenset[str] = frozenset(
    {
        "Gebruik en instellingen",
        "Usage and settings",
        "Beperkingen",
        "Constraints",
        "Onderhoud",
        "Maintenance",
        "Onderhoud en veiligheid",
        "Maintenance and safety",
    }
)

_H1_RE = re.compile(r"^# (.+)$", re.MULTILINE)
_H2_RE = re.compile(r"^## (.+)$", re.MULTILINE)


@dataclass(frozen=True, slots=True)
class Equipment:
    id: str
    path: Path
    name: str
    category: str
    brand: str | None = None
    model: str | None = None
    aliases: tuple[str, ...] = ()
    domains: tuple[str, ...] = ()
    limits: dict[str, float | tuple[float, float]] = field(default_factory=dict)

    @property
    def max_batch_g(self) -> float | None:
        val = self.limits.get("batch_g")
        if val is None:
            return None
        if isinstance(val, tuple):
            return val[1]
        return val


def parse_equipment(text: str, path: Path) -> tuple[Equipment | None, list[Diagnostic]]:
    diagnostics: list[Diagnostic] = []
    file_id = path.stem
    if not is_valid_id(file_id):
        diagnostics.append(
            Diagnostic(
                path,
                f"Invalid equipment file ID '{file_id}': must be lowercase ASCII with hyphens.",
            )
        )

    fm, _raw_fm, body, fm_diags = split_frontmatter(text, path)
    diagnostics.extend(fm_diags)
    if fm_diags:
        return None, diagnostics

    unknown_keys = set(fm.keys()) - ALLOWED_FRONTMATTER_KEYS
    for key in sorted(unknown_keys):
        diagnostics.append(Diagnostic(path, f"Unknown frontmatter key '{key}'."))

    kind = fm.get("kind")
    if kind != "equipment":
        diagnostics.append(
            Diagnostic(path, f"Expected frontmatter 'kind: equipment', got {kind!r}.")
        )

    category = fm.get("category")
    if not isinstance(category, str) or category not in VALID_EQUIPMENT_CATEGORIES:
        diagnostics.append(
            Diagnostic(
                path,
                f"Invalid or missing 'category': expected one of "
                f"{sorted(VALID_EQUIPMENT_CATEGORIES)}, got {category!r}.",
            )
        )
        category_str = ""
    else:
        category_str = category

    brand = fm.get("brand")
    if brand is not None and (not isinstance(brand, str) or not brand.strip()):
        diagnostics.append(Diagnostic(path, "'brand' must be a non-empty string."))
        brand = None

    model = fm.get("model")
    if model is not None and (not isinstance(model, str) or not model.strip()):
        diagnostics.append(Diagnostic(path, "'model' must be a non-empty string."))
        model = None

    aliases: list[str] = []
    raw_aliases = fm.get("aliases")
    if raw_aliases is not None:
        if not isinstance(raw_aliases, list) or not all(
            isinstance(a, str) and a.strip() for a in raw_aliases
        ):
            diagnostics.append(Diagnostic(path, "'aliases' must be a list of non-empty strings."))
        else:
            aliases = [a.strip() for a in raw_aliases]

    domains: list[str] = []
    raw_domains = fm.get("domains")
    if raw_domains is not None:
        if not isinstance(raw_domains, list) or not all(isinstance(d, str) for d in raw_domains):
            diagnostics.append(Diagnostic(path, "'domains' must be a list of strings."))
        else:
            for d in raw_domains:
                if d not in VALID_DOMAINS:
                    diagnostics.append(
                        Diagnostic(
                            path,
                            f"Unknown domain '{d}' in 'domains'; expected one of "
                            f"{sorted(VALID_DOMAINS)}.",
                        )
                    )
                else:
                    domains.append(d)

    limits: dict[str, float | tuple[float, float]] = {}
    raw_limits = fm.get("limits")
    if raw_limits is not None:
        if not isinstance(raw_limits, dict):
            diagnostics.append(Diagnostic(path, "'limits' must be a mapping."))
        else:
            for k, v in raw_limits.items():
                if k not in ALLOWED_LIMIT_KEYS:
                    diagnostics.append(Diagnostic(path, f"Unknown limit key '{k}' in 'limits'."))
                    continue
                parsed_val, val_diags = parse_number_or_range(
                    v,
                    f"limits.{k}",
                    path,
                    allow_range=k in RANGE_LIMIT_KEYS,
                )
                diagnostics.extend(val_diags)
                if parsed_val is not None:
                    limits[k] = parsed_val

    h1_matches = list(_H1_RE.finditer(body))
    if not h1_matches:
        diagnostics.append(Diagnostic(path, "Missing '# Name' heading."))
        return None, diagnostics
    if len(h1_matches) > 1:
        diagnostics.append(Diagnostic(path, "Multiple '# ' H1 headings found; expected only one."))

    name = h1_matches[0].group(1).strip()
    after_h1 = body[h1_matches[0].end() :]
    h2_matches = list(_H2_RE.finditer(after_h1))
    intro = after_h1[: h2_matches[0].start()].strip() if h2_matches else after_h1.strip()
    if not intro:
        diagnostics.append(Diagnostic(path, "Missing intro paragraph under '# Name'."))

    for m in h2_matches:
        sec_title = m.group(1).strip()
        if sec_title not in ALLOWED_SECTIONS:
            diagnostics.append(Diagnostic(path, f"Unexpected section heading '## {sec_title}'."))

    equipment = Equipment(
        id=file_id,
        path=path,
        name=name,
        category=category_str,
        brand=brand,
        model=model,
        aliases=tuple(aliases),
        domains=tuple(domains),
        limits=limits,
    )
    return equipment, diagnostics
