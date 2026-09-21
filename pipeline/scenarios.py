"""Imports + domestic supply -> monthly volume (kg) per supply scenario.

Scenarios:
  domestic_fresh    domestic field crop (or unheated glass) in its fresh season
  domestic_stored   domestic crop out of cold store
  domestic_heated   domestic glasshouse output outside the field season
  import_near       imports by road from Europe / Morocco / Turkey
  import_near_heated  nearby import from northern Europe outside the field
                    season (heated glasshouse; e.g. NL tomatoes in winter)
  import_far        overseas import by sea
  import_far_air    overseas import by air (item-specific share of far imports)
"""
from collections import defaultdict
from statistics import mean

from .footprint import haversine_km, transport_kg_per_kg

SHORT = ("domestic_fresh", "domestic_stored", "domestic_heated", "import_near", "import_near_heated")
FAR = ("import_far", "import_far_air")
FAR_DEFAULT_KM = 9000.0
HEATED_LAT = 47.0


def monthly_import_kg(per_origin: dict, month: int, years: list[int]) -> dict:
    """origin -> average kg imported in this calendar month across the years."""
    out = {}
    for origin, series in per_origin.items():
        vals = [series.get(f"{y}-{month:02d}", 0.0) for y in years]
        avg = mean(vals)
        if avg > 0:
            out[origin] = avg
    return out


def redistribute_hubs(imports: dict, hubs: list) -> dict:
    """Spread hub-country volume (re-exports) proportionally over the other origins.

    Comext reports intra-EU trade by country of dispatch, so e.g. bananas shipped
    via Rotterdam show up as Dutch. If nothing but hubs remain, keep them as is.
    """
    hub_kg = sum(kg for o, kg in imports.items() if o in hubs)
    rest = {o: kg for o, kg in imports.items() if o not in hubs}
    rest_kg = sum(rest.values())
    if not hubs or hub_kg == 0 or rest_kg == 0:
        return imports
    scale = (rest_kg + hub_kg) / rest_kg
    return {o: kg * scale for o, kg in rest.items()}


def apply_origin_ref(imports: dict, ref: dict, origins: dict) -> dict:
    """Replace dispatch-country origins with the true (extra-EU) origin mix.

    `ref` is the EU27-level import volume by origin for the month; only non-road
    (overseas) origins are kept. Scaled to the importer's total volume.
    """
    total = sum(imports.values())
    overseas = {o: kg for o, kg in ref.items() if origins.get(o, {}).get("mode") == "sea"}
    ref_total = sum(overseas.values())
    if total == 0 or ref_total == 0:
        return imports
    return {o: total * kg / ref_total for o, kg in overseas.items()}


def recent_production_t(series: dict, n: int = 3) -> float:
    """Mean of the latest n non-zero yearly values (tonnes); 0 if none."""
    vals = [v for _, v in sorted(series.items()) if v]
    return mean(vals[-n:]) if vals else 0.0


def domestic_volumes(item: dict, fresh: list, stored: list, total_t: float, glass_t: float) -> dict:
    """month -> {scenario: kg}. Annual output is spread evenly over the months it is sold."""
    total_t = max(total_t, glass_t)
    if total_t <= 0 or not (fresh or stored):
        return {}
    glass_share = glass_t / total_t
    field_kg = total_t * 1000 * (1 - glass_share)
    glass_kg = total_t * 1000 * glass_share
    avail = sorted(set(fresh) | set(stored))
    out = defaultdict(lambda: defaultdict(float))
    for m in avail:
        scen = "domestic_fresh" if m in fresh else "domestic_stored"
        out[m][scen] += field_kg / len(avail)
    glass_months = item["glassMonths"]
    for m in glass_months:
        scen = "domestic_fresh" if m in fresh else "domestic_heated"
        out[m][scen] += glass_kg / len(glass_months)
    return out


def import_scenarios(item: dict, month: int, imports: dict, origins: dict, importer: dict,
                     in_field_season: bool, transport_cfg: dict) -> tuple[dict, dict]:
    """Returns ({scenario: kg}, {scenario: kg transport per kg produce, volume-weighted})."""
    vol: dict = defaultdict(float)
    tr_weighted: dict = defaultdict(float)
    can_heat = item["productionHeatedKgPerKg"] is not None
    for origin, kg in imports.items():
        info = origins.get(origin)
        if info:
            dist = haversine_km(importer["lat"], importer["lon"], info["lat"], info["lon"])
            mode = info["mode"]
        else:
            dist, mode = FAR_DEFAULT_KM, "sea"
        if mode == "road":
            heated = can_heat and not in_field_season and info is not None and info["lat"] >= HEATED_LAT
            scen = "import_near_heated" if heated else "import_near"
            parts = [(scen, 1.0, transport_kg_per_kg(dist, "road", transport_cfg))]
        else:
            air = item["airShareFar"]
            parts = [
                ("import_far", 1 - air, transport_kg_per_kg(dist, "sea", transport_cfg)),
                ("import_far_air", air, transport_kg_per_kg(dist, "air", transport_cfg)),
            ]
        for scen, share, tr in parts:
            if share <= 0:
                continue
            vol[scen] += kg * share
            tr_weighted[scen] += kg * share * tr
    transport = {s: tr_weighted[s] / vol[s] for s in vol}
    return dict(vol), transport


def probabilities(volumes: dict) -> dict:
    total = sum(volumes.values())
    return {s: v / total for s, v in volumes.items()} if total > 0 else {}


def confidence(probs: dict, fallback: bool, unknown_origin_share: float) -> str:
    if not probs:
        return "low"
    top = max(probs.values())
    if fallback or top < 0.4 or unknown_origin_share > 0.2:
        return "low"
    return "high" if top >= 0.6 else "medium"
