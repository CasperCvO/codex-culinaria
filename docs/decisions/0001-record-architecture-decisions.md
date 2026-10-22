# 1. Record architecture decisions

Status: Accepted

Date: 2026-10-22

## Context

Design decisions for this repo need to outlive the chat sessions in which they were made.

## Decision

Significant decisions are recorded as Architecture Decision Records (ADRs) in
`docs/decisions/`, numbered sequentially (`NNNN-title.md`). Once accepted an ADR is
immutable: to reverse it, write a new ADR and mark the old one `Superseded by NNNN`.

Template:

```markdown
# N. Title

Status: Proposed | Accepted | Superseded by NNNN

Date: YYYY-MM-DD

## Context

## Decision

## Consequences
```

## Consequences

Decisions are auditable and cheap to write; new contributors (human or agent) can see why
things are the way they are.
