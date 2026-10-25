---
kind: ingredient_family
category: sugar
calculators:
  - ice_cream
  - dough
---

# Suikers

Suikers en gedehydrateerde glucosestropen voor ijs (vriespuntverlaging en zoetkracht),
patisserie (hygroscopiciteit, Maillard- en karamellisatiereacties) en confiserie.

_Referentie: sacharose (kristalsuiker) heeft per definitie PAC = 100 en POD = 100. Voor
samengestelde suikers (zoals basterdsuiker) berekent de calculator PAC en POD uit de
sacharose- en invertsuikerfractie._

<!-- culinaria:overview (generated - edits here are overwritten) -->
| Ingrediënt | Droge stof (%) | Koolhydraten (%) | Suikers (%) | Sacharose (%) | Invertsuiker (%) | PAC | POD | DE | Bronstatus |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| **Kristalsuiker** | 100.0 | 100.0 | 100.0 | 100.0 | 0.0 | 100 | 100 | - | datasheet |
| **Dextrose** | 92.0 | 92.0 | 92.0 | 0.0 | 0.0 | 172 | 74 | 100 | datasheet |
| ↳ Dextrose (Sosa) | 92.0 | 92.0 | 92.0 | 0.0 | 0.0 | 172 | 74 | 100 | datasheet |
| **Glucosepoeder 33DE** | 94.0 | 94.0 | - | 0.0 | 0.0 | 56 | 24 | 33 | datasheet |
| ↳ Glucosepoeder 33DE (Sosa) | 94.0 | 94.0 | - | 0.0 | 0.0 | 56 | 24 | 33 | datasheet |
| **Witte basterdsuiker** | 99.0 | 99.0 | 99.0 | 97.0 | 1.1 | - | - | - | datasheet |
| **Bruine basterdsuiker** | 99.0 | 99.0 | 99.0 | 97.2 | 2.0 | - | - | - | datasheet |
| **Donkere basterdsuiker** | 98.0 | 98.0 | 98.0 | 95.0 | 1.5 | - | - | - | datasheet |
<!-- /culinaria:overview -->

## Kristalsuiker

```yaml
aliases:
  - Fijne kristalsuiker
  - Suiker
  - Sacharose
  - Tafelsuiker
water_pct: 0.0
solids_pct: 100.0
carbs_pct: 100.0
sugars_pct: 100.0
sucrose_pct: 100.0
invert_sugar_pct: 0.0
protein_pct: 0.0
fat_pct: 0.0
pac: 100
pod: 100
source_type: datasheet
source: Stoichiometrische referentie (zuivere sacharose, M = 342.3 g/mol)
```

Zuivere sacharose (disacharide van glucose en fructose). Dient als het 100/100-ankerpunt voor
vriespuntverlaging (PAC) en relatieve zoetkracht (POD). In droge karamel smelt sacharose rond
160 °C en ontleedt daarbij thermisch tot vluchtige en bruine karamelpolymeren.

## Dextrose

```yaml
aliases:
  - Druivensuiker
  - D-glucose monohydraat
water_pct: 8.0
solids_pct: 92.0
carbs_pct: 92.0
sugars_pct: 92.0
sucrose_pct: 0.0
invert_sugar_pct: 0.0
protein_pct: 0.0
fat_pct: 0.0
pac: 172
pod: 74
de: 100
source_type: datasheet
source: "Sosa technisch productblad Dextrose ref. 48684 / 41519 (sosa.cat/en/product/dextrose/: Solids 92%, PAC 172%, POD 74%)"
```

Kristallijn D-glucose monohydraat (~8% kristalwater, M = 180.16 g/mol watervrij). Omdat het
molecuulgewicht bijna de helft is van sacharose, levert 1 g dextrose veel meer opgeloste
deeltjes dan sacharose (PAC 172 op productgewicht) bij een mildere zoetheid (POD 74). Wordt in
ijs en sorbet gebruikt om het vriespunt te verlagen zonder de zoetheid op te drijven.

### Dextrose (Sosa)

```yaml
brand: Sosa
source_type: datasheet
source: Sosa technisch productblad Dextrose ref. 48684 / 41519 (sosa.cat/en/product/dextrose/)
```

