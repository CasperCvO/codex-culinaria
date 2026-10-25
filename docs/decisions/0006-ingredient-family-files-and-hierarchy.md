# 6. Ingredient family files and three-level hierarchy

Status: Accepted (amends 0005)

Date: 2026-10-23

## Context

ADR 0005 specified one Markdown file per ingredient in `03_reference/ingredients/`. In
practice, culinary R&D involves both generic functional ingredients (`Basmatirijst`,
`Dextrose`, `Pure chocolade 70%`) and brand- or cultivar-specific products (`Rahman
Superbasmati`, `Tilda Pure Basmati`, `Golden Sella Basmati`, `Valrhona Guanaja 70%`).

Giving every ingredient and brand variant its own file causes two problems:

1. **File explosion and duplication:** `03_reference/ingredients/` would grow to hundreds
   of small files repeating 90% of the same composition data.
2. **Poor comparison workflow:** Both human authors in Obsidian and the runtime R&D agent
   brainstorm by comparing alternatives within a family (e.g. comparing PAC/POD across all
   sugars in `suikers.md`, or hydration ratios across rice types in `rijst.md`). Splitting
   a family across many files forces constant file switching and multiple agent tool calls.

## Decision

- `03_reference/ingredients/` holds **one file per ingredient family** (e.g. `rijst.md`,
  `suikers.md`, `zuivel-en-eieren.md`, `bloem-en-granen.md`, `chocolade.md`), rather than
  one file per individual ingredient.
- Each family file uses a three-level heading hierarchy:
  - `# H1` - **Ingredient family** (overview, generated comparison table, general domain
    science).
  - `## H2` - **Functional ingredient** (e.g. `Basmatirijst`, `Dextrose`, `Zeeuwse bloem`):
    holds baseline composition, functional properties (hydration, PAC/POD, protein/ash),
    aliases and sources in a fenced `yaml` block with English keys and fixed units.
  - `### H3` - **Product / brand / cultivar variant** (e.g. `Rahman Superbasmati`,
    `Tilda Pure Basmati`): grouped under its `##` parent. Its `yaml` block merges **per
    property** over the parent's `yaml` block (retaining all parent properties that are not
    explicitly overridden).
- Every ingredient block declares `source_type` (`datasheet`, `database`, `measured`, or
  `unverified`) and `source` so calculators and validators can warn when calculations rely
  on unverified numbers.
- Ingredient files describe only general properties and handling of the ingredient itself,
  never recipe-specific steps.
- Pantry / stock status does **not** live in `03_reference/ingredients/`, so shopping
  changes do not dirty reference files; stock is tracked in a separate pantry file.
- Recipes may reference either a `##` functional ingredient or a `###` variant (or any of
  their aliases).
- The Python core library parses the hierarchy so agent tools can retrieve either a single
  resolved ingredient (with inherited parent properties) to save context tokens, or the
  entire family when brainstorming substitutions.

## Consequences

`03_reference/ingredients/` stays compact (~15-30 files for the whole kitchen), related
ingredients can be compared side by side in one file, and brand variants no longer
duplicate baseline data. Structured data uses YAML blocks with fixed units and per-property
inheritance, avoiding a second free-text number parser.
