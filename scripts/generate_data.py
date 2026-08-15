"""Builds frontend/src/data/seasonal.json: every country x every month, baked
in at build time so the Vue app ships with no backend and no runtime API.
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from app.seasonal import DATA_PATH, get_seasonal  # noqa: E402

OUTPUT_PATH = REPO_ROOT / "frontend" / "src" / "data" / "seasonal.json"

# Countries that get a dedicated tab; every other country present in the
# source data gets listed in the "more countries" dropdown.
MAIN_CODES = ["GB", "DE", "IT", "ES"]

# ISO 3166-1 alpha-2 -> English display name, for every country code present
# in eufic_seasonal_produce_matrix.json.
COUNTRY_NAMES = {
    "AT": "Austria",
    "BE": "Belgium",
    "BG": "Bulgaria",
    "CH": "Switzerland",
    "CY": "Cyprus",
    "CZ": "Czechia",
    "DE": "Germany",
    "DK": "Denmark",
    "EE": "Estonia",
    "ES": "Spain",
    "FI": "Finland",
    "FR": "France",
    "GB": "United Kingdom",
    "GR": "Greece",
    "HR": "Croatia",
    "HU": "Hungary",
    "IE": "Ireland",
    "IT": "Italy",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "LV": "Latvia",
    "MT": "Malta",
    "NL": "Netherlands",
    "PL": "Poland",
    "PT": "Portugal",
    "RO": "Romania",
    "SE": "Sweden",
    "SK": "Slovakia",
    "TR": "Turkey",
}

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def _flag(code: str) -> str:
    """Regional-indicator flag emoji for an ISO 3166-1 alpha-2 code."""
    return "".join(chr(0x1F1E6 + ord(letter) - ord("A")) for letter in code)


def _country_codes() -> list[str]:
    with open(DATA_PATH, encoding="utf-8") as f:
        produce = json.load(f)["produce"]
    codes = {code for item in produce.values() for code in item["countries"]}
    return sorted(codes)


def build_countries() -> list[dict]:
    codes = _country_codes()
    missing = [code for code in codes if code not in COUNTRY_NAMES]
    if missing:
        raise ValueError(f"No display name for country code(s): {missing}")

    main = [
        {"code": code, "label": COUNTRY_NAMES[code], "flag": _flag(code), "main": True}
        for code in MAIN_CODES
    ]
    others = sorted(
        (
            {"code": code, "label": COUNTRY_NAMES[code], "flag": _flag(code), "main": False}
            for code in codes
            if code not in MAIN_CODES
        ),
        key=lambda c: c["label"],
    )
    return main + others


def build() -> dict:
    countries = build_countries()
    data = {}
    for country in countries:
        code = country["code"]
        data[code] = {str(month): get_seasonal(month, code) for month in range(1, 13)}
    return {"countries": countries, "monthNames": MONTH_NAMES, "data": data}


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(build(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
