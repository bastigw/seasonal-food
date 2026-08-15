<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.png" />
  <img src="assets/logo.png" alt="" width="64" height="64" />
</picture>

# Seasonal Food

A mobile-first webpage showing what fruit and vegetables are currently in
season (fresh and stored) in the UK and Germany, plus Italy and Spain
(major growers whose produce commonly ends up on UK and German shelves),
based on
[EUFIC](https://www.eufic.org/en/explore-seasonal-fruit-and-vegetables-in-europe)
data bundled in this repo (`eufic_seasonal_produce_matrix.json`).

Switch between countries with the tabs at the top and step through months
with the arrows, all client-side, no reloads. Produce is grouped into
grocery-style subcategories (Leafy Greens & Salad, Root & Tuber Vegetables,
Stone Fruit, Berries, etc. - see `app/produce_groups.py`), and each item is
tagged **early** / **peak** / **ending** based on where the month falls
within its contiguous in-season window for that country. Items in season
essentially year-round get no tag.

## Architecture

- `app/seasonal.py` and `app/produce_groups.py` hold the seasonality logic
  (pure Python, no dependencies).
- `scripts/generate_data.py` runs that logic for all 4 countries x all 12
  months and writes `frontend/src/data/seasonal.json`.
- `frontend/` is a Vite + Vue 3 + Tailwind CSS app. It imports that JSON at
  build time and bundles it in, so the shipped site is fully static: no
  backend, no API, no runtime environment variables.
- The `Dockerfile` is a 3-stage build: Python generates the data, Node
  builds the static site, and the final image is just `nginx:alpine`
  serving the result.

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
