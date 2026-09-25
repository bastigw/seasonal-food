"""Scenario -> kg CO2e per kg produce (production + transport [+ storage])."""
from math import asin, cos, radians, sin, sqrt

AIR_SCENARIOS = {"import_far_air"}


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = radians(lat1), radians(lat2)
    a = sin((p2 - p1) / 2) ** 2 + cos(p1) * cos(p2) * sin(radians(lon2 - lon1) / 2) ** 2
    return 2 * 6371.0 * asin(sqrt(a))


def transport_kg_per_kg(distance_km: float, mode: str, cfg: dict) -> float:
    """kg CO2e to move 1 kg produce; mode is road | sea | air."""
    factor = cfg[f"{mode}KgPerTkm"] * cfg[f"{mode}Detour"]
    return distance_km * factor / 1000.0


def production_with_source(item: dict, scenario: str, origin: str | None = None,
                           hestia: dict | None = None) -> tuple[float, str, str | None]:
    """Production-only footprint (no transport/storage) for one scenario, plus
    where the number came from: (kg CO2e/kg, source, proxy origin).

    Heated scenarios always use the item's flat heated constant: HESTIA's
    per-country aggregates don't distinguish heated glasshouse production
    from field/tunnel growing, so they can't isolate the heating effect the
    heated constant exists to capture. For unheated scenarios the tiers are:

    1. "country"  - a real HESTIA value for the origin country
    2. "proxy"    - the item's `hestiaProxy` maps the origin to a comparable
                    country that has a HESTIA value (e.g. Chile -> Peru for
                    avocado, where HESTIA's own Chile aggregate is too poor
                    to publish)
    3. "estimate" - the flat global `productionFieldKgPerKg` constant
    """
    heated = scenario in ("domestic_heated", "import_near_heated")
    if heated and item["productionHeatedKgPerKg"] is not None:
        return item["productionHeatedKgPerKg"], "estimate", None
    by_country = (hestia or {}).get(item["id"], {})
    if origin:
        override = by_country.get(origin)
        if override:
            return override["gwp100KgPerKg"], "country", None
        proxy = (item.get("hestiaProxy") or {}).get(origin)
        if proxy and by_country.get(proxy):
            return by_country[proxy]["gwp100KgPerKg"], "proxy", proxy
    return item["productionFieldKgPerKg"], "estimate", None


def production_kg_per_kg(item: dict, scenario: str, origin: str | None = None, hestia: dict | None = None) -> float:
    return production_with_source(item, scenario, origin, hestia)[0]


def scenario_kg_per_kg(item: dict, scenario: str, transport: float, cfg: dict,
                       origin: str | None = None, hestia: dict | None = None) -> float:
    total = production_kg_per_kg(item, scenario, origin, hestia) + transport
    if scenario == "domestic_stored":
        total += cfg["storageKgPerKg"]
    return total


def tier(kg_per_kg: float, thresholds: dict) -> str:
    if kg_per_kg <= thresholds["lowMax"]:
        return "low"
    if kg_per_kg <= thresholds["mediumMax"]:
        return "medium"
    return "high"
