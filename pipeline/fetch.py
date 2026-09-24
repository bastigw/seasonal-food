"""Downloads raw trade and production data into data/raw/ (committed snapshot).

Run manually (needs network): python3 -m pipeline.fetch
The build (pipeline/build.py) only reads the snapshot, so it is offline and
deterministic.

Sources:
  Eurostat Comext DS-045409   monthly imports into DE by origin (kg)
  HMRC uktradeinfo OTS        monthly imports into GB by origin (kg net mass)
  Eurostat apro_cpsh1         annual harvested production (thousand tonnes)
  HESTIA aggregated data      per-country crop production GWP100 (kg CO2e/kg)
                              via the public AWS Open Data bucket (no auth).
                              Needs the `duckdb` package (fetch-time only;
                              pipeline/build.py stays dependency-free).
"""
import json
import sys
import tempfile
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

# Newest release older than 182 days (HESTIA's own cutoff for publicly
# available, non-preview data); check https://api.hestia.earth/settings/dataReleases
# for newer ones as time passes.
HESTIA_RELEASE = "2026-03-10"
HESTIA_PARQUET = (
    f"https://hestia-aggregated-data.s3.eu-west-2.amazonaws.com/"
    f"data/parquet/releases/{HESTIA_RELEASE}/impacts.parquet"
)
# HESTIA's countryId is "GADM-<ISO3>"; map the ISO3 codes it actually uses
# to the ISO2 codes this project keys everything else by.
HESTIA_ISO3_TO_ISO2 = {
    "ALB": "AL", "ARG": "AR", "AUS": "AU", "BGD": "BD", "BRA": "BR", "KHM": "KH",
    "CAN": "CA", "CHN": "CN", "COL": "CO", "CRI": "CR", "CYP": "CY", "CIV": "CI",
    "DOM": "DO", "ECU": "EC", "FRA": "FR", "DEU": "DE", "GHA": "GH", "HUN": "HU",
    "IND": "IN", "IDN": "ID", "IRN": "IR", "IRL": "IE", "ITA": "IT", "KEN": "KE",
    "LVA": "LV", "MYS": "MY", "MEX": "MX", "MMR": "MM", "NPL": "NP", "PAK": "PK",
    "PER": "PE", "PRT": "PT", "ROU": "RO", "RUS": "RU", "ZAF": "ZA", "ESP": "ES",
    "SWE": "SE", "TZA": "TZ", "THA": "TH", "TUR": "TR", "UKR": "UA", "GBR": "GB",
    "USA": "US", "VNM": "VN",
}


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


def fetch_hestia() -> dict:
    """{itemId: {countryCode: {gwp100, qualityScore}}} for items with a hestiaProduct."""
    import duckdb  # fetch-time only dependency; pip install duckdb

    products = {i["hestiaProduct"]: i["id"] for i in CONFIG["items"] if i["hestiaProduct"]}

    with tempfile.NamedTemporaryFile(suffix=".parquet") as tmp:
        print("hestia: downloading", HESTIA_PARQUET)
        urllib.request.urlretrieve(HESTIA_PARQUET, tmp.name)
        rows = duckdb.connect().execute(
            """
            SELECT productName, countryId, value, aggregatedQualityScore, aggregatedQualityScoreMax
            FROM read_parquet(?)
            WHERE section = 'impacts' AND termId = 'gwp100' AND productName IN ?
            """,
            [tmp.name, list(products)],
        ).fetchall()

    out: dict = {}
    for product_name, country_id, value, score, score_max in rows:
        iso3 = country_id.removeprefix("GADM-")
        iso2 = HESTIA_ISO3_TO_ISO2.get(iso3)
        if not iso2 or value is None:
            continue  # skip "World" aggregate and any region we can't map
        item_id = products[product_name]
        out.setdefault(item_id, {})[iso2] = {
            "gwp100KgPerKg": round(float(value), 4),
            "qualityScore": float(score) / float(score_max) if score is not None else None,
        }
    for item_id, by_country in out.items():
        print("hestia", item_id, len(by_country), "countries")
    return out


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[1:])
    jobs = (
        ("comext_DE", fetch_comext),
        ("comext_EU", lambda: fetch_comext("EU27_2020", ref_only=True)),
        ("hmrc_GB", fetch_hmrc),
        ("production", fetch_production),
        ("hestia_gwp100", fetch_hestia),
    )
    for name, fn in jobs:
        if only and name not in only:
            continue
        (RAW / f"{name}.json").write_text(json.dumps(fn(), separators=(",", ":")), encoding="utf-8")
        print("wrote", name)


if __name__ == "__main__":
    main()
