# 5. Vault layout and plain-text storage

Status: Accepted

Date: 2026-10-22

## Context

The vault must work as an Obsidian vault today, survive an editor switch, and stay
diff-friendly in git. Folders express workflow state (lab vs library vs reference); finer
classification belongs in frontmatter.

## Decision

- Top-level layout: `00_context/` (agent context), `01_rd_lab/` (work in progress),
  `02_library/components/` and `02_library/dishes/` (locked), `03_reference/ingredients/`,
  `04_knowledge/` (technique, science, food-safety notes). See `vault/README.md`.
- `02_library` rather than `02_vault`: no "vault inside the vault".
- One Markdown file with YAML frontmatter per recipe, ingredient and device.
- No database as source of truth. A SQLite index may be added later as a disposable,
  gitignored cache rebuilt from the files.
- Files must read correctly in Obsidian and VS Code; no editor-specific syntax in data.

## Consequences

Everything is greppable, diffable and portable; the trade-off is slower ad-hoc queries
until the disposable index exists.
