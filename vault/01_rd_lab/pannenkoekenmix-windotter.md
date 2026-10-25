---
kind: component
status: testing
version: "1.0"
domain: pastry
basis: total
techniques:
  - enzymatische-hydrolyse
source: LLM-chat (data_examples/Pannenkokenmix_reg.md)
created: 2026-10-25
---

# Pannenkoekenmix (stijl De Windotter)

Reconstructie van de molen-pannenkoekenmix van De Windotter op basis van ingrediëntenvolgorde en
vezel-/eiwitbalans (60% patentbloem, 25% volkoren tarwebloem, 14% boekweitmeel, 1% actief
gerstemoutmeel).

## Formule

| Ingrediënt | Gewicht (g) | Batch (%) | Opmerking |
| :--- | ---: | ---: | :--- |
| Patentbloem | 600.0 | 60.0% | |
| Volkoren tarwebloem | 250.0 | 25.0% | |
| Boekweitmeel | 140.0 | 14.0% | |
| Actief gerstemoutmeel | 10.0 | 1.0% | vervangt tarwemoutmeel + enzym |
| Ascorbinezuur | 0.04 | 0.004% | 40 mg, optionele meelverbeteraar |
| **Totaal (inzet)** | **1000.0** | **100.0%** | |

_Batch: % van de totale inzet, 1000.0 g._

## Bereiding

1. Meng het ascorbinezuur en het actieve gerstemoutmeel eerst door een klein deel van de
   patentbloem als voormengsel.
2. Voeg de resterende patentbloem, de volkoren tarwebloem en het boekweitmeel toe en zeef tweemaal
   grondig door elkaar.

   _Waarom:_ de 60/25/14-verhouding levert circa 5.7% vezels en 12.7% eiwit op de droge mix; het
   actieve gerstemoutmeel (1%) zet tijdens 15-20 minuten beslagrust een deel van het zetmeel om
   in maltose voor egale bruining.

## Iteratielog

### v1.0 - 2026-10-25

- Eerste versie, overgenomen uit een LLM-chat en omgezet naar dit formaat.
