# Vault

This is the culinary data of codex-culinaria: recipes, ingredients, equipment and
knowledge notes as Markdown files with YAML frontmatter, versioned in git. The file
formats are defined in Phase 1 - see [`../docs/roadmap.md`](../docs/roadmap.md).

## Folders

| Folder | Contents |
| --- | --- |
| `00_context/` | Standing context for the runtime R&D agent. `equipment/` holds one file per device (capabilities, limits, settings); `skills/` holds domain instructions for the runtime agent. Later also `system_prompt.md` and `house_standards.md`. |
| `01_rd_lab/` | Work in progress: concepts and formulations under test. |
| `02_library/components/` | Locked sub-recipes: stocks, pastes, doughs, stabilizer blends, spice mixes. |
| `02_library/dishes/` | Locked complete dishes; may reference components. |
| `03_reference/ingredients/` | One file per ingredient family: composition and functional data with sources, product variants, alternative names. Used by the calculators. |
| `04_knowledge/` | Technique, science and food-safety notes. |

## Principles

- Folders express workflow state; classification lives in frontmatter.
- One file per recipe or device; one file per ingredient family in `03_reference/ingredients/`.
- Any search index is a disposable cache, never edited by hand.
- Works in Obsidian or any editor (Obsidian workspace files are gitignored).
- Content may be in Dutch.
