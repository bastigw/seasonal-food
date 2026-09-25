import json
import unittest
from pathlib import Path

from pipeline import build
from pipeline.footprint import (
    haversine_km, production_with_source, scenario_kg_per_kg, tier, transport_kg_per_kg,
)
from pipeline.scenarios import (
    apply_origin_ref, confidence, domestic_volumes, import_scenarios, probabilities,
    recent_production_t, redistribute_hubs,
)

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "data" / "items.json").read_text(encoding="utf-8"))
ORIGINS = json.loads((ROOT / "data" / "origins.json").read_text(encoding="utf-8"))
ITEMS = {i["id"]: i for i in CFG["items"]}
BERLIN = CFG["countries"]["DE"]


class FootprintTests(unittest.TestCase):
    def test_haversine_berlin_madrid(self):
        self.assertAlmostEqual(haversine_km(52.52, 13.40, 40.4, -3.7), 1870, delta=40)

    def test_air_much_worse_than_sea(self):
        t = CFG["transport"]
        self.assertGreater(transport_kg_per_kg(8000, "air", t), 10 * transport_kg_per_kg(8000, "sea", t))

    def test_heated_scenario_uses_heated_production(self):
        tomato = ITEMS["tomato"]
        t = CFG["transport"]
        self.assertGreater(scenario_kg_per_kg(tomato, "domestic_heated", 0, t),
                           scenario_kg_per_kg(tomato, "domestic_fresh", 0, t))

    def test_tier_thresholds(self):
        th = CFG["tierThresholdsPerKg"]
        self.assertEqual([tier(0.4, th), tier(1.0, th), tier(3.0, th)], ["low", "medium", "high"])


class ScenarioTests(unittest.TestCase):
    def test_probabilities_sum_to_one(self):
        p = probabilities({"a": 1.0, "b": 3.0})
        self.assertAlmostEqual(sum(p.values()), 1.0)
        self.assertEqual(max(p, key=p.get), "b")

    def test_recent_production_ignores_zero_years(self):
        self.assertEqual(recent_production_t({"2018": 0, "2019": 10, "2020": 20}), 15)
        self.assertEqual(recent_production_t({}), 0)

    def test_domestic_glass_outside_season_is_heated(self):
        vols = domestic_volumes(ITEMS["tomato"], fresh=[6, 7, 8], stored=[], total_t=100, glass_t=50)
        self.assertIn("domestic_heated", vols[3])
        self.assertNotIn("domestic_heated", vols[7])

    def test_northern_import_is_heated_off_season_only(self):
        item = ITEMS["tomato"]
        args = dict(origins=ORIGINS, importer=BERLIN, transport_cfg=CFG["transport"])
        winter, _, _ = import_scenarios(item, 2, {"NL": 100.0, "ES": 100.0}, in_field_season=False, **args)
        summer, _, _ = import_scenarios(item, 8, {"NL": 100.0, "ES": 100.0}, in_field_season=True, **args)
        self.assertEqual(winter["import_near_heated"], 100.0)
        self.assertNotIn("import_near_heated", summer)

    def test_far_import_splits_air_share(self):
        vol, tr, _ = import_scenarios(ITEMS["green-bean"], 2, {"KE": 100.0}, ORIGINS, BERLIN, False, CFG["transport"])
        self.assertAlmostEqual(vol["import_far_air"], 60.0)
        self.assertGreater(tr["import_far_air"], tr["import_far"])

    def test_hub_volume_redistributed(self):
        out = redistribute_hubs({"NL": 50.0, "CO": 30.0, "EC": 20.0}, ["NL", "BE"])
        self.assertAlmostEqual(sum(out.values()), 100.0)
        self.assertNotIn("NL", out)

    def test_origin_ref_replaces_dispatch_countries(self):
        out = apply_origin_ref({"NL": 100.0}, {"CR": 90.0, "ES": 10.0}, ORIGINS)
        self.assertEqual(out, {"CR": 100.0})

    def test_low_confidence_on_fallback_or_split(self):
        self.assertEqual(confidence({"a": 0.9}, True, 0), "low")
        self.assertEqual(confidence({"a": 0.35, "b": 0.35, "c": 0.3}, False, 0), "low")
        self.assertEqual(confidence({"a": 0.9}, False, 0), "high")


