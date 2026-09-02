import os
import unittest

from modules.diagnosis import (
    BUSINESS_LABELS,
    DOG_CAT_SHOP,
    SAMPLE_DATA,
    calculate_long_stay_ratio,
    diagnose,
)


class DiagnosisTests(unittest.TestCase):
    def test_shop_representative_case_compares_long_stay(self):
        result = diagnose(DOG_CAT_SHOP, SAMPLE_DATA[DOG_CAT_SHOP])
        self.assertEqual(result.top_issues[0].title, "長期在店")
        self.assertIn("成約率", result.priority_message)
        self.assertIn("90日超在店", result.ai_insight)
        self.assertEqual(len(result.top_issues), 3)
        combined = result.priority_message + result.ai_insight + " ".join(x.detail for x in result.top_issues)
        self.assertNotIn("成約率は大きく崩れていない", combined)
        self.assertNotIn("成約率は低い", combined)
        self.assertNotIn("成約率は高い", combined)

    def test_shop_prioritizes_conversion_when_leads_are_plentiful(self):
        result = diagnose(DOG_CAT_SHOP, {"sales": 5, "visits": 50, "conversion": 10, "price": 250000, "days": 45, "inventory": 10, "long_stay": 0, "inquiries": 60})
        self.assertEqual(result.top_issues[0].title, "成約率")
        self.assertIn("集客量より", result.ai_insight)

    def test_long_stay_ratio_uses_current_inventory(self):
        self.assertEqual(calculate_long_stay_ratio(3, 15), 20.0)
        result = diagnose(DOG_CAT_SHOP, SAMPLE_DATA[DOG_CAT_SHOP])
        self.assertIn("在店CA15頭のうち90日超在店が3頭（20%）", result.top_issues[0].detail)

    def test_zero_inventory_is_safe(self):
        self.assertEqual(calculate_long_stay_ratio(3, 0), 0.0)
        data = {**SAMPLE_DATA[DOG_CAT_SHOP], "inventory": 0}
        result = diagnose(DOG_CAT_SHOP, data)
        self.assertIn("入力値", " ".join(issue.detail for issue in result.top_issues))

    def test_salon_representative_case_compares_capacity_and_ticket(self):
        result = diagnose("トリミングサロン", SAMPLE_DATA["トリミングサロン"])
        self.assertEqual(result.top_issues[0].title, "客単価・メニュー構成")
        self.assertIn("予約稼働率", result.priority_message)
        self.assertIn("単純に予約件数を増やす余地", result.ai_insight)
        combined = result.priority_message + result.ai_insight + " ".join(x.detail for x in result.top_issues)
        self.assertNotIn("客単価は低い", combined)
        self.assertNotIn("平均客単価は低い", combined)
        self.assertIn("目標客単価との差", combined)

    def test_breeder_representative_case_compares_funnel(self):
        result = diagnose("ブリーダー", SAMPLE_DATA["ブリーダー"])
        self.assertEqual(result.top_issues[0].title, "成約ファネル全体")
        self.assertIn("問い合わせ", result.priority_message)
        self.assertIn("問い合わせ40件から見学12件、成約3件", result.ai_insight)
        self.assertIn("異なる段階の率を単純比較せず", result.ai_insight)
        self.assertNotIn("率がより低い", result.ai_insight)

    def test_scores_are_bounded_and_zero_values_are_safe(self):
        cases = {
            DOG_CAT_SHOP: {"sales": 0, "visits": 0, "conversion": 0, "price": 0, "days": 500, "inventory": 0, "long_stay": 100, "inquiries": 0},
            "トリミングサロン": {"revenue": 0, "treatments": 0, "ticket": 0, "return_rate": 0, "occupancy": 0, "new_customers": 0, "next_booking": 0},
            "ブリーダー": {"inquiries": 0, "visits": 0, "contracts": 0, "inquiry_visit": 0, "visit_contract": 0, "sales_days": 500, "digital_share": 0},
        }
        for business, data in cases.items():
            with self.subTest(business=business):
                result = diagnose(business, data)
                self.assertGreaterEqual(result.score, 0)
                self.assertLessEqual(result.score, 100)

    def test_only_implemented_businesses_are_selectable(self):
        self.assertEqual(BUSINESS_LABELS, (DOG_CAT_SHOP, "トリミングサロン", "ブリーダー"))


class ConfigurationTests(unittest.TestCase):
    def test_cta_url_has_default_without_environment_value(self):
        previous = os.environ.pop("CTA_URL", None)
        try:
            import config
            self.assertTrue(config.CTA_URL.startswith("https://"))
        finally:
            if previous is not None:
                os.environ["CTA_URL"] = previous


if __name__ == "__main__":
    unittest.main()
