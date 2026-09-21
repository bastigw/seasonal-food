# Climate Impact Refactor - Design

Date: 2026-09-21

## Goal

Turn the page from "what is in season" into "what is the climate impact of the
fruit and vegetables people typically buy in a supermarket, in this country,
this month". It must be glanceable: colour and sort order carry the message.

## Decisions

- Scope: ~30 everyday items, no exotics.
- Countries: Germany and UK only (pipeline built so more countries are config).
- Metric: climate only (kg CO2e), shown per 500 g portion. Water/land later.
- Shown footprint is that of the **most likely supply scenario**, not a weighted
  average. A likelihood indicator ("88% short travel") shows how certain that is.
- Data is a modelled estimate from published trade statistics, and the UI says so.
- Grouping: Vegetables = Fruiting veg, Roots & storage, Leafy & cabbages, Other.
  Fruit = Local & berries, Citrus & tropical, Other.
- Item display: coloured bar (tiers low/medium/high, fixed thresholds) with a
  small value at the end, sorted best to worst within each category.

## Supply scenarios

| Scenario | Travel |
|---|---|
| Domestic field, fresh | short |
| Domestic stored | short |
| Domestic heated greenhouse | short, high energy |
| Nearby import (EU/neighbours, road) | medium |
| Far import (overseas, sea) | long |
| Far import by air | long, very high |

"Short travel" probability = domestic + nearby scenarios.

## Architecture

The app stays fully static; the pipeline runs at build time and writes JSON.

```
data/raw/               cached downloads
data/items.yaml         curated items: CN/HS codes, category, production
                        footprints, greenhouse share, tier thresholds, air list
data/distances.csv      origin -> DE / UK distance and typical mode
pipeline/
  sources/comext.py     Eurostat monthly imports by origin (DE)
  sources/hmrc.py       HMRC monthly imports by origin (UK)
  sources/production.py domestic annual production + EUFIC seasonality
                        -> monthly domestic supply
  scenarios.py          imports + domestic supply -> probability per scenario
  footprint.py          scenario -> kg CO2e/kg (production + transport)
  build.py              writes frontend/src/data/impact.json
```

Existing `app/seasonal.py` logic becomes an input to the pipeline. The old
seasonal UI and data are removed once the new page works.

### Scenario computation
For each item x country x month:
1. Group imports by origin into nearby / far-sea / air using the distance table
   and mode rules (air only for a documented list, or Comext mode data if it
   covers the items - to be verified).
2. Split domestic supply into field-fresh / stored / heated using the EUFIC
   window for the month plus the greenhouse share.
3. Normalise to probabilities; top scenario supplies the footprint.

Output per item/country/month:
`{ topScenario, kgCO2ePerPortion, tier, probShort, probFar, confidence }`

### Footprint
Production (per-item value from Poore & Nemecek / Agribalyse, with heated
greenhouse override) plus transport (distance x mode factor, DEFRA/GLEC).
Thresholds are fixed in `items.yaml`, not relative to the month.

## Data sources

- Imports by origin/month: Eurostat Comext (DE), HMRC trade data (UK)
- Domestic production: Eurostat annual, spread by EUFIC windows (a proxy)
- Greenhouse share: published studies / national statistics for a few items
- Production footprints: Poore & Nemecek (Our World in Data), Agribalyse
- Transport factors: DEFRA/GLEC conversion factors

Every item's JSON carries its source references.

## Frontend

- Tabs: DE and UK. Month switcher and DE/EN toggle unchanged.
- Two groups (Vegetables, Fruit) with the categories above.
- Row: name, bar (CO2e per 500 g), small value, compact "88% short" likelihood.
- Low-confidence rows get a subtle "rough estimate" marker.
- Optional tap-to-expand detail (scenario breakdown, sources); not required
  for the first version.
- Short disclaimer under the title: estimates from trade statistics.

## Error handling

- No usable trade data for a month: fall back to the item's annual average and
  flag the month low confidence. Never fill silently.
- Source download failure: fail the build; no stale or partial data shipped.
- Confidence derives from share of trade volume matched to an origin and the
  margin of the top scenario.

## Testing

- Unit tests for `scenarios.py` and `footprint.py` with hand-made fixtures
  (probabilities sum to 1, top scenario correct, tiers respect thresholds).
- Golden test on 2-3 items (e.g. German tomato Feb vs Aug) for month-effect
  direction.
- JSON schema check at end of build.
- Light frontend component test for row rendering and sort order.

## Out of scope

Other countries, water/land metrics, swap suggestions. Design leaves room.

## Open item

First implementation step is a feasibility check of Comext and HMRC downloads
(and Comext transport-mode coverage) for ~5 items before building the full
pipeline.

## Implementation notes (deviations from the design above)

- `data/items.yaml` is `data/items.json` (stdlib only, no YAML dependency);
  distances are computed from coordinates in `data/origins.json`.
- Raw downloads are a committed snapshot in `data/raw/`; `pipeline/fetch.py`
  refreshes it, `pipeline/build.py` is offline.
- Added scenario `import_near_heated` (northern-European import outside the
  field season, e.g. Dutch winter tomatoes).
- Comext reports intra-EU trade by dispatch country, so re-export hubs are
  redistributed (`hubReexport`) or replaced by the EU27 extra-EU origin mix
  (`originRef`, banana/pineapple/avocado).
- Comext transport-mode data is not available through the API; air freight
  uses a per-item share (`airShareFar`).
- Old `app/` and `scripts/` seasonal code removed; EUFIC JSON is read
  directly by the pipeline.
