"""Builds frontend/src/data/impact.json from the raw snapshot in data/raw/.

Offline and deterministic: python3 -m pipeline.build
"""
import json
from pathlib import Path

from .footprint import production_kg_per_kg, scenario_kg_per_kg, tier
from .scenarios import (
    FAR, SHORT, confidence, domestic_volumes, import_scenarios, monthly_import_kg,
    apply_origin_ref, probabilities, recent_production_t, redistribute_hubs,
)

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUTPUT = ROOT / "frontend" / "src" / "data" / "impact.json"
EUFIC = ROOT / "eufic_seasonal_produce_matrix.json"

TRADE_FILES = {"DE": "comext_DE.json", "GB": "hmrc_GB.json"}
COUNTRY_LABELS = {"DE": ("Germany", "Deutschland"), "GB": ("United Kingdom", "Vereinigtes Königreich")}
DOMESTIC_KM = 250.0
MIN_MONTH_SHARE = 0.10  # hide item-months below 10% of an average month's volume
THIN_MONTH_SHARE = 0.25  # below this, the estimate is flagged low confidence
SOURCES = {
    "trade": "Eurostat Comext DS-045409 (DE), HMRC OTS (UK), monthly imports by origin, 2023-2025",
    "production": "Eurostat apro_cpsh1 harvested production (latest 3 years; UK ends 2019/2020)",
    "seasonality": "EUFIC seasonal produce matrix",
    "footprint": "Poore & Nemecek 2018 (via Our World in Data) category medians, adjusted; DEFRA/GLEC transport factors (approximate)",
    "footprintOrigin": "HESTIA aggregated data (hestia.earth), release 2026-03-10, where a real "
                        "per-origin-country value exists; Poore & Nemecek category median otherwise",
}


def _flag(code: str) -> str:
    code = "GB" if code == "GB" else code
    return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in code)


MAX_ORIGIN_ROWS = 3


def build_origin_breakdown(item: dict, country_code: str, dom_month: dict, imp_origin_parts: list,
                           domestic_km: float, cfg: dict, hestia: dict, portion: float, total_kg: float) -> list:
    """Per-origin-country footprint for one item/month: the top supplying
    countries (imports plus, if any, the country's own domestic production)
    each with their own kg CO2e/portion - not the single blended "top
    scenario" value, so e.g. Colombian vs. Costa Rican bananas show up as
    their own real numbers instead of one averaged-away figure."""
    rows: dict = {}  # origin -> {"kg": float, "co2Weighted": float}

    def add(origin: str, scenario: str, kg: float, transport_per_kg: float, storage: float = 0.0):
        if kg <= 0:
            return
        production = production_kg_per_kg(item, scenario, origin, hestia)
        row = rows.setdefault(origin, {"kg": 0.0, "co2Weighted": 0.0})
        row["kg"] += kg
        row["co2Weighted"] += kg * (production + transport_per_kg + storage)

    for origin, scenario, kg, transport_per_kg in imp_origin_parts:
        add(origin, scenario, kg, transport_per_kg)

    if dom_month:
        domestic_transport = domestic_km * cfg["transport"]["roadKgPerTkm"] * cfg["transport"]["roadDetour"] / 1000
        for scenario, kg in dom_month.items():
            storage = cfg["transport"]["storageKgPerKg"] if scenario == "domestic_stored" else 0.0
            add(country_code, scenario, kg, domestic_transport, storage)

    if total_kg <= 0 or not rows:
        return []
    ranked = sorted(rows.items(), key=lambda kv: -kv[1]["kg"])[:MAX_ORIGIN_ROWS]
    return [
        {
            "code": origin,
            "share": round(r["kg"] / total_kg, 3),
            "kgCo2ePerPortion": round((r["co2Weighted"] / r["kg"]) * portion, 3),
        }
        for origin, r in ranked
    ]


