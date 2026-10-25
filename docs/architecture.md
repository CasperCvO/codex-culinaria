# Architecture

codex-culinaria is a local-first culinary R&D system: plain-text culinary data in a
Git-versioned vault, a tested Python core library for everything that must be computed or
validated, a CLI on top of it, and - in later phases - a runtime R&D agent and a web
workbench. The vault is the product; the tooling serves it.

## Principles

1. **Plain text in git is the source of truth.** Recipes, ingredients, equipment and notes
   are Markdown files with YAML frontmatter in the vault. Any index or database is a
   disposable cache rebuilt from those files, never edited by hand.
2. **Deterministic computation.** Percentages, scaling, PAC/POD, hydration and safety
   limits are computed by tested Python, never by an LLM. Derived numbers are not stored
   as truth.
3. **Vault decoupled from code.** The vault location is resolved via
   `--vault` / `CULINARIA_VAULT` (default `vault`); references inside the vault are
   relative to the vault root. The code never imports from or hard-codes it, and the vault
   can move to its own repository later.
4. **Two tiers of agent instructions.** The coding agent reads `AGENTS.md`, `docs/` and
   `.devin/skills/`; the runtime culinary agent reads `vault/00_context/`. Neither reads
   the other's instructions.
5. **Local-first.** Everything runs locally; cloud LLM APIs are only used by the agent
   runtime (Phase 3).
6. **Editor-agnostic files.** Files must read correctly in Obsidian, VS Code and on
   GitHub. Tooling never depends on editor-specific syntax such as Obsidian
   `[[wikilinks]]`.

## Components

| Component | Status |
| --- | --- |
| Vault | Populated with Phase 1 recipes, ingredient families, equipment and knowledge notes |
| Core library `codex_culinaria` | Schema, parser, formatter and cross-reference validator (Phase 1); calculators in Phase 2 |
| CLI `culinaria` | `check` and `fmt` commands |
| Agent runtime | Phase 3 |
| Web workbench | Phase 4 |

## Languages

Code, docs and schema keys are English. Vault content is Dutch (any language is allowed).
