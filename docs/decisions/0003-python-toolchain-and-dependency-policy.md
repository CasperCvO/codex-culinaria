# 3. Python toolchain and dependency policy

Status: Accepted

Date: 2026-10-22

## Context

2026 saw repeated supply-chain compromises - e.g. LiteLLM's PyPI package was compromised
twice (March and October), via a compromised CI dependency and via stolen tokens. A
single-user repo can still adopt cheap defenses.

## Decision

- Python 3.14, managed by uv, with a committed `uv.lock`.
- ruff for linting and formatting, mypy strict, pytest, Typer for the CLI.
- Dependencies are added only when needed, via `uv add` (never edited in by hand).
- uv `exclude-newer = "7 days"` in `pyproject.toml`: only releases older than 7 days can
  resolve. This is never overridden or relaxed.
- GitHub Actions are pinned to full commit SHAs with a trailing version comment, and the
  workflow uses least-privilege `permissions`. CI installs a pinned uv release (also at
  least 7 days old) instead of the latest.
- ruff excludes `vault/` and `data_examples/`, so formatting never touches user data.

## Consequences

A malicious release cannot be pulled in during its first week; every CI action resolves to
an immutable commit. Cost: occasional waits for a fresh upstream release.
