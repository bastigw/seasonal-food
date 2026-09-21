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


def production_kg_per_kg(item: dict, scenario: str) -> float:
    heated = scenario in ("domestic_heated", "import_near_heated")
    if heated and item["productionHeatedKgPerKg"] is not None:
        return item["productionHeatedKgPerKg"]
    return item["productionFieldKgPerKg"]


def scenario_kg_per_kg(item: dict, scenario: str, transport: float, cfg: dict) -> float:
    total = production_kg_per_kg(item, scenario) + transport
    if scenario == "domestic_stored":
        total += cfg["storageKgPerKg"]
    return total


def tier(kg_per_portion: float, thresholds: dict) -> str:
    if kg_per_portion <= thresholds["lowMax"]:
        return "low"
    if kg_per_portion <= thresholds["mediumMax"]:
        return "medium"
    return "high"
