# Ingredient family file format (draft v0)

Status: **draft for review** - not implemented yet. Decision recorded in
[ADR 0006](../decisions/0006-ingredient-family-files-and-hierarchy.md). Worked examples in
[`examples/ingredients/`](examples/ingredients/).

## Goals

- Keep `03_reference/ingredients/` compact (~15-30 files for the whole kitchen) and easy to
  browse in Obsidian, VS Code and on GitHub.
- Show all related ingredients (e.g. all sugars, all rice types, all flours) side by side
  for comparison and R&D brainstorming.
- Avoid data duplication between generic functional ingredients (`Basmatirijst`) and
  specific commercial products or cultivars (`Rahman Superbasmati`, `Tilda Pure Basmati`).
- Support both fine-grained agent queries (fetching a single resolved ingredient entry) and
  broad brainstorming queries (loading an entire family).

## Three-level hierarchy

One file per **ingredient family** in `03_reference/ingredients/<family-id>.md`:

| Level | Heading | Role | Example |
| --- | --- | --- | --- |
| 1. Family | `# H1` | Groups related ingredients; holds family notes and a generated summary table | `# Rijst`, `# Suikers` |
| 2. Functional ingredient | `## H2` | A distinct culinary/chemical ingredient type with baseline composition and functional data | `## Basmatirijst`, `## Dextrose` |
| 3. Variant / product | `### H3` | A specific brand, cultivar or commercial product under its `##` parent; inherits parent data and overrides only what differs | `### Rahman Superbasmati`, `### Tilda Pure Basmati` |

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

Each `##` or `###` section starts with a structured property list (bullet items with bold
keys), followed by optional free-text notes on culinary behavior, science and handling.

Standard property keys (Dutch or English accepted by the parser):

- **Aliassen** (`Aliases`) - comma-separated alternative names matched in recipe tables.
- **Merk** (`Brand`) - manufacturer or brand name (mainly on `###` variants, or on `##`
  when a functional ingredient is only stocked from one brand).
- **Voorraad** (`Pantry`) - `ja` or `nee`.
- **Rol** (`Role`) - optional sub-classification used by calculators, e.g. `flour` (for
  `basis: flour` in bread/pastry recipes) or `inclusion`.
- **Samenstelling (per 100 g)** (`Composition (per 100 g)`) - comma-separated key-value
  pairs:
  - general: `water`, `droge stof` (`solids`), `koolhydraten` (`carbs`), `suikers`
    (`sugars`), `eiwit` (`protein`), `vet` (`fat`), `verzadigd vet` (`saturated_fat`),
    `vezels` (`fiber`), `zout` (`salt`);
  - dairy / chocolate: `cacaoboter` (`cocoa_butter`), `vetvrije cacaobestanddelen`
    (`non_fat_cocoa_solids`), `MSNF` (milk solids non-fat), `melkvet` (`milk_fat`),
    `lactose`.
- **Functioneel** (`Functional`) - domain-specific parameters:
  - sugars & ice cream: `PAC` (anti-freezing power, sucrose = 100), `POD` (relative
    sweetness, sucrose = 100), `DE` (dextrose equivalent), `Brix`;
  - grains & legumes: `hydratatie` (`hydration_ratio`, mass of total free water per 1 g dry
    ingredient), `stoomtijd_min` / `kooktijd_min`, `amylose`;
  - flours: `asgehalte` (`ash_pct`), `absorptie` (`absorption_pct`), `gluten` (`sterk`,
    `medium`, `zwak`, `vrij`).
- **Bron** (`Source`) - provenance of the numbers (manufacturer technical datasheet, NEVO,
  USDA, bench measurement).

### Inheritance rules

A `###` variant inherits all properties (`Samenstelling`, `Functioneel`, `Rol`) from its
enclosing `##` section except `Aliassen`, `Merk` and `Voorraad`. Any key specified in the
`###` section overrides that specific key from the `##` parent.

## How recipes reference ingredients

- In a recipe's `## Formule` table, the **Ingrediënt** cell may name either a `##`
  functional ingredient (`Basmatirijst`, `Dextrose`, `Witte chocolade`) or a `###` variant
  (`Rahman Superbasmati`, `Valrhona Ivoire 35%`), or any listed alias.
- Use a `##` functional ingredient name when the recipe works with any standard product of
  that type; use a `###` variant name when the recipe is calibrated to that specific
  product's properties (such as `jollof-rahman-superbasmati.md` or `Valrhona Guanaja 70%`).
- Every `##` name, `###` name and alias must be unique across all files in
  `03_reference/ingredients/`.
