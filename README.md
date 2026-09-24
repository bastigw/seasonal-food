<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.png" />
  <img src="assets/logo.png" alt="" width="64" height="64" />
</picture>

# Climate Impact of Produce

A mobile-first webpage showing the estimated climate impact (kg CO2e per
500 g) of the fruit and vegetables people typically buy in a supermarket,
for **Germany** and the **UK**, month by month. Each item shows a coloured
bar (green / amber / red) for the footprint of its **most likely supply
route** that month, plus how likely it is to have travelled a short or a
long way. Everyday items only (~30), grouped into a few broad categories,
sorted best to worst.

The numbers are a **modelled estimate from trade statistics, not a
measurement**.

## How the numbers are made

For each item x country x month the pipeline estimates the mix of supply
scenarios (domestic field / stored / heated glasshouse, nearby import,
overseas by sea, overseas by air) and reports the footprint of the most
likely one:

- **Imports by origin and month:** Eurostat Comext (DE) and HMRC OTS (UK),
  2023-2025 average. Intra-EU trade is recorded by country of dispatch, so
  re-export hubs (NL/BE) are handled explicitly - see `hubReexport` /
  `originRef` in `data/items.json`.
- **Domestic supply:** Eurostat annual production (incl. "under glass"),
  spread over the months the EUFIC seasonality matrix says the item is
  sold. Glasshouse output outside the field season counts as heated.
- **Footprint:** production value plus transport (distance x mode factor,
  DEFRA/GLEC-style). Production uses a real per-origin-country value from
  [HESTIA](https://www.hestia.earth) aggregated data when the item's
  dominant import origin that month has one (unheated scenarios only -
  HESTIA doesn't distinguish heated glasshouse production); otherwise it
  falls back to a flat per-item value (approximate, after Poore & Nemecek
  2018 via Our World in Data). Air-freight shares, glasshouse months and
  the flat production values are assumptions in `data/items.json` and
  should be reviewed before quoting single numbers.

Known limitations: exports of domestic produce are ignored; UK production
data ends 2019/2020; Comext has no transport-mode data, so air freight is
an explicit per-item assumption.

## Architecture

- `data/items.json` - curated items, footprints, thresholds, transport
  factors. `data/origins.json` - origin coordinates and road/sea mode.
- `data/raw/` - committed snapshot of the downloaded trade, production and
  HESTIA emissions data. Refresh with `python3 -m pipeline.fetch` (needs
  network; the HESTIA job additionally needs `pip install duckdb` to read
  the Parquet file it downloads - fetch-time only, not needed to build).
- `pipeline/` - pure-Python (stdlib only) model: `scenarios.py`,
  `footprint.py`, `build.py` (offline; writes
  `frontend/src/data/impact.json`). Tests: `python3 -m unittest discover
  -s pipeline/tests -t .`
- `frontend/` - Vite + Vue 3 + Tailwind CSS. The JSON is bundled at build
  time, so the shipped site is fully static.
- `Dockerfile` - 3 stages: Python runs the tests and builds the data, Node
  builds the site, `nginx:alpine` serves it.

## Deploying with Portainer (no registry, just GitHub)

Portainer can build the image itself from a Dockerfile in a Git
repository, so nothing needs to be pushed to Docker Hub or any other
registry.

1. Push this repo to GitHub.
2. In Portainer: **Stacks -> Add stack -> Repository**.
3. Set the repository URL to your GitHub repo (and branch, e.g. `main`).
   Compose path defaults to `docker-compose.yml`, which is correct here.
4. Deploy the stack. Portainer clones the repo, runs `docker build`, and
   starts the container, all on your host, no external registry involved.
   No environment variables to configure.
5. Visit `http://<host>:8080` (or whichever port you mapped) from your
   phone on the same network.
6. To pick up future changes (e.g. an updated data file), use Portainer's
   "Pull and redeploy" / "Update the stack" action, which re-clones and
   rebuilds.

## Local development

Requires Python 3.12+ (standard library only, no venv needed) and Node 20+.

```bash
cd frontend
npm install
npm run generate-data   # builds src/data/seasonal.json from the Python logic
npm run dev             # opens on http://localhost:5173, hot reload
```

Re-run `npm run generate-data` any time you edit
`eufic_seasonal_produce_matrix.json`, `app/seasonal.py`, or
`app/produce_groups.py`.

### Test the full container build locally

```bash
docker compose up --build
```

Visit `http://localhost:8080`.

## Updating the seasonal data

Replace `eufic_seasonal_produce_matrix.json`, commit, push to GitHub, then
redeploy the stack in Portainer to rebuild the image with the new data.
