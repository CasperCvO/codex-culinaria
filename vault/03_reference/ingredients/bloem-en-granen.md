---
kind: ingredient_family
category: flour
calculators:
  - dough
---

# Bloem en granen

Tarwebloem, pseudogranen en havervlokken voor patisserie en bakkerij. Alle meel- en
bloemsoorten met `role: flour` tellen mee wanneer een recept `basis: flour` gebruikt.

<!-- culinaria:overview (generated - edits here are overwritten) -->
| Ingrediënt | Rol | Droge stof (%) | Koolhydraten (%) | Eiwit (%) | Vet (%) | Vezels (%) | Asgehalte (%) | Gluten | Bronstatus |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- | :--- |
| **Zeeuwse bloem** | flour | 86.0* | 71.0 | 9.0 | 1.0 | 3.0 | 0.45* | weak | datasheet + unverified* |
| **T55 bloem** | flour | 86.0* | 72.0* | 11.0* | 1.2* | 3.0* | 0.55 | medium | datasheet + unverified* |
| **Boekweitmeel** | flour | 87.0* | 72.0 | 9.0 | 2.8 | 5.6 | - | none | database + unverified* |
| **Havervlokken** | grain | 89.0* | 60.7 | 12.8 | 7.3 | 7.3 | - | none | database + unverified* |
| **Patentbloem** | flour | 86.0* | 71.0 | 11.5 | 1.3 | 3.0 | 0.45* | medium | database + unverified* |
| **Volkoren tarwebloem** | flour | 86.5* | 60.0 | 12.5 | 2.2 | 11.0 | 1.60* | medium | database + unverified* |
| **Actief gerstemoutmeel** | flour | 92.0* | 72.0* | 11.0* | 2.0* | 5.0* | 1.50* | weak | unverified* |
| **Maïszetmeel** | flour | 88.0 | 87.0 | 0.3 | 0.1 | 0.5 | - | none | database |
<!-- /culinaria:overview -->

## Zeeuwse bloem

```yaml
role: flour
water_pct: 14.0
solids_pct: 86.0
carbs_pct: 71.0
sugars_pct: 1.0
protein_pct: 9.0
fat_pct: 1.0
saturated_fat_pct: 0.1
fiber_pct: 3.0
salt_pct: 0.0
ash_pct: 0.45
gluten: weak
source_type: datasheet
source: Molen Mulder Pot productblad Zeeuwse Bloem (71 g koolhydraten, 1 g vet, 3 g vezels) en NBC kennisbank (8-9% eiwit voor Zeeuwse bloem van zachte zeeklimaattarwe)
unverified:
  - water_pct
  - solids_pct
  - ash_pct
```

Bloem van zachte Nederlandse zeeklimaattarwe met laag eiwitgehalte (~8-9%) en korte, zwakke
glutenketens. Geeft minimale elasticiteit en daardoor een brosse, korte breuk in koekjes en
zanddeeg.

## T55 bloem

```yaml
aliases:
  - Franse bloem T55
  - Tarwebloem T55
role: flour
water_pct: 14.0
solids_pct: 86.0
carbs_pct: 72.0
sugars_pct: 1.2
protein_pct: 11.0
fat_pct: 1.2
saturated_fat_pct: 0.2
fiber_pct: 3.0
salt_pct: 0.0
ash_pct: 0.55
gluten: medium
source_type: datasheet
source: Franse maalnorm Type 55 (asgehalte 0.50-0.60% op droge stof); overige macronutriënten zijn richtwaarden en hangen af van de specifieke molen
unverified:
  - water_pct
  - solids_pct
  - carbs_pct
  - sugars_pct
  - protein_pct
  - fat_pct
  - saturated_fat_pct
  - fiber_pct
```

Franse standaardbloem met een wettelijk asgehalte van 0.50-0.60% op de droge stof en een
gematigd eiwitgehalte (~10.5-11.5%). Geeft in combinatie met zwakkere patisseriebloem extra
interne samenhang aan deeg zonder het taai te maken.

## Boekweitmeel

```yaml
aliases:
  - Boekweit meel
role: flour
water_pct: 13.0
solids_pct: 87.0
carbs_pct: 72.0
protein_pct: 9.0
fat_pct: 2.8
fiber_pct: 5.6
salt_pct: 0.0
gluten: none
source_type: database
source: "NEVO-online 2023/8.0 (RIVM, via Brood.net: 353 kcal, 72 g koolhydraten, 5.6 g vezels, 9.0 g eiwit, 2.8 g vet per 100 g)"
unverified:
  - water_pct
  - solids_pct
```

