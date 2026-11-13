"""Unit tests cho Pipeline ETL 4 bước (Extract -> Asset Handling -> Transform & Map MET)."""

import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Cho phép chạy test logic ETL bằng unittest thuần kể cả khi chưa cài pydantic_settings/requests/sqlalchemy
if importlib.util.find_spec("pydantic_settings") is None and "app.config" not in sys.modules:
    fake_cfg = types.ModuleType("app.config")
    fake_cfg.BACKEND_DIR = BACKEND_DIR  # type: ignore[attr-defined]
    fake_cfg.settings = types.SimpleNamespace(  # type: ignore[attr-defined]
        ASSET_STORAGE_PROVIDER="github_cdn",
        ASSET_BASE_URL="https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises",
        CLOUDINARY_CLOUD_NAME="",
        CLOUDINARY_API_KEY="",
        CLOUDINARY_API_SECRET="",
        CLOUDINARY_FOLDER="fitness_app/exercises",
        AWS_S3_BUCKET="",
        AWS_S3_REGION="ap-southeast-1",
        AWS_S3_PREFIX="exercises",
        AWS_ACCESS_KEY_ID="",
        AWS_SECRET_ACCESS_KEY="",
    )
    sys.modules["app.config"] = fake_cfg

if importlib.util.find_spec("requests") is None and "requests" not in sys.modules:
    sys.modules["requests"] = types.ModuleType("requests")

if importlib.util.find_spec("sqlalchemy") is None and "scripts.etl.load" not in sys.modules:
    fake_load = types.ModuleType("scripts.etl.load")
    fake_load.load_exercises = lambda *a, **k: (0, 0)  # type: ignore[attr-defined]
    fake_load.load_foods = lambda *a, **k: (0, 0)  # type: ignore[attr-defined]
    sys.modules["scripts.etl.load"] = fake_load

from scripts.etl.asset_handler import AssetHandler  # noqa: E402
from scripts.etl.extract import (  # noqa: E402
    check_vietnam_fct_2017_pdf,
    extract_compendium_csv,
    extract_exercises_json,
    extract_kaggle_exercise_csv,
    extract_megagym_csv,
)
from scripts.etl.transform import (  # noqa: E402
    infer_clinical_tags,
    intensity_from_met,
    map_met_for_exercise,
    transform_compendium_rows,
    transform_exercises_json,
    transform_kaggle_rows,
    transform_megagym_rows,
)


class TestETLPipeline(unittest.TestCase):
    def test_step1_extract_raw_datasets(self):
        exdb = extract_exercises_json()
        comp = extract_compendium_csv()
        kag = extract_kaggle_exercise_csv()
        mega = extract_megagym_csv()

        self.assertGreater(len(exdb), 800)
        self.assertGreater(len(comp), 800)
        self.assertGreater(len(kag), 200)
        self.assertGreater(len(mega), 2500)
        pdf_path = check_vietnam_fct_2017_pdf()
        self.assertIsNotNone(pdf_path)
        assert pdf_path is not None
        self.assertTrue(pdf_path.name.endswith(".pdf"))

    def test_step2_asset_handler_cdn_and_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest_file = Path(tmp) / "manifest.json"
            handler = AssetHandler(provider="github_cdn", upload_enabled=False, manifest_path=manifest_file)
            urls, thumb, video = handler.resolve_exercise_media(["3_4_Sit-Up/0.jpg", "3_4_Sit-Up/1.jpg"])

            self.assertEqual(len(urls), 2)
            self.assertIsNotNone(thumb)
            assert thumb is not None
            self.assertTrue(thumb.endswith("/3_4_Sit-Up/0.jpg"))
            self.assertIsNone(video)

    def test_step3_transform_and_met_mapping(self):
        self.assertEqual(intensity_from_met(2.3), "Light")
        self.assertEqual(intensity_from_met(4.5), "Moderate")
        self.assertEqual(intensity_from_met(8.0), "Vigorous")

        self.assertGreaterEqual(map_met_for_exercise("Barbell Back Squat", category="powerlifting"), 6.0)
        self.assertLess(map_met_for_exercise("Hamstring Stretch", category="stretching"), 3.0)

        banned, reason = infer_clinical_tags("Barbell Back Squat", category="powerlifting")
        self.assertIn("knee_osteoarthritis", banned)
        self.assertIn("hypertension", banned)
        self.assertTrue(reason)

    def test_step3_transform_all_sources_schema(self):
        exdb_records = transform_exercises_json(extract_exercises_json()[:5])
        comp_records = transform_compendium_rows(extract_compendium_csv()[:5])
        kag_records = transform_kaggle_rows(extract_kaggle_exercise_csv()[:5])
        mega_records = transform_megagym_rows(extract_megagym_csv()[:5])

        for rec in exdb_records + comp_records + kag_records + mega_records:
            self.assertTrue(rec["code"])
            self.assertTrue(rec["name_en"])
            self.assertGreater(rec["met_value"], 0)
            self.assertIn(rec["intensity_level"], {"Light", "Moderate", "Vigorous"})
            self.assertIsInstance(rec["banned_for"], list)
            self.assertIsInstance(rec["image_urls"], list)


if __name__ == "__main__":
    unittest.main()
