---
kind: ingredient_family
category: condiment
calculators:
  - hydration
  - safety
---

# Water, zout en smaakmakers

Water, zouten, azijnen, geconcentreerde smaakmakers en bouillons.

<!-- culinaria:overview (generated - edits here are overwritten) -->
| Ingrediënt | Water (%) | Droge stof (%) | Koolhydraten (%) | Suikers (%) | Zuur (%) | Zout (%) | Bronstatus |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| **Water** | 100.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.00 | datasheet |
| **Zout** | 0.0 | 100.0 | 0.0 | 0.0 | 0.0 | 100.00 | datasheet |
| **Fijn zeezout** | 0.5 | 99.5 | 0.0 | 0.0 | 0.0 | 99.00 | database |
| **Appelciderazijn** | 94.0 | 6.0 | 0.9 | 0.4 | 5.0 | 0.00 | database |
| **Tomatenpuree** | 70.0 | 30.0 | 18.0 | 12.0 | 2.0* | 0.50 | database + unverified* |
| **Worcestershiresaus** | 68.0* | 32.0* | 27.0 | 22.0 | 3.5* | 2.90 | datasheet + unverified* |
| **Scherpe mosterd** | 65.0 | 35.0 | 5.0 | 2.0 | 3.5* | 5.50 | database + unverified* |
| **Bouillonblokjes** | 4.0* | 96.0* | 22.0* | 5.0* | - | 48.00* | unverified* |
| **Krachtige vleesbouillon** | 96.0* | 4.0* | 0.5* | 0.2* | - | 0.80* | unverified* |
| **Gedroogde crayfish** | 12.0* | 88.0* | 0.0* | 0.0* | - | 3.00* | unverified* |
<!-- /culinaria:overview -->

## Water

```yaml
water_pct: 100.0
solids_pct: 0.0
carbs_pct: 0.0
sugars_pct: 0.0
acidity_pct: 0.0
salt_pct: 0.0
source_type: datasheet
source: Zuiver water (H2O)
```

Vrije waterfase voor siropen, deeg en hydratatie.

## Zout

```yaml
aliases:
  - Keukenzout
  - NaCl
water_pct: 0.0
solids_pct: 100.0
carbs_pct: 0.0
sugars_pct: 0.0
acidity_pct: 0.0
salt_pct: 100.0
pac: 585
source_type: datasheet
source: Zuiver natriumchloride (M = 58.44 g/mol, dissociatie in 2 ionen)
```

Zuiver natriumchloride ($NaCl$). Heeft door dissociatie in $Na^+$ en $Cl^-$ bij een lage
molaire massa van 58.44 g/mol een zeer sterke vriespuntverlaging (PAC ~585 ten opzichte van
sacharose = 100).

## Fijn zeezout

```yaml
aliases:
  - Zeezout
water_pct: 0.5
solids_pct: 99.5
carbs_pct: 0.0
sugars_pct: 0.0
acidity_pct: 0.0
salt_pct: 99.0
pac: 580
source_type: database
source: Standaard droog fijn zeezout (~99% NaCl)
```

Fijn gemalen zeezout dat snel oplost in emulsies, koekdeeg en sorbetbases.

## Appelciderazijn

```yaml
aliases:
  - Appelazijn
water_pct: 94.0
solids_pct: 6.0
carbs_pct: 0.9
sugars_pct: 0.4
acidity_pct: 5.0
salt_pct: 0.0
source_type: database
source: Standaard appelciderazijn (5% azijnzuur)
```

Gefermenteerde appelazijn met 5% titreerbaar zuur (als azijnzuur).

## Tomatenpuree

```yaml
water_pct: 70.0
solids_pct: 30.0
carbs_pct: 18.0
sugars_pct: 12.0
protein_pct: 4.5
fat_pct: 0.5
acidity_pct: 2.0
salt_pct: 0.5
source_type: database
source: NEVO-online (RIVM) dubbel geconcentreerde tomatenpuree (28-30% droge stof)
unverified:
  - acidity_pct
```

Dubbel geconcentreerde tomatenpuree (28-30% droge stof).

## Worcestershiresaus

```yaml
water_pct: 68.0
solids_pct: 32.0
carbs_pct: 27.0
sugars_pct: 22.0
acidity_pct: 3.5
salt_pct: 2.9
source_type: datasheet
source: Lea & Perrins Worcestershire Sauce voedingstabel
unverified:
  - water_pct
  - solids_pct
  - acidity_pct
```

Gefermenteerde saus op basis van moutazijn, melasse, ansjovis en tamarinde.

## Scherpe mosterd

```yaml
aliases:
  - Dijonmosterd
water_pct: 65.0
solids_pct: 35.0
carbs_pct: 5.0
sugars_pct: 2.0
protein_pct: 7.0
fat_pct: 11.0
acidity_pct: 3.5
salt_pct: 5.5
source_type: database
source: NEVO-online (RIVM) Dijonmosterd
unverified:
  - acidity_pct
```

Gladde mosterd van bruine/zwarte mosterdzaadjes. De mucilage (slijmstoffen) en fosfolipiden uit
het mosterdzaad werken als emulgator in vinaigrettes en glazuren.

## Bouillonblokjes

```yaml
water_pct: 4.0
solids_pct: 96.0
carbs_pct: 22.0
sugars_pct: 5.0
protein_pct: 10.0
fat_pct: 12.0
salt_pct: 48.0
source_type: unverified
source: Richtwaarde geconcentreerd bouillonblokje (~48% zout)
```

Geconcentreerd droog bouillonblokje (kip of rund) met hoog zout- en glutamaatgehalte.

## Krachtige vleesbouillon

```yaml
water_pct: 96.0
solids_pct: 4.0
carbs_pct: 0.5
sugars_pct: 0.2
protein_pct: 2.5
fat_pct: 0.5
salt_pct: 0.8
source_type: unverified
source: Richtwaarde getrokken kippen- of runderbouillon (96% vrij water)
```

Getrokken vlees- of gevogeltebouillon; levert ~96% vrij water voor zetmeelgelatinisatie plus
opgeloste gelatine en nucleotiden (IMP).

## Gedroogde crayfish

```yaml
water_pct: 12.0
solids_pct: 88.0
carbs_pct: 0.0
sugars_pct: 0.0
protein_pct: 68.0
fat_pct: 6.0
salt_pct: 3.0
source_type: unverified
source: Richtwaarde gedroogde West-Afrikaanse rivierkreeftjes/garnalen
```

Gedroogde en gerookte zoetwatergarnalen/rivierkreeftjes, vermalen tot poeder als umami- en
aromabasis in West-Afrikaanse stoofgerechten.
