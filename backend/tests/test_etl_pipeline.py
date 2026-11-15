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
        self.assertEqual(len(EXERCISE_DEFINITIONS), 50)
        items = build_50_exercises()
        self.assertEqual(len(items), 50)

        expected_muscles = {
            "Chest", "Back", "Shoulders", "Rear Delts", "Biceps", "Triceps",
            "Quadriceps", "Hamstrings", "Glutes", "Calves", "Abs"
        }
        found_muscles = {item["target_muscle"] for item in items}
        self.assertEqual(expected_muscles, found_muscles)

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


if __name__ == "__main__":
    unittest.main()
