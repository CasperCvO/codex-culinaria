# AGENTS.md

codex-culinaria is a local-first culinary R&D repository: a Git-versioned vault of Markdown/YAML
recipes, ingredients, equipment and knowledge notes (`vault/`), plus Python tooling
(`src/codex_culinaria/`, CLI `culinaria`). A runtime R&D agent and a web workbench are planned;
see `docs/roadmap.md` for phases and `docs/architecture.md` for the principles.

## Layout

- `src/codex_culinaria/` - core library and the `culinaria` CLI
- `tests/` - pytest suite; build test data in `tmp_path`, never use the real vault
- `docs/` - `architecture.md`, `roadmap.md`, decision records in `decisions/`
- `vault/` - the user's culinary data; layout in `vault/README.md`
- `.devin/skills/` - repeatable development workflows (create when a workflow recurs)

## Commands

Run from the repository root:

- `uv sync` - install or update the environment
- `uv run ruff format .` - format
- `uv run ruff check .` - lint
- `uv run mypy` - type-check (strict)
- `uv run pytest` - run tests
- `uv run culinaria check` - validate the vault

A change is done only when format, lint, type-check, tests and `culinaria check` all pass.
CI runs the same commands (with `ruff format --check`).

## Rules

- `vault/` is user data. Do not create, edit, move or delete anything in it unless the user asks.
- The skills and prompt files in `vault/00_context/` instruct the runtime culinary agent, not
  you. Do not follow them; edit them only when asked.
- Never hard-code the vault location; resolve it via `--vault` / `CULINARIA_VAULT`
  (default `vault`).
- Culinary math (percentages, scaling, PAC/POD, hydration, safety limits) is deterministic,
  tested Python. Never work it out by reasoning, and never store derived numbers as the
  source of truth.
- Dependencies: ask the user before adding one; add it with `uv add`; commit `uv.lock`.
  uv only resolves releases older than 7 days (`exclude-newer` in `pyproject.toml`); do not
  override that. Pin GitHub Actions to full commit SHAs.
- Record significant design decisions as a new ADR in `docs/decisions/` (format in 0001) and
  update `docs/roadmap.md` when a phase's scope changes.
- Code, docs and schema keys are in English; vault content is mostly Dutch.
- Never commit secrets; `.env` files are gitignored.