class GoldenTests(unittest.TestCase):
    """Real snapshot: month effects must point the right way."""

    @classmethod
    def setUpClass(cls):
        cls.out = build.build()

    def item(self, country, month, item_id):
        for cat in ("vegetable", "fruit"):
            for g in self.out["data"][country][str(month)][cat]:
                for i in g["items"]:
                    if i["id"] == item_id:
                        return i

    def test_banana_is_long_travel_in_de(self):
        self.assertLess(self.item("DE", 2, "banana")["probShort"], 0.2)

    def test_tomato_feb_has_heated_share_de(self):
        feb, aug = self.item("DE", 2, "tomato"), self.item("DE", 8, "tomato")
        self.assertGreater(feb["mix"].get("import_near_heated", 0), aug["mix"].get("import_near_heated", 0))

    def test_potato_beats_air_freighted_beans(self):
        self.assertLess(self.item("GB", 2, "potato")["kgCo2ePerKg"],
                        self.item("GB", 2, "green-bean")["kgCo2ePerKg"])

    def test_origin_breakdown_has_distinct_per_country_values(self):
        # Different supplying countries should show their own footprint,
        # not one blended-away number repeated for each row.
        rows = self.item("GB", 1, "banana")["originBreakdown"]
        self.assertGreater(len(rows), 1)
        values = {r["kgCo2ePerKg"] for r in rows}
        self.assertGreater(len(values), 1)
        shares = [r["share"] for r in rows]
        self.assertEqual(shares, sorted(shares, reverse=True))

    def test_banana_production_uses_hestia_origin_value_not_flat_constant(self):
        # GB imports bananas mostly from Colombia in January; HESTIA has a
        # real per-country value for that, which should override the item's
        # flat global productionFieldKgPerKg constant.
        flat = ITEMS["banana"]["productionFieldKgPerKg"]
        self.assertNotAlmostEqual(self.item("GB", 1, "banana")["productionKgPerKg"], flat, places=2)

    def test_production_source_tiers(self):
        item = {**ITEMS["avocado"], "hestiaProxy": {"CL": "PE"}}
        hestia = {"avocado": {"PE": {"gwp100KgPerKg": 4.05}}}
        self.assertEqual(production_with_source(item, "import_far", "PE", hestia), (4.05, "country", None))
        self.assertEqual(production_with_source(item, "import_far", "CL", hestia), (4.05, "proxy", "PE"))
        flat = item["productionFieldKgPerKg"]
        # No proxy mapping for CO, and a proxy whose own value is missing, both fall through.
        self.assertEqual(production_with_source(item, "import_far", "CO", hestia), (flat, "estimate", None))
        self.assertEqual(production_with_source(item, "import_far", "CL", {}), (flat, "estimate", None))

    def test_avocado_chile_and_colombia_use_peru_proxy_in_breakdown(self):
        seen = {}
        for cc in ("DE", "GB"):
            for m in range(1, 13):
                for o in (self.item(cc, m, "avocado") or {}).get("originBreakdown", []):
                    seen.setdefault(o["code"], o)
        self.assertTrue(seen, "avocado should have an origin breakdown")
        for code in ("CL", "CO"):
            if code in seen:
                self.assertEqual(seen[code]["productionSource"], "proxy", code)
                self.assertEqual(seen[code]["proxyFrom"], "PE")
        if "PE" in seen:
            self.assertEqual(seen["PE"]["productionSource"], "country")

    def test_groups_sorted_best_to_worst(self):
        for country in self.out["data"].values():
            for month in country.values():
                for cat in ("vegetable", "fruit"):
                    for g in month[cat]:
                        v = [i["kgCo2ePerKg"] for i in g["items"]]
                        self.assertEqual(v, sorted(v))

    def test_dairy_meat_reference_values(self):
        rows = {i["id"]: i["kgCo2ePerKg"] for i in self.out["dairyMeat"]}
        self.assertEqual(set(rows), {i["id"] for i in CFG["dairyMeat"]["items"]})
        self.assertIn("farmed-fish", rows)
        self.assertEqual(list(rows.values()), sorted(rows.values(), reverse=True))
        self.assertAlmostEqual(rows["beef"], 0.4 * 99.48 + 0.6 * 33.3, places=1)
        # The big animal products dwarf even air-freighted produce (milk and
        # eggs per kg do not, which is why the page rescales rather than assuming).
        worst_produce = max(
            i["kgCo2ePerKg"]
            for month in self.out["data"]["DE"].values()
            for cat in ("vegetable", "fruit")
            for g in month[cat]
            for i in g["items"]
        )
        self.assertGreater(sorted(rows.values())[-4], worst_produce)

    def test_category_group_limits(self):
        self.assertLessEqual(len(CFG["groups"]["vegetable"]), 4)  # 3 + Other
        self.assertLessEqual(len(CFG["groups"]["fruit"]), 3)  # 2 + Other


if __name__ == "__main__":
    unittest.main()