## Glucosepoeder 33DE

```yaml
aliases:
  - Gedehydrateerde glucosestroop 33DE
  - Glucose 33DE
water_pct: 6.0
solids_pct: 94.0
carbs_pct: 94.0
sucrose_pct: 0.0
invert_sugar_pct: 0.0
protein_pct: 0.0
fat_pct: 0.0
pac: 56
pod: 24
de: 33
source_type: datasheet
source: "Sosa technisch productblad Powdered Glucose DE33 ref. 50053 / 41434 (sosa.cat/en/product/powdered-glucose-de33/: Solids 94%, PAC 56%, POD 24%, pH 4.5-5.5)"
```

Geatomiseerde (gesproeidroogde) glucosestroop verkregen door partiële hydrolyse van maïszetmeel
tot een Dextrose Equivalent van 33. Bevat een hoog aandeel langere oligosachariden en
maltodextrinen: levert daardoor veel droge stof (94%) en viscositeit in de serumfase bij een
lage zoetkracht (POD 24) en gematigde vriespuntverlaging (PAC 56). Remt rekristallisatie van
sacharose en verhoogt het mondgevoel in sorbets, roomijs en ganaches. Volgens Sosa vervangt
75 g glucosepoeder 100 g vloeibare glucosestroop.

### Glucosepoeder 33DE (Sosa)

```yaml
brand: Sosa
source_type: datasheet
source: Sosa technisch productblad Powdered Glucose DE33 ref. 50053 / 41434 (sosa.cat/en/product/powdered-glucose-de33/)
```

## Witte basterdsuiker

```yaml
aliases:
  - Blanke basterdsuiker
water_pct: 1.0
solids_pct: 99.0
carbs_pct: 99.0
sugars_pct: 99.0
sucrose_pct: 97.0
invert_sugar_pct: 1.1
protein_pct: 0.0
fat_pct: 0.0
salt_pct: 0.0
source_type: datasheet
source: Cosun Beet Company specificatie Basterdsuiker Blank (97% sacharose, 0.5-1.6% invertsuiker, korrel 0.2-0.4 mm) en Van Gilse PS in foodservice PSID 19937 (99 g koolhydraten/suikers per 100 g)
```

Fijn gezeefde kristalsuiker (0.2-0.4 mm) gecoat met een dunne film invertsuikerstroop. Lost in
deeg en beslag sneller op dan gewone kristalsuiker en houdt gebak langer mals door de
hygroscopische werking van de fructose in de invertsuikerlaag.

## Bruine basterdsuiker

```yaml
aliases:
  - Lichtbruine basterdsuiker
  - Gele basterdsuiker
water_pct: 1.0
solids_pct: 99.0
carbs_pct: 99.0
sugars_pct: 99.0
sucrose_pct: 97.2
invert_sugar_pct: 2.0
protein_pct: 0.0
fat_pct: 0.0
salt_pct: 0.0
source_type: datasheet
source: Cosun Beet Company specificatie Basterdsuiker Geel (97.2% sacharose, 1.5-2.5% invertsuiker, korrel 0.2-0.4 mm)
```

Fijn gezeefde kristalsuiker verrijkt met invertsuikerstroop en gekaramelliseerde suikerstroop.

## Donkere basterdsuiker

```yaml
aliases:
  - Donkerbruine basterdsuiker
  - Basterdsuiker donker
water_pct: 2.0
solids_pct: 98.0
carbs_pct: 98.0
sugars_pct: 98.0
sucrose_pct: 95.0
invert_sugar_pct: 1.5
protein_pct: 0.0
fat_pct: 0.0
salt_pct: 0.05
source_type: datasheet
source: Cosun Beet Company specificatie Basterdsuiker Donker (95% sacharose, 0.5-2.0% invertsuiker, korrel 0.5-0.9 mm) en Van Gilse PS in foodservice PSID 1291010 (98 g koolhydraten/suikers, 0.05 g zout per 100 g)
```

Basterdsuiker met een hoger aandeel invertsuikerstroop en karamel. De reducerende monosachariden
(glucose en fructose) versnellen zowel Maillardreacties als bruinkleuring tijdens het bakken en
houden koekdeeg zacht en smeuïg.
