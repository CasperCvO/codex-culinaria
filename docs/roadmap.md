# Roadmap

Each phase lists its goal and exit criteria. Phases are sequential; scope changes are
recorded in an ADR (see `docs/decisions/`).

## Phase 0 - Foundation (done)

Goal: repository, tooling, CI, docs and vault skeleton; `culinaria check` validates the
vault layout.

Exit: format, lint, type-check, tests and `culinaria check` green locally and in CI.

## Phase 1 - Data model & formats (current)

Goal: the recipe, ingredient and equipment file formats, plus a parser/serializer and
validators.

Recipe file format - draft in `docs/specs/recipe-format.md`: a full formula table up front
(hand-written, the source of every weight), then per-phase sections in chronological
order whose ingredient tables are generated from it, so they cannot disagree. Also:

- the 100% basis can be one line, a group of lines (e.g. flour + oats), total flour, or
  total batch;
- ingredient lines reference ingredient or component IDs;
- steps reference ingredient lines, so scaled weights fill in;
- split uses of one ingredient are separate lines;
- data uses plain numbers (display may use Dutch notation);
- target, computed and measured metrics are kept apart;
- an iteration log tracks changes over time.

Ingredient and equipment schemas: one file per ingredient family (with functional
ingredients and brand/cultivar variants in a heading hierarchy, see
`docs/specs/ingredient-format.md`) and one file per device; composition data with sources;
aliases.

Deliverables:

- parser/serializer with canonical, idempotent formatting (minimal git diffs);
- `culinaria check` validates schema and cross-references; `culinaria fmt` normalizes;
- `data_examples/` (mixed formats and languages from many LLM chats) migrated into the
  vault as the first content and test fixtures.

Exit: examples migrated, validator green, round-trip tests pass.

## Phase 2 - Calculators

Goal: deterministic culinary math over the vault data.

- Scaler: any basis or target yield.
- Dough: hydration including preferments, desired dough temperature.
- Ice cream: total solids, fat, MSNF, sugars, POD, PAC from sourced reference data.
- Food-safety checks as validators: e.g. curing-salt dosing, PHA boil for kidney beans,
  pasteurization.

Exposed via the CLI.

Exit: tests pass against hand-checked examples.

## Phase 3 - Agent runtime

Goal: an LLM adapter (Gemini + OpenRouter) with semantic tools over the core library - the
agent never writes recipe files as free text. Skills come from `vault/00_context/skills/`.
CLI chat first.

## Phase 4 - Web workbench

Goal: split-pane UI with live file view, scaling as a view (not an edit), metrics readout,
save iteration / promote via git.

## Phase 5 - Extensions

Goal: web research tool, search index, allergen roll-up, costing.

## Open decisions

- Recipe layout details (table vs per-phase sections, generated part).
- ID scheme and link syntax for cross-references.
- Folder vs `status` field as the single source of workflow state.
- Pantry file format (kept separate from `03_reference/ingredients/` so stock changes do
  not dirty reference data; see ADR 0006).
- Trial photos/attachments (Git LFS?).
- LLM adapter: thin wrapper over an official SDK vs LiteLLM - LiteLLM's PyPI package was
  compromised twice in 2026 (March and October); also the data-privacy tier
  (paid / zero-retention routing).
- Web stack.
- Conversation persistence.
