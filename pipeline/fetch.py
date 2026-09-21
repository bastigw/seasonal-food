"""Downloads raw trade and production data into data/raw/ (committed snapshot).

Run manually (needs network): python3 -m pipeline.fetch
The build (pipeline/build.py) only reads the snapshot, so it is offline and
deterministic.

Sources:
  Eurostat Comext DS-045409   monthly imports into DE by origin (kg)
  HMRC uktradeinfo OTS        monthly imports into GB by origin (kg net mass)
  Eurostat apro_cpsh1         annual harvested production (thousand tonnes)
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
CONFIG = json.loads((ROOT / "data" / "items.json").read_text(encoding="utf-8"))

COMEXT = "https://ec.europa.eu/eurostat/api/comext/dissemination/statistics/1.0/data/DS-045409"
CROPS = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/apro_cpsh1"
HMRC = "https://api.uktradeinfo.com"


def get(url: str, retries: int = 3) -> dict:
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=120) as resp:
                return json.load(resp)
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(3)


def jsonstat_rows(data: dict):
    """Yield {dimension: category} -> value for a JSON-stat 2.0 response."""
    ids, sizes, dims = data["id"], data["size"], data["dimension"]
    index = {d: {v: k for k, v in dims[d]["category"]["index"].items()} for d in ids}
    for pos, value in data.get("value", {}).items():
        pos = int(pos)
        coords = {}
        for d, size in reversed(list(zip(ids, sizes))):
            coords[d] = index[d][pos % size]
            pos //= size
        yield coords, value


def fetch_comext(reporter: str = "DE", ref_only: bool = False) -> dict:
    out = {}
    for item in CONFIG["items"]:
        if ref_only and not item["originRef"]:
            continue
        per_origin: dict = {}
        for year in CONFIG["years"]:
            months = "&".join(f"time={year}-{m:02d}" for m in range(1, 13))
            url = (
                f"{COMEXT}?format=JSON&lang=EN&freq=M&reporter={reporter}&flow=1"
                f"&product={item['tradeCode']}&indicators=QUANTITY_IN_100KG&{months}"
            )
            for coords, value in jsonstat_rows(get(url)):
                partner = coords["partner"]
                if len(partner) != 2 or not partner.isalpha():
                    continue  # skip aggregates such as WORLD / INT_EU27_2020
                per_origin.setdefault(partner, {})[coords["time"]] = value * 100.0
        out[item["id"]] = per_origin
        print("comext", item["id"], len(per_origin), "origins")
    return out


def fetch_hmrc() -> dict:
    countries = {}
    url = f"{HMRC}/Country?$select=CountryId,CountryCodeAlpha"
    while url:
        page = get(url)
        for c in page["value"]:
            countries[c["CountryId"]] = c["CountryCodeAlpha"]
        url = page.get("@odata.nextLink")

    first, last = CONFIG["years"][0], CONFIG["years"][-1]
    out = {}
    for item in CONFIG["items"]:
        code = item["tradeCode"]
        field = "Cn8Code" if len(code) == 8 else f"Hs{len(code)}Code"
        flt = (
            f"Commodity/{field} eq '{code}' and MonthId ge {first}01 and MonthId le {last}12"
            " and (FlowTypeId eq 1 or FlowTypeId eq 3)"
        )
        url = (
            f"{HMRC}/OTS?$select=MonthId,CountryId,NetMass&$filter={urllib.parse.quote(flt)}"
        )
        per_origin: dict = {}
        while url:
            page = get(url)
            for row in page["value"]:
                if not row["NetMass"]:
                    continue
                origin = countries.get(row["CountryId"], "")
                if len(origin) != 2 or not origin.isalpha():
                    continue
                month = str(row["MonthId"])
                key = f"{month[:4]}-{month[4:]}"
                slot = per_origin.setdefault(origin, {})
                slot[key] = slot.get(key, 0.0) + float(row["NetMass"])
            url = page.get("@odata.nextLink")
        out[item["id"]] = per_origin
        print("hmrc", item["id"], len(per_origin), "origins")
    return out


def fetch_production() -> dict:
    codes = sorted(
        {
            c
            for item in CONFIG["items"]
            for c in (item["cropCode"], item["glassCropCode"])
            if c
        }
    )
    crops = "&".join(f"crops={c}" for c in codes)
    url = (
        f"{CROPS}?format=JSON&lang=EN&geo=DE&geo=UK&strucpro=HPRD_HUMD_EU_THS_T&{crops}"
    )
    out: dict = {"DE": {}, "GB": {}}
    for coords, value in jsonstat_rows(get(url)):
        country = "GB" if coords["geo"] == "UK" else coords["geo"]
        out[country].setdefault(coords["crops"], {})[coords["time"]] = value * 1000.0  # tonnes
    return out


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[1:])
    jobs = (
        ("comext_DE", fetch_comext),
        ("comext_EU", lambda: fetch_comext("EU27_2020", ref_only=True)),
        ("hmrc_GB", fetch_hmrc),
        ("production", fetch_production),
    )
    for name, fn in jobs:
        if only and name not in only:
            continue
        (RAW / f"{name}.json").write_text(json.dumps(fn(), separators=(",", ":")), encoding="utf-8")
        print("wrote", name)


if __name__ == "__main__":
    main()