Meel van het pseudograan boekweit (*Fagopyrum esculentum*). Volledig vrij van gluten (bevat
voornamelijk globulinen en albuminen), maar rijk aan waterbindende pentosanen en zetmeel, en
geeft een nootachtig, aards aroma.

## Havervlokken

```yaml
aliases:
  - Grove havervlokken
  - Haverlokken
  - Havermout
role: grain
water_pct: 11.0
solids_pct: 89.0
carbs_pct: 60.7
sugars_pct: 2.0
protein_pct: 12.8
fat_pct: 7.3
saturated_fat_pct: 1.3
fiber_pct: 7.3
salt_pct: 0.02
gluten: none
source_type: database
source: "NEVO-online 2023/8.0 (RIVM, via Brood.net: 373 kcal, 60.7 g koolhydraten, 7.3 g vezels, 12.8 g eiwit, 7.3 g vet per 100 g)"
unverified:
  - water_pct
  - solids_pct
```

Geplette en gestoomde hele haverkorrels. Rijk aan oplosbare bèta-glucanen die tijdens een koude
deegrust vrij water binden. Droog roosteren op 160 °C vormt pyrazinen door Maillardreacties
tussen de havereiwitten en suikers.

## Patentbloem

```yaml
aliases:
  - Tarwebloem
  - Patent bloem
role: flour
water_pct: 14.0
solids_pct: 86.0
carbs_pct: 71.0
sugars_pct: 1.5
protein_pct: 11.5
fat_pct: 1.3
saturated_fat_pct: 0.3
fiber_pct: 3.0
salt_pct: 0.0
ash_pct: 0.45
gluten: medium
source_type: database
source: NEVO-online (RIVM) en NBC kennisbank "Patentbloem" (~11-12% eiwit, laag asgehalte uit de kern van het endosperm)
unverified:
  - water_pct
  - solids_pct
  - ash_pct
```

Fijn uitgemalen tarwebloem uit het binnenste van de meelkern met laag asgehalte (~0.40-0.50%)
en sterkere glutenkwaliteit (~11-12% eiwit) dan Zeeuwse bloem.

## Volkoren tarwebloem

```yaml
aliases:
  - Tarwe volkorenmeel
  - Volkorenbloem
  - Volkorenmeel
role: flour
water_pct: 13.5
solids_pct: 86.5
carbs_pct: 60.0
sugars_pct: 2.0
protein_pct: 12.5
fat_pct: 2.2
saturated_fat_pct: 0.4
fiber_pct: 11.0
salt_pct: 0.0
ash_pct: 1.60
gluten: medium
source_type: database
source: NEVO-online (RIVM) "Tarwemeel volkoren"
unverified:
  - water_pct
  - solids_pct
  - ash_pct
```

Volledig uitgemalen tarwekorrel inclusief zemel en kiem. De scherpe zemeldeeltjes en het hoge
vezelgehalte (~11%) verhogen de waterabsorptie maar onderbreken glutenstrengen fysiek.

## Actief gerstemoutmeel

```yaml
aliases:
  - Gerstemoutmeel actief
role: flour
water_pct: 8.0
solids_pct: 92.0
carbs_pct: 72.0
sugars_pct: 10.0
protein_pct: 11.0
fat_pct: 2.0
fiber_pct: 5.0
ash_pct: 1.50
gluten: weak
source_type: unverified
source: Richtwaarde diastatisch (enzymactief) licht gerstemoutmeel
```

Niet-geëest (diastatisch) gerstemoutmeel met actieve $\alpha$- en $\beta$-amylasen en proteasen.
Hydrolyseert tijdens de beslagrust beschadigd zetmeel naar maltose (sterkere Maillard- en
karamellisatiekleuring) en verlaagt de beslagviscositeit.

## Maïszetmeel

```yaml
aliases:
  - Maizena
role: flour
water_pct: 12.0
solids_pct: 88.0
carbs_pct: 87.0
sugars_pct: 0.0
protein_pct: 0.3
fat_pct: 0.1
fiber_pct: 0.5
salt_pct: 0.0
gluten: none
source_type: database
source: NEVO-online (RIVM) "Maïszetmeel"
```

Zuiver maisendospermzetmeel zonder gluten. Verlaagt in beslag het effectieve glutenaandeel en
vormt als droge coating rond vochtige vullingstukjes (zoals feta) een hydrofiele buffer.

