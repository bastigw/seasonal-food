import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set

from .produce_groups import GROUP_ORDER, group_for

DATA_PATH = Path(__file__).resolve().parent.parent / "eufic_seasonal_produce_matrix.json"

_produce = None


def _display_name(name: str) -> str:
    return " ".join(word.capitalize() for word in name.split(" "))


def _load() -> dict:
    global _produce
    if _produce is None:
        with open(DATA_PATH, encoding="utf-8") as f:
            _produce = json.load(f)["produce"]
    return _produce


def _contiguous_run(months: Set[int], current: int) -> List[int]:
    """The maximal run of consecutive months (wrapping Dec->Jan) containing `current`."""
    if len(months) >= 12:
        return list(range(1, 13))

    run = [current]

    m = current
    while True:
        prev = m - 1 if m > 1 else 12
        if prev in months and prev not in run:
            run.insert(0, prev)
            m = prev
        else:
            break

    m = current
    while True:
        nxt = m + 1 if m < 12 else 1
        if nxt in months and nxt not in run:
            run.append(nxt)
            m = nxt
        else:
            break

    return run


def _season_stage(months: List[int], current: int) -> Optional[str]:
    """Where `current` falls within its contiguous in-season run: early/peak/ending.

    None means the item is in season essentially year-round (no meaningful stage).
    """
    month_set = set(months)
    if len(month_set) >= 12:
        return None

    run = _contiguous_run(month_set, current)
    if len(run) <= 1:
        return "peak"
    if current == run[0]:
        return "early"
    if current == run[-1]:
        return "ending"
    return "peak"


def get_seasonal(month: int, country: str) -> Dict[str, Dict[str, List[dict]]]:
    """Produce in season for a country/month, grouped and stage-annotated.

    Returns, e.g.:
        {
          "fresh": {
            "vegetable": [{"group": "Leafy Greens & Salad", "items": [{"name": "Rucola", "stage": "peak"}, ...]}, ...],
            "fruit": [...],
          },
          "stored": {...},
        }
    """
    buckets: Dict[str, Dict[str, Dict[str, list]]] = {
        "fresh": {"vegetable": defaultdict(list), "fruit": defaultdict(list)},
        "stored": {"vegetable": defaultdict(list), "fruit": defaultdict(list)},
    }

    for name, info in _load().items():
        country_info = info["countries"].get(country)
        if not country_info:
            continue
        category = info["category"]
        group = group_for(name, category)
        for state in ("fresh", "stored"):
            months = country_info.get(state, [])
            if month in months:
                buckets[state][category][group].append(
                    {"name": _display_name(name), "stage": _season_stage(months, month)}
                )

    result: Dict[str, Dict[str, List[dict]]] = {}
    for state, categories in buckets.items():
        result[state] = {}
        for category, groups in categories.items():
            ordered_groups = []
            for group_name in GROUP_ORDER[category]:
                items = groups.get(group_name)
                if items:
                    items.sort(key=lambda item: item["name"])
                    ordered_groups.append({"group": group_name, "items": items})
            result[state][category] = ordered_groups

    return result