def build_country(code: str, cfg: dict, trade: dict, production: dict, origins: dict, eufic: dict,
                  ref: dict, hestia: dict) -> dict:
    importer = cfg["countries"][code]
    years = cfg["years"]
    portion = cfg["portionKg"]
    result = {str(m): {"vegetable": {}, "fruit": {}} for m in range(1, 13)}

    for item in cfg["items"]:
        eufic_key = item["eufic"].get(code)
        info = eufic.get(eufic_key, {}).get("countries", {}).get(code, {}) if eufic_key else {}
        fresh, stored = info.get("fresh", []), info.get("stored", [])
        total_t = recent_production_t(production.get(item["cropCode"], {})) if item["cropCode"] else 0.0
        glass_t = recent_production_t(production.get(item["glassCropCode"], {})) if item["glassCropCode"] else 0.0
        domestic = domestic_volumes(item, fresh, stored, total_t, glass_t)

        monthly = []
        for m in range(1, 13):
            imports = redistribute_hubs(
                monthly_import_kg(trade.get(item["id"], {}), m, years), item["hubReexport"])
            if item["originRef"] and code == "DE":
                imports = apply_origin_ref(
                    imports, monthly_import_kg(ref.get(item["id"], {}), m, years), origins)
            imp_vol, imp_tr, imp_origin_parts = import_scenarios(
                item, m, imports, origins, importer, m in fresh, cfg["transport"])
            vol = dict(domestic.get(m, {}))
            for s, v in imp_vol.items():
                vol[s] = vol.get(s, 0.0) + v
            unknown = sum(kg for o, kg in imports.items() if o not in origins)
            monthly.append((m, vol, imp_tr, imports, unknown, imp_origin_parts))

        avg_month = sum(sum(v.values()) for _, v, *_ in monthly) / 12
        if avg_month <= 0:
            continue

        for m, vol, imp_tr, imports, unknown, imp_origin_parts in monthly:
            total = sum(vol.values())
            if total < MIN_MONTH_SHARE * avg_month:
                continue
            probs = probabilities(vol)
            top = max(probs, key=probs.get)
            transport = DOMESTIC_KM * cfg["transport"]["roadKgPerTkm"] * cfg["transport"]["roadDetour"] / 1000 \
                if top.startswith("domestic") else imp_tr[top]
            # Best-guess origin for the winning scenario, to look up a real
            # per-country HESTIA production value instead of the flat
            # per-item constant: the country itself for domestic scenarios,
            # otherwise the single largest import origin this month.
            origin = code if top.startswith("domestic") else (
                max(imports, key=imports.get) if imports else None)
            kg_per_portion = scenario_kg_per_kg(item, top, transport, cfg["transport"], origin, hestia) * portion
            production_portion = production_kg_per_kg(item, top, origin, hestia) * portion
            storage_portion = cfg["transport"]["storageKgPerKg"] * portion if top == "domestic_stored" else 0.0
            transport_portion = transport * portion
            imp_total = sum(imports.values())
            conf = confidence(probs, total < THIN_MONTH_SHARE * avg_month,
                              unknown / imp_total if imp_total else 0.0)
            origin_breakdown = build_origin_breakdown(
                item, code, domestic.get(m, {}), imp_origin_parts, DOMESTIC_KM, cfg, hestia, portion, total)
            result[str(m)][item["category"]].setdefault(item["group"], []).append({
                "id": item["id"],
                "name": item["name"],
                "kgCo2ePerPortion": round(kg_per_portion, 3),
                "productionKgPerPortion": round(production_portion, 3),
                "transportKgPerPortion": round(transport_portion, 3),
                "storageKgPerPortion": round(storage_portion, 3),
                "tier": tier(kg_per_portion, cfg["tierThresholdsPerPortion"]),
                "scenario": top,
                "probShort": round(sum(p for s, p in probs.items() if s in SHORT), 3),
                "probFar": round(sum(p for s, p in probs.items() if s in FAR), 3),
                "confidence": conf,
                "mix": {s: round(p, 3) for s, p in sorted(probs.items(), key=lambda t: -t[1]) if p >= 0.01},
                "originBreakdown": origin_breakdown,
            })

    for month in result.values():
        for category, groups in cfg["groups"].items():
            month[category] = [
                {
                    "group": gid,
                    "label": {"en": en, "de": de},
                    "items": sorted(month[category].get(gid, []), key=lambda i: i["kgCo2ePerPortion"]),
                }
                for gid, en, de in groups
                if month[category].get(gid)
            ]
    return result


def validate(out: dict) -> None:
    for code, months in out["data"].items():
        assert set(months) == {str(m) for m in range(1, 13)}, code
        for month in months.values():
            for category in ("vegetable", "fruit"):
                for group in month[category]:
                    for i in group["items"]:
                        assert i["tier"] in ("low", "medium", "high"), i
                        assert i["kgCo2ePerPortion"] > 0, i
                        parts = i["productionKgPerPortion"] + i["transportKgPerPortion"] + i["storageKgPerPortion"]
                        assert abs(parts - i["kgCo2ePerPortion"]) < 0.01, i
                        assert 0 <= i["probShort"] <= 1 and 0 <= i["probFar"] <= 1, i
                        assert i["probShort"] + i["probFar"] <= 1.01, i
                        assert i["confidence"] in ("low", "medium", "high"), i
                        assert 1 <= len(i["originBreakdown"]) <= MAX_ORIGIN_ROWS, i
                        assert abs(sum(o["share"] for o in i["originBreakdown"])) <= 1.01, i
                        for o in i["originBreakdown"]:
                            assert o["kgCo2ePerPortion"] > 0, i


def build() -> dict:
    cfg = json.loads((ROOT / "data" / "items.json").read_text(encoding="utf-8"))
    origins = json.loads((ROOT / "data" / "origins.json").read_text(encoding="utf-8"))
    production = json.loads((RAW / "production.json").read_text(encoding="utf-8"))
    eufic = json.loads(EUFIC.read_text(encoding="utf-8"))["produce"]
    ref = json.loads((RAW / "comext_EU.json").read_text(encoding="utf-8"))
    hestia_path = RAW / "hestia_gwp100.json"
    hestia = json.loads(hestia_path.read_text(encoding="utf-8")) if hestia_path.exists() else {}
    data = {}
    for code, fname in TRADE_FILES.items():
        trade = json.loads((RAW / fname).read_text(encoding="utf-8"))
        data[code] = build_country(code, cfg, trade, production[code], origins, eufic, ref, hestia)
    out = {
        "countries": [
            {"code": c, "label": {"en": en, "de": de}, "flag": _flag(c)}
            for c, (en, de) in COUNTRY_LABELS.items()
        ],
        "tiers": cfg["tierThresholdsPerPortion"],
        "portionKg": cfg["portionKg"],
        "sources": SOURCES,
        "data": data,
    }
    validate(out)
    return out


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(build(), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
