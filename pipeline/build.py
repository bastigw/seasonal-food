"""Builds frontend/src/data/impact.json from the raw snapshot in data/raw/.

Offline and deterministic: python3 -m pipeline.build
"""
import json
from pathlib import Path

from .footprint import scenario_kg_per_kg, tier
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
}


def _flag(code: str) -> str:
    code = "GB" if code == "GB" else code
    return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in code)


def build_country(code: str, cfg: dict, trade: dict, production: dict, origins: dict, eufic: dict,
                  ref: dict) -> dict:
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
            imp_vol, imp_tr = import_scenarios(item, m, imports, origins, importer, m in fresh, cfg["transport"])
            vol = dict(domestic.get(m, {}))
            for s, v in imp_vol.items():
                vol[s] = vol.get(s, 0.0) + v
            unknown = sum(kg for o, kg in imports.items() if o not in origins)
            monthly.append((m, vol, imp_tr, imports, unknown))

        avg_month = sum(sum(v.values()) for _, v, *_ in monthly) / 12
        if avg_month <= 0:
            continue

        for m, vol, imp_tr, imports, unknown in monthly:
            total = sum(vol.values())
            if total < MIN_MONTH_SHARE * avg_month:
                continue
            probs = probabilities(vol)
            top = max(probs, key=probs.get)
            transport = DOMESTIC_KM * cfg["transport"]["roadKgPerTkm"] * cfg["transport"]["roadDetour"] / 1000 \
                if top.startswith("domestic") else imp_tr[top]
            kg_per_portion = scenario_kg_per_kg(item, top, transport, cfg["transport"]) * portion
            imp_total = sum(imports.values())
            conf = confidence(probs, total < THIN_MONTH_SHARE * avg_month,
                              unknown / imp_total if imp_total else 0.0)
            result[str(m)][item["category"]].setdefault(item["group"], []).append({
                "id": item["id"],
                "name": item["name"],
                "kgCo2ePerPortion": round(kg_per_portion, 3),
                "tier": tier(kg_per_portion, cfg["tierThresholdsPerPortion"]),
                "scenario": top,
                "probShort": round(sum(p for s, p in probs.items() if s in SHORT), 3),
                "probFar": round(sum(p for s, p in probs.items() if s in FAR), 3),
                "confidence": conf,
                "mix": {s: round(p, 3) for s, p in sorted(probs.items(), key=lambda t: -t[1]) if p >= 0.01},
                "topOrigins": [o for o, _ in sorted(imports.items(), key=lambda t: -t[1])[:3]],
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
                        assert 0 <= i["probShort"] <= 1 and 0 <= i["probFar"] <= 1, i
                        assert i["probShort"] + i["probFar"] <= 1.01, i
                        assert i["confidence"] in ("low", "medium", "high"), i


def build() -> dict:
    cfg = json.loads((ROOT / "data" / "items.json").read_text(encoding="utf-8"))
    origins = json.loads((ROOT / "data" / "origins.json").read_text(encoding="utf-8"))
    production = json.loads((RAW / "production.json").read_text(encoding="utf-8"))
    eufic = json.loads(EUFIC.read_text(encoding="utf-8"))["produce"]
    ref = json.loads((RAW / "comext_EU.json").read_text(encoding="utf-8"))
    data = {}
    for code, fname in TRADE_FILES.items():
        trade = json.loads((RAW / fname).read_text(encoding="utf-8"))
        data[code] = build_country(code, cfg, trade, production[code], origins, eufic, ref)
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
