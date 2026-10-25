# Ingredient family file format (draft v0)

Status: **draft for review** - not implemented yet. Decision recorded in
[ADR 0006](../decisions/0006-ingredient-family-files-and-hierarchy.md). Worked examples in
[`examples/ingredients/`](examples/ingredients/).

## Goals

- Keep `03_reference/ingredients/` compact (~15-30 files for the whole kitchen) and easy to
  browse in Obsidian, VS Code and on GitHub.
- Show all related ingredients (e.g. all sugars, all rice types, all flours) side by side
  for comparison and R&D brainstorming.
- Store structured data in YAML with fixed English keys and fixed units - no free-text
  number/unit parsing, and no derived numbers stored as truth.
- Avoid data duplication between generic functional ingredients (`Basmatirijst`) and
  specific commercial products or cultivars (`Rahman Superbasmati`, `Tilda Pure Basmati`)
  via per-property inheritance.
- Distinguish verified datasheets, food databases, own measurements and unverified claims
  so calculators never silently trust unverified numbers.
- Keep reference data stable: no stock/pantry flags and no recipe-specific method steps.

## Three-level hierarchy

One file per **ingredient family** in `03_reference/ingredients/<family-id>.md`:

| Level | Heading | Role | Example |
| --- | --- | --- | --- |
| 1. Family | `# H1` | Groups related ingredients; holds family notes and a generated summary table | `# Rijst`, `# Suikers` |
| 2. Functional ingredient | `## H2` | A distinct culinary/chemical ingredient type with baseline composition and functional data | `## Basmatirijst`, `## Dextrose` |
| 3. Variant / product | `### H3` | A specific brand, cultivar or commercial product under its `##` parent; inherits parent properties per key and overrides only what differs | `### Rahman Superbasmati`, `### Tilda Pure Basmati` |

## Frontmatter

```yaml
---
kind: ingredient_family
category: grain
calculators:
  - hydration
---
```

| Field | Required | Example | Notes |
| --- | --- | --- | --- |
| `kind` | yes | `ingredient_family` | fixed |
| `category` | yes | `grain` | `grain`, `flour`, `sugar`, `dairy`, `fat`, `chocolate`, `fruit`, `hydrocolloid`, `legume`, `meat`, `nut`, `aromatic`, `condiment`, `alcohol` |
| `calculators` | no | `[ice_cream]` | `ice_cream`, `dough`, `hydration`, `safety`; tells `check` which numeric properties are required |

## Summary table (generated)

Directly under the `# H1` intro, `culinaria fmt` generates a comparison table between
`<!-- culinaria:overview -->` and `<!-- /culinaria:overview -->` summarizing all `##` and
`###` entries in the file (with `###` variants indented under their parent using `↳`).

## Functional ingredient (`##`) and variant (`###`) sections

Each `##` or `###` section starts with a fenced `yaml` block holding its structured
properties, followed by optional free-text prose describing general culinary behavior,
physical-chemical mechanisms and ingredient-level handling (never recipe-specific steps).

### Property keys and fixed units

All schema keys are English; every numeric key has a fixed unit so values are plain YAML
numbers (`12.0`) or `[min, max]` ranges (`[14, 16]`):

