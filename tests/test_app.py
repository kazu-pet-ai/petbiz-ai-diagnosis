import unittest

from streamlit.testing.v1 import AppTest

from modules.diagnosis import BUSINESS_LABELS, SAMPLE_DATA


class AppTests(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file("../app.py").run(timeout=15)
        self.assertFalse(self.app.exception)

    def test_sample_button_restores_editable_sample_data(self):
        self.app.number_input[0].set_value(1).run()
        self.assertEqual(self.app.number_input[0].value, 1)
        self.app.button[0].click().run()
        self.assertEqual(self.app.number_input[0].value, SAMPLE_DATA[BUSINESS_LABELS[0]]["sales"])

    def test_all_businesses_render_and_diagnose_all_sections(self):
        expected_sections = {"#### 最優先課題", "#### AIの着眼点", "#### 改善優先順位 TOP 3", "#### AI活用候補", "#### 人が判断すべき領域"}
        for business in BUSINESS_LABELS:
            with self.subTest(business=business):
                app = AppTest.from_file("../app.py").run(timeout=15)
                app.radio[0].set_value(business).run()
                app.button[1].click().run(timeout=15)
                self.assertFalse(app.exception)
                rendered = {element.value for element in app.markdown}
                self.assertTrue(expected_sections.issubset(rendered))
                self.assertTrue(any("経営スコア" in value for value in rendered))
                self.assertTrue(any("この数字の“原因”まで" in value for value in rendered))


if __name__ == "__main__":
    unittest.main()
