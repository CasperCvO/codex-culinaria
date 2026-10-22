# codex-culinaria

Local-first culinary R&D: a Git-versioned vault of Markdown/YAML recipes, ingredients,
equipment and knowledge notes, plus Python tooling and the `culinaria` CLI to validate and
compute over it.

Status: **Phase 0 - foundation** (see [`docs/roadmap.md`](docs/roadmap.md)).

## Requirements

- [uv](https://docs.astral.sh/uv/) - fetches Python 3.14 automatically if it is missing.

## Quickstart

```bash
uv sync
uv run culinaria --help
uv run culinaria check
```

`check` validates the vault layout. Point it elsewhere with `--vault PATH` or
`CULINARIA_VAULT` (default: `vault`).

## Development

```bash
uv run ruff format .     # format
uv run ruff check .      # lint
uv run mypy              # type-check (strict)
uv run pytest            # tests
uv run culinaria check   # validate the vault
```

## Layout

```
src/codex_culinaria/  core library + culinaria CLI
tests/                pytest suite
docs/                 architecture, roadmap, decisions (ADRs)
vault/                the culinary data (see vault/README.md)
```

## More

- [`docs/architecture.md`](docs/architecture.md) - principles and components
- [`docs/roadmap.md`](docs/roadmap.md) - phases and exit criteria
- [`docs/decisions/`](docs/decisions/) - architecture decision records
- [`vault/README.md`](vault/README.md) - vault layout
