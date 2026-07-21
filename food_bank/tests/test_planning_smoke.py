"""Smoke tests for planning engine (Phases 1–3). Run: python -m unittest tests.test_planning_smoke"""

import unittest
import uuid

import store


class PlanningSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        store.load()
        cls.fb_id = store.get_app_settings()["food_bank_id"]
        cls.week_key = "2099-W50"

    def test_map_url_validation(self):
        cleaned = store.save_app_settings({"donor_dropoff_map_url": "http://bad"})
        self.assertEqual(cleaned["donor_dropoff_map_url"], "")
        cleaned = store.save_app_settings({"donor_dropoff_map_url": "https://maps.example.com/pantry"})
        self.assertEqual(cleaned["donor_dropoff_map_url"], "https://maps.example.com/pantry")

    def test_donor_guidance_enrichment(self):
        diapers = next(c for c in store.get_planning_categories() if c["id"] == "diapers")
        self.assertIn("donor_guidance", diapers)
        self.assertIn("Any size", diapers["donor_guidance"])

    def test_visit_normalization_denominator(self):
        wk = "2099-W51"
        visitor = str(uuid.uuid4())
        non_visitor = str(uuid.uuid4())
        store.add_client_requests(visitor, ["canned"], self.fb_id, wk, expecting_visit=True)
        store.add_client_requests(non_visitor, ["canned", "produce"], self.fb_id, wk, expecting_visit=False)
        report = store.compute_weekly_trends(self.fb_id, wk)
        canned = next(r for r in report["categories"] if r["category_id"] == "canned")
        self.assertTrue(report["demand_normalized"])
        self.assertEqual(canned["client_count"], 1)
        self.assertEqual(canned["demand_pct"], 100.0)

    def test_compute_week_forecast(self):
        forecast = store.compute_week_forecast(self.fb_id, self.week_key)
        self.assertEqual(forecast["week_key"], store.next_week_key(self.week_key))
        self.assertIn("headline", forecast)
        self.assertIn("categories", forecast)

    def test_bundle_rule_fires(self):
        store.save_staff_thresholds(
            {
                "produce": "low",
                "dairy": "critically_low",
                "protein": "ok",
                "grains": "ok",
                "gluten_free": "ok",
                "canned": "ok",
                "baby": "ok",
                "diapers": "ok",
                "personal_care": "ok",
                "snacks": "ok",
            },
            {"shelf": "ok", "refrigerated": "ok", "frozen": "ok"},
        )
        cid = str(uuid.uuid4())
        store.add_client_requests(cid, ["produce", "dairy"], self.fb_id, "2099-W52", expecting_visit=True)
        plan = store.compute_order_plan(self.fb_id, "2099-W52")
        self.assertGreaterEqual(len(plan["bundle_suggestions"]), 1)

    def test_recommended_mix_shape(self):
        plan = store.compute_order_plan(self.fb_id, self.week_key)
        mix = plan["recommended_mix"]
        self.assertIn("total_pallets", mix)
        self.assertIn("by_storage", mix)
        self.assertIn("headline", mix)
        self.assertIn("also_consider", plan)
        self.assertIn("forecast", plan)


if __name__ == "__main__":
    unittest.main()
