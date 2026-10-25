---
kind: ingredient_family
category: grain
calculators:
  - hydration
---

# Rijst

Rijstsoorten, zetmeelprofielen en hydratatieratio's (massa droge rijst : massa totaal vrij
vocht) voor koken en gesloten stoomgelatinisatie.

<!-- culinaria:overview (generated - edits here are overwritten) -->
| Ingrediënt | Droge stof (%) | Koolhydraten (%) | Eiwit (%) | Vet (%) | Amylose (%) | Hydratatie | Stoomtijd (min) | Bronstatus |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| **Basmatirijst** | 88.0 | 77.7 | 7.8 | 0.8 | 22.0* | 1.15* | 15* | datasheet + unverified* |
| ↳ Rahman Superbasmati | 88.0 | 77.7 | 7.8 | 0.8 | 22.0* | 1.10* | 14-16* | unverified* |
| ↳ Tilda Pure Basmati | 88.0 | 77.7 | 7.8 | 0.8 | 22.0* | 1.15* | 15* | datasheet + unverified* |
| **Langkorrelige parboiled rijst** | 88.0 | 78.6 | 7.9 | 0.7 | 22.0* | 1.50* | 25* | datasheet + unverified* |
| ↳ Golden Sella Basmati | 88.0 | 78.6 | 7.9 | 0.7 | 22.0* | 1.50* | 25* | datasheet + unverified* |
<!-- /culinaria:overview -->

## Basmatirijst

```yaml
aliases:
  - Witte basmatirijst
  - Basmati
water_pct: 12.0
solids_pct: 88.0
carbs_pct: 77.7
sugars_pct: 0.5
protein_pct: 7.8
fat_pct: 0.8
saturated_fat_pct: 0.2
fiber_pct: 1.0
salt_pct: 0.01
amylose_pct: 22.0
hydration_ratio: 1.15
steaming_min: 15
source_type: datasheet
source: Tilda Pure Basmati voedingstabel (tilda.com/products/pure-basmati-rice/); vocht 12% volgens USDA FoodData Central
unverified:
  - amylose_pct
  - hydration_ratio
  - steaming_min
```

Langkorrelige, gerijpte (aged) aromatische rijst met een hoog amylosegehalte (~20-25%). Door de
lineaire amyloseketens blijven de korrels na het garen droog en los van elkaar, maar eenmaal
gehydrateerd heeft de onbehandelde korrel een beperkte mechanische en thermische weerstand.

### Rahman Superbasmati

```yaml
brand: Rahman
hydration_ratio: 1.10
steaming_min: [14, 16]
source_type: unverified
source: LLM-chat (data_examples/Jollof.md), nog niet gemeten
```

Extra lange, gerijpte superbasmatikorrel met lage structurele weerstand tegen overhydratatie en
roeren. Wassen in lauwwarm water tot het spoelwater helder is, niet weken, en 15 minuten laten
uitlekken op een fijne zeef.

### Tilda Pure Basmati

```yaml
brand: Tilda
source_type: datasheet
source: Tilda Pure Basmati voedingstabel (tilda.com/products/pure-basmati-rice/)
```

Iets kortere en mechanisch iets stabielere korrel dan superbasmati.

## Langkorrelige parboiled rijst

```yaml
aliases:
  - Parboiled basmatirijst
  - Sella basmati
  - Parboiled rijst
water_pct: 12.0
solids_pct: 88.0
carbs_pct: 78.6
sugars_pct: 0.7
protein_pct: 7.9
fat_pct: 0.7
saturated_fat_pct: 0.2
fiber_pct: 1.2
salt_pct: 0.01
amylose_pct: 22.0
hydration_ratio: 1.50
steaming_min: 25
source_type: datasheet
source: Tilda Golden Sella Basmati voedingstabel (tilda.com/products/golden-sella-basmati-rice/)
unverified:
  - amylose_pct
  - hydration_ratio
  - steaming_min
```

Rijst die in het ongeschilde vlies onder stoomdruk is voorgegelatiniseerd en daarna gedroogd.
De retrogradatie van het zetmeel tijdens het drogen vormt een stevig, hittebestendig netwerk
waardoor de korrel aanzienlijk meer vloeistof en langere stoomtijden verdraagt zonder open te
barsten of papperig te worden.

### Golden Sella Basmati

```yaml
brand: Tilda
source_type: datasheet
source: Tilda Golden Sella Basmati voedingstabel (tilda.com/products/golden-sella-basmati-rice/)
```

Goudgele parboiled basmati.
