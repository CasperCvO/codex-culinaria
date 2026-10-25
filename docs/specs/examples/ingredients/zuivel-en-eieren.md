---
kind: ingredient_family
category: dairy
calculators:
  - ice_cream
  - dough
---

# Zuivel en eieren

Melkproducten, boter en eieren voor ijs (melkvet, vetvrije droge melkstof / MSNF en lactose
voor vriespuntberekening) en patisserie (waterfase en emulgering).

<!-- culinaria:overview (generated - edits here are overwritten) -->
| Ingrediënt | Water (%) | Droge stof (%) | Vet (%) | MSNF (%) | Lactose (%) | Eiwit (%) | Bronstatus |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| **Volle melk** | 87.6 | 12.4 | 3.4 | 9.0 | 4.5 | 3.3 | database |
| **Halfvolle melk** | 89.4 | 10.6 | 1.5 | 9.1 | 4.7 | 3.4 | database |
| **Slagroom 35%** | 58.8 | 41.2 | 35.3 | 5.9 | 3.0 | 2.3 | database |
| **Magere melkpoeder** | 4.0 | 96.0 | 0.5 | 95.5 | 52.0 | 36.0 | datasheet |
| ↳ Mattisson Magere Melkpoeder Biologisch | 4.0 | 96.0 | 0.5 | 95.5 | 52.0 | 36.0 | datasheet |
| **Roomboter** | 16.0 | 84.0 | 82.0 | 2.0 | 0.7 | 0.7 | database |
| **Heel ei** | 76.1 | 23.9 | 9.1 | - | - | 12.3 | database |
| **Eidooier** | 50.8 | 49.2 | 32.0 | - | - | 16.2 | database |
<!-- /culinaria:overview -->

## Volle melk

```yaml
water_pct: 87.6
solids_pct: 12.4
carbs_pct: 4.5
sugars_pct: 4.5
lactose_pct: 4.5
protein_pct: 3.3
fat_pct: 3.4
saturated_fat_pct: 2.2
msnf_pct: 9.0
salt_pct: 0.11
source_type: database
source: NEVO-online (RIVM) code 279 "Melk volle"
```

Standaard gehomogeniseerde en gepasteuriseerde koemelk. Het lactose-aandeel heeft een PAC van
100 (gelijk aan sacharose, M = 342.3 g/mol) en telt volledig mee in de vriespuntberekening van
roomijs.

## Halfvolle melk

```yaml
water_pct: 89.4
solids_pct: 10.6
carbs_pct: 4.7
sugars_pct: 4.7
lactose_pct: 4.7
protein_pct: 3.4
fat_pct: 1.5
saturated_fat_pct: 0.9
msnf_pct: 9.1
salt_pct: 0.11
source_type: database
source: NEVO-online (RIVM) code 286 "Melk halfvolle"
```

Koemelk gestandaardiseerd op 1.5% melkvet; levert iets meer water en vrijwel dezelfde vetvrije
droge melkstof (MSNF) als volle melk.

## Slagroom 35%

```yaml
aliases:
  - Slagroom
  - Ongeklopte slagroom
water_pct: 58.8
solids_pct: 41.2
carbs_pct: 3.0
sugars_pct: 3.0
lactose_pct: 3.0
protein_pct: 2.3
fat_pct: 35.3
saturated_fat_pct: 24.0
msnf_pct: 5.9
salt_pct: 0.1
source_type: database
source: NEVO-online 2025/9.0 (RIVM) code 299 "Room slag- onbereid" (58.8 g water, 35.3 g vet, 2.3 g eiwit) en AH/Melkan etiket (3.0 g suikers, 24 g verzadigd vet)
```

Primaire bron van melkvet in roomijs. Tijdens de koude rijping (2-4 °C) kristalliseert een deel
van het melkvet in de vetbolletjes, wat bij het draaien zorgt voor gecontroleerde partiële
coalescentie rond ingeslagen luchtbellen.

## Magere melkpoeder

```yaml
aliases:
  - Mageremelkpoeder
  - SMP
water_pct: 4.0
solids_pct: 96.0
carbs_pct: 52.0
sugars_pct: 52.0
lactose_pct: 52.0
protein_pct: 36.0
fat_pct: 0.5
saturated_fat_pct: 0.3
msnf_pct: 95.5
salt_pct: 1.0
source_type: datasheet
source: "Mattisson productblad MT2801 (mattisson.nl/biologische-magere-melkpoeder: 0.5 g vet, 52 g koolhydraten/suikers, 36 g eiwit, 1.0 g zout per 100 g)"
```

Gesproeidroogde magere melk. Verhoogt in roomijs het gehalte aan vetvrije droge melkstof (MSNF)
en eiwit zonder extra water toe te voegen. Boven circa 10-11% totale MSNF in een ijsmix (of
meer dan ~6 g lactose per 100 g vrij water) dreigt bij -18 °C uitkristallisatie van lactose
(zanderig mondgevoel).

### Mattisson Magere Melkpoeder Biologisch

```yaml
aliases:
  - Magere melkpoeder (Mattisson)
brand: Mattisson
source_type: datasheet
source: Mattisson productblad MT2801 (mattisson.nl/biologische-magere-melkpoeder)
```

## Roomboter

```yaml
aliases:
  - Ongezouten roomboter
  - Boter
water_pct: 16.0
solids_pct: 84.0
carbs_pct: 0.7
sugars_pct: 0.7
lactose_pct: 0.7
protein_pct: 0.7
fat_pct: 82.0
saturated_fat_pct: 53.4
msnf_pct: 2.0
salt_pct: 0.01
source_type: database
source: EU-verordening 1308/2013 voor ongezouten roomboter (82.0% melkvet, 16.0% water, 2.0% MSNF) en NEVO-online code 310 "Boter ongezouten" (0.7 g eiwit, 53.4 g verzadigd vet)
```

Water-in-olie-emulsie met 82% melkvet en circa 16% vrij water. In deeg levert dat vrije water
het oplosmiddel waarin suikers deels oplossen en het zetmeel tijdens een koude rustfase
hydrateert.

## Heel ei

```yaml
aliases:
  - Ei
  - Kippenei
water_pct: 76.1
solids_pct: 23.9
carbs_pct: 0.2
sugars_pct: 0.2
protein_pct: 12.3
fat_pct: 9.1
saturated_fat_pct: 2.9
salt_pct: 0.35
source_type: database
source: NEVO-online (RIVM) code 83 "Kippenei rauw"
```

Gemiddeld kippenei zonder schaal (~50-60 g eetbaar deel per ei: circa twee derde ei-eiwit en
een derde eidooier).

## Eidooier

```yaml
aliases:
  - Eierdooiers
  - Eigeel
water_pct: 50.8
solids_pct: 49.2
carbs_pct: 0.0
sugars_pct: 0.0
protein_pct: 16.2
fat_pct: 32.0
saturated_fat_pct: 8.0
salt_pct: 0.13
source_type: database
source: NEVO-online (RIVM) code 85 "Eidooier rauw" en Voedingswaardetabel.nl (50.8 g water, 16.2 g eiwit, 32.0 g vet)
```

Bevat ~9-10% fosfolipiden (waaronder lecithine) en lipoproteïnen (LDL) die vet- en waterfasen
emulgeren in deeg en anglaise-ijsbases. Coaguleert in een anglaise met suiker en melk rond
82-84 °C.
