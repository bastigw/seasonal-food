"""Builds frontend/src/data/seasonal.json: every country x every month, baked
in at build time so the Vue app ships with no backend and no runtime API.
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from app.seasonal import get_seasonal  # noqa: E402

OUTPUT_PATH = REPO_ROOT / "frontend" / "src" / "data" / "seasonal.json"

SHIPPED_NOTE = "Much of what's in season here gets shipped to the UK and Germany."

COUNTRIES = [
    {"code": "GB", "label": "United Kingdom", "flag": "\U0001F1EC\U0001F1E7", "note": None},
    {"code": "DE", "label": "Germany", "flag": "\U0001F1E9\U0001F1EA", "note": None},
    {"code": "IT", "label": "Italy", "flag": "\U0001F1EE\U0001F1F9", "note": SHIPPED_NOTE},
    {"code": "ES", "label": "Spain", "flag": "\U0001F1EA\U0001F1F8", "note": SHIPPED_NOTE},
]

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def build() -> dict:
    data = {}
    for country in COUNTRIES:
        code = country["code"]
        data[code] = {str(month): get_seasonal(month, code) for month in range(1, 13)}
    return {"countries": COUNTRIES, "monthNames": MONTH_NAMES, "data": data}


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(build(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
