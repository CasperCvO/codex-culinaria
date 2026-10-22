# 4. Agent instruction layout

Status: Accepted

Date: 2026-10-22

## Context

Two different agents work on this project: a coding agent (Devin) that edits the repo, and
a future runtime culinary agent that reads skills and prompts from the vault. Their
instructions must not leak into each other.

## Decision

- Coding agent: a lean root `AGENTS.md` (auto-loaded by Devin), `docs/` for architecture,
  roadmap and ADRs, and `.devin/skills/` for repeatable development workflows.
- Runtime culinary agent: `vault/00_context/` (skills, system prompt, house standards).
- Rejected a `.agent/` directory: Devin does not read it, and it hides documentation from
  humans.

## Consequences

`AGENTS.md` stays short and is always in context; deeper docs are linked, not inlined.
Vault instructions travel with the data and remain editor-agnostic.
