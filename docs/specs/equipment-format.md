# Equipment file format (draft v0)

Status: **draft for review** - not implemented yet. Worked examples in
[`examples/equipment/`](examples/equipment/).

## Goals

- Give the kitchen's physical constraints a single source of truth in
  `00_context/equipment/<device-id>.md` (batch limits, temperature ranges, conditioning rules,
  settings tables).
- Let recipes reference equipment by plain name (`KitchenAid ijsmaker`, `Boxer 35`, `Oven`),
  validated by `culinaria check` and canonicalized via aliases by `culinaria fmt`.
- Keep structured limits in YAML frontmatter with fixed English keys and fixed units so
  validators and calculators can check recipes against device limits without parsing prose.
- Give the runtime R&D agent (Phase 3) concise, reliable context on what equipment is available
  in the kitchen and how each device behaves.
- Stay brief for simple tools while supporting rich settings tables for calibrated devices (such
  as pasta rollers, chamber vacuum sealers, or passive freezer bowls).

## Scope: what gets a file

One file per device in `00_context/equipment/<device-id>.md`. Create a file when a piece of
equipment:

1. is named in a recipe's `equipment:` frontmatter list, or
2. imposes a physical constraint, calibration offset, or discrete setting scale that recipes or
   the R&D agent rely on (e.g. maximum batch mass in a passive ice cream bowl, maximum product
   temperature in a chamber vacuum sealer, mm thickness per roller setting on a pasta machine).

Generic small hand tools (whisk, bowl, chef's knife, cutting board, sieve) do not go in recipe
`equipment:` lists and do not get equipment files.

## Anatomy

One device per Markdown file, in this order:

| Part | Required | Contents |
| --- | --- | --- |
| Frontmatter | yes | structured metadata and numeric limits, see [Frontmatter](#frontmatter) |
| `# Name` | yes | canonical device name (the only H1); matched by recipe `equipment:` lists |
| Intro | yes | 1-3 sentences: what the device is and its role in the kitchen |
| `## Gebruik en instellingen` | no | operating procedure, conditioning rules, or a settings table |
| `## Beperkingen` | no | thermodynamic or mechanical reasons behind the device's limits |
| `## Onderhoud` | no | cleaning, storage, or care rules that prevent damage |

Section headings are Dutch because the vault content is Dutch; the parser also accepts the
English equivalents (`Usage and settings`, `Constraints`, `Maintenance`). Omit optional sections
when a device does not need them.

## Frontmatter

```yaml
---
kind: equipment
category: cold
brand: KitchenAid
model: 5KSM2CB5
aliases:
  - IJsmachine
  - KitchenAid-vrieskom
  - KitchenAid ijskom
domains:
  - frozen
limits:
  volume_ml: 1900
  batch_g: [350, 650]
  max_input_temp_c: 4
  prechill_temp_c: -18
  prechill_h: 24
  max_run_min: 15
---
```

| Field | Required | Example | Notes |
| --- | --- | --- | --- |
| `kind` | yes | `equipment` | fixed |
| `category` | yes | `cold` | `thermal`, `cold`, `mechanical`, `vacuum`, `cookware`, `measuring` |
| `brand` | no | `Henkelman` | manufacturer or brand |
| `model` | no | `Boxer 35` | model name or code |
| `aliases` | no | `[IJsmachine]` | alternative names matched in recipe `equipment:` lists |
| `domains` | no | `[frozen]` | recipe domains (`frozen`, `pastry`, `bread`, `savory`, `preserves`, `confectionery`, `beverage`) for selective agent context loading |
| `limits` | no | see below | numeric operating bounds and capacities with fixed units |

### `limits` keys and fixed units

Every key in `limits` has a fixed unit and takes either a plain number (`650`) or a
`[min, max]` range (`[350, 650]`):

| Key | Type / Unit | Meaning |
| --- | --- | --- |
| `batch_g` | `float \| [float, float]` (g) | Working batch mass per cycle (single value = maximum working mass; range = `[min, max]`) |
| `volume_ml` | `float` (ml) | Nominal vessel or chamber volume |
| `temp_c` | `float \| [float, float]` (°C) | Operating temperature range |
| `max_input_temp_c` | `float` (°C) | Maximum product temperature when loaded into the device |
| `prechill_temp_c` | `float` (°C) | Required conditioning temperature before use (e.g. `-18` or lower) |
| `prechill_h` | `float` (h) | Minimum conditioning duration before use |
| `max_run_min` | `float` (min) | Maximum continuous run time per cycle |
| `vacuum_pct` | `float` (%) | Maximum chamber/extraction vacuum percentage |

## Names, files and resolution

- File name = ID: lowercase ASCII with hyphens (`kitchenaid-ijsmaker.md`, `boxer-35.md`),
  unique across the vault.
- Every `# Name` and alias in `00_context/equipment/` must be unique across all equipment
  files.
- In a recipe's `equipment:` frontmatter list, each item must match a device's `# Name` or one
  of its `aliases`.
  - `culinaria check` reports unknown equipment names with close-match suggestions.
  - `culinaria fmt` rewrites any alias (e.g. `Heteluchtoven` or `IJsmachine`) to the device's
    canonical `# Name`.
- When a recipe declares a device with `limits.batch_g` and the recipe's input total (or mix
  mass) exceeds the upper bound of `batch_g`, `culinaria check` emits a warning that the recipe
  exceeds a single-cycle batch for that device.

## Numbers

As in recipes and ingredient files: decimal point everywhere (`4.8 mm`, `-18 °C`, `99.8%`),
never a thousands separator (`1900`, not `1.900`).
