"""Unit tests cho Pipeline ETL & Dữ liệu 50 bài tập + PDF thực phẩm 2017."""

import importlib.util
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from scripts.etl.asset_handler import AssetHandler
from scripts.etl.build_50_exercises import build_50_exercises, EXERCISE_DEFINITIONS
from scripts.etl.build_curated_foods import build_curated_foods, FAMILIAR_FOOD_DEFINITIONS
from scripts.etl.crawl_bhx_prices import crawl_bhx_food_prices, BHX_BENCHMARK_PRICES
from scripts.etl.extract import check_vietnam_fct_2017_pdf, extract_exercises_json
from scripts.etl.extract_pdf_foods import extract_pdf_foods
from scripts.etl.transform import (
    infer_clinical_tags,
    intensity_from_met,
    map_met_for_exercise,
)


class TestETLPipeline(unittest.TestCase):
    def test_step1_extract_raw_datasets(self):
        exdb = extract_exercises_json()
        self.assertGreater(len(exdb), 800)

        pdf_path = check_vietnam_fct_2017_pdf()
        self.assertIsNotNone(pdf_path)
        assert pdf_path is not None
        self.assertTrue(pdf_path.name.endswith(".pdf"))

    def test_step2_extract_50_exercises(self):
        self.assertGreaterEqual(len(EXERCISE_DEFINITIONS), 50)
        items = build_50_exercises()
        self.assertGreaterEqual(len(items), 50)

        expected_muscles = {
            "Chest", "Back", "Shoulders", "Rear Delts", "Biceps", "Triceps",
            "Quadriceps", "Hamstrings", "Glutes", "Calves", "Abs"
        }
        found_muscles = {item["target_muscle"] for item in items}
        self.assertEqual(expected_muscles, found_muscles)

        # Kiểm tra đầy đủ 3 cấp độ cường độ (Light, Moderate, Vigorous)
        found_intensities = {item["intensity_level"] for item in items}
        self.assertEqual({"Light", "Moderate", "Vigorous"}, found_intensities)

        # Kiểm tra có đầy đủ bài tập ở mức độ Light
        light_items = [it for it in items if it["intensity_level"] == "Light"]
        self.assertGreaterEqual(len(light_items), 15)

        for item in items:
            self.assertIn("name_vi", item)
            self.assertIn("name_en", item)
            self.assertIn("target_muscle", item)
            self.assertIn("secondary_muscle", item)
            self.assertIn("banned_for", item)
            self.assertIn("clinical_reasons", item)
            self.assertIn("image", item)
            self.assertIn("common_mistakes", item)
            self.assertGreater(item["met_value"], 0)
            self.assertIn(item["intensity_level"], {"Light", "Moderate", "Vigorous"})

    def test_step3_extract_pdf_foods(self):
        pdf_path = check_vietnam_fct_2017_pdf()
        self.assertIsNotNone(pdf_path)

        foods = extract_pdf_foods()
        self.assertGreater(len(foods), 500)

        first = foods[0]
        self.assertTrue(first["code"].startswith("VN_"))
        self.assertTrue(first["name_vi"])
        self.assertEqual(first["source"], "VN_FCT")
        self.assertGreaterEqual(first["calories_100g"], 0)

    def test_step4_clinical_and_intensity_logic(self):
        self.assertEqual(intensity_from_met(2.3), "Light")
        self.assertEqual(intensity_from_met(4.5), "Moderate")
        self.assertEqual(intensity_from_met(8.0), "Vigorous")

        banned, reason = infer_clinical_tags("Barbell Back Squat", category="powerlifting")
        self.assertIn("knee_osteoarthritis", banned)
        self.assertIn("hypertension", banned)
        self.assertTrue(reason)

    def test_step5_curated_familiar_foods_with_bhx_prices(self):
        # Kiểm tra crawler giá Bách Hóa Xanh
        self.assertGreaterEqual(len(BHX_BENCHMARK_PRICES), 70)
        prices = crawl_bhx_food_prices()
        self.assertGreaterEqual(len(prices), 70)
        self.assertIn("uc_ga_phi_le", prices)
        self.assertIn("thit_ba_chi", prices)
        self.assertGreater(prices["uc_ga_phi_le"]["price_per_100g"], 0)

        # Kiểm tra danh mục thực phẩm quen thuộc đã tích hợp giá BHX
        foods = build_curated_foods()
        self.assertGreaterEqual(len(foods), 70)
        self.assertLessEqual(len(foods), 100)

        # Kiểm tra các nguyên liệu và món ăn quen thuộc bắt buộc có mặt
        food_names = [f["name_vi"].lower() for f in foods]
        self.assertTrue(any("ức gà" in n for n in food_names))
        self.assertTrue(any("thịt heo" in n or "ba chỉ" in n for n in food_names))
        self.assertTrue(any("bò" in n for n in food_names))
        self.assertTrue(any("trứng" in n for n in food_names))
        self.assertTrue(any("cá hồi" in n for n in food_names))
        self.assertTrue(any("rau muống" in n for n in food_names))
        self.assertTrue(any("gạo" in n for n in food_names))
        self.assertTrue(any("phở bò" in n for n in food_names))
        self.assertTrue(any("cơm tấm" in n for n in food_names))

        for f in foods:
            self.assertTrue(f["code"])
            self.assertTrue(f["name_vi"])
            self.assertGreater(f["calories_100g"], 0)
            self.assertGreater(f["estimated_price_vnd"], 0, f"Món {f['name_vi']} thiếu giá BHX")
            self.assertIn(f["diet_type"], {"all", "vegetarian", "vegan"})


if __name__ == "__main__":
    unittest.main()
