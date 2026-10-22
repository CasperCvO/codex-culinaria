# 2. Single repo with a configurable vault location

Status: Accepted

Date: 2026-10-22

## Context

The vault is user data that may later outgrow this repo, but today app and data evolve
together and a split would only add friction.

## Decision

Application and vault live in one repository for now. The vault path is never hard-coded:
every command resolves it via `--vault` or `CULINARIA_VAULT` (default `vault`).
References inside vault files are relative to the vault root. Code never imports from or
depends on the vault's location. The vault can be split out later with history preserved
(e.g. `git filter-repo`). The repository is local-only for now - no remote.

## Consequences

One clone gets everything; tests never touch the real vault. The split-out path stays open
because no code path assumes the vault sits next to the code.