| Key | Type / Unit | Meaning |
| --- | --- | --- |
| `aliases` | `list[str]` | Alternative names matched in recipe tables |
| `brand` | `str` | Manufacturer or brand name |
| `role` | `str` | Optional sub-role for calculators: `flour` (for `basis: flour`), `grain`, `inclusion` |
| `source_type` | `str` | Required when properties are defined: `datasheet`, `database`, `measured`, or `unverified` |
| `source` | `str` | Required with `source_type`: datasheet code/title, NEVO/USDA entry, trial date, or chat source |
| `unverified` | `list[str]` | Optional list of property keys in this block that are unverified when the main `source_type` is `datasheet` or `database` |
| `water_pct` | `float` (g/100 g) | Water content |
| `solids_pct` | `float` (g/100 g) | Total dry matter (`100 - water_pct`) |
| `carbs_pct` | `float` (g/100 g) | Available carbohydrates |
| `sugars_pct` | `float` (g/100 g) | Total sugars (mono- and disaccharides) |
| `sucrose_pct` | `float` (g/100 g) | Sucrose fraction (when specified on datasheet, e.g. basterdsuiker, couverture, sweetened puree) |
| `invert_sugar_pct` | `float` (g/100 g) | Invert sugar fraction |
| `lactose_pct` | `float` (g/100 g) | Lactose fraction |
| `protein_pct` | `float` (g/100 g) | Total protein |
| `fat_pct` | `float` (g/100 g) | Total fat |
| `saturated_fat_pct` | `float` (g/100 g) | Saturated fatty acids |
| `cocoa_butter_pct` | `float` (g/100 g) | Cocoa butter fraction |
| `milk_fat_pct` | `float` (g/100 g) | Milk fat fraction |
| `non_fat_cocoa_solids_pct` | `float` (g/100 g) | Non-fat cocoa solids |
| `msnf_pct` | `float` (g/100 g) | Milk solids non-fat (vetvrije droge melkstof) |
| `fiber_pct` | `float` (g/100 g) | Dietary fiber |
| `salt_pct` | `float` (g/100 g) | Salt (NaCl equivalent) |
| `ash_pct` | `float` (% of dry matter) | Flour ash content (mineral fraction) |
| `pac` | `int \| float` | Anti-freezing power relative to sucrose = 100 (stored only for pure/technical sugars where it is a defining constant or datasheet value, never pre-computed for compound ingredients) |
| `pod` | `int \| float` | Sweetening power relative to sucrose = 100 (same rule as `pac`) |
| `de` | `int \| float` | Dextrose Equivalent (0-100) for glucose syrups and dextrose |
| `brix` | `float` (°Bx) | Refractometric soluble solids at 20 °C |
| `acidity_pct` | `float` (g/100 g) | Titratable acidity (as citric acid monohydrate) |
| `hydration_ratio` | `float` (g/g) | Target mass of total free water per 1 g dry ingredient |
| `steaming_min` | `int \| [int, int]` (min) | Closed-steam cooking time in minutes |
| `amylose_pct` | `float` (g/100 g starch) | Amylose fraction of starch |
| `absorption_pct` | `float` (%) | Dough water absorption capacity |
| `gluten` | `str` | Gluten network strength: `strong`, `medium`, `weak`, `none` |

### Per-property inheritance

A `###` variant inherits from its enclosing `##` section **per property key**
(`resolved = parent | variant`):

1. All composition, functional and `role` keys on the `##` parent are kept unless the
   `###` block defines the same key. For example, if `## Basmatirijst` defines
   `amylose_pct: 22.0` and `### Rahman Superbasmati` overrides only `hydration_ratio` and
   `steaming_min`, `Rahman Superbasmati` retains `amylose_pct: 22.0` and all parent
   composition keys.
2. `aliases` and `brand` are not inherited: each `##` or `###` entry has its own name,
   aliases and brand.
3. Provenance is tracked per property after merging: inherited keys keep the parent's
   `source_type` and `source`; keys defined in `###` take the variant's `source_type` and
   `source` (or `unverified` list). If a `###` block only records `brand` or `aliases` and
   overrides no numbers, it may omit `source_type` and `source`.

### Source types and validation

| `source_type` | Meaning | Validator / calculator behavior |
| --- | --- | --- |
| `datasheet` | Manufacturer technical specification sheet or label | Trusted |
| `database` | National or scientific food database (NEVO, USDA) | Trusted |
| `measured` | Own kitchen/bench measurement (with date/trial note) | Trusted |
| `unverified` | Estimate or unverified LLM-chat claim | `culinaria check` and calculators emit a warning when used |

## How recipes reference ingredients

- In a recipe's `## Formule` table, the **Ingrediënt** cell may name either a `##`
  functional ingredient (`Basmatirijst`, `Dextrose`, `Witte chocolade`) or a `###` variant
  (`Rahman Superbasmati`, `Valrhona Ivoire 35%`), or any listed alias.
- Use a `##` functional ingredient name when the recipe works with any standard product of
  that type; use a `###` variant name when the recipe is calibrated to that specific
  product's properties (such as `jollof-rahman-superbasmati.md` or `Valrhona Guanaja 70%`).
- Every `##` name, `###` name and alias must be unique across all files in
  `03_reference/ingredients/`.
