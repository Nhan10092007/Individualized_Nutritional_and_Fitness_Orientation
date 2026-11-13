"""
Bước 1 (Extract): Tải file raw từ GitHub / URL chính thống hoặc đọc từ backend/data/raw/.
"""

import csv
import json
import urllib.request
from pathlib import Path
from typing import Any

from app.config import BACKEND_DIR

RAW_DATA_DIR = BACKEND_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BACKEND_DIR / "data" / "processed"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

GITHUB_EXERCISES_JSON_URL = (
    "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json"
)
GITHUB_COMPENDIUM_CSV_URL = (
    "https://raw.githubusercontent.com/andyreagan/compendium-of-physical-activity/master/compendiumofphysicalactivities.csv"
)
VIETNAM_FCT_2017_PDF_NAME = "bang-thanh-phan-dinh-duong-thuc-pham-vn-2017-27-4-17.pdf"
VIETNAM_FCT_2017_PDF_PATH = RAW_DATA_DIR / VIETNAM_FCT_2017_PDF_NAME


def check_vietnam_fct_2017_pdf(path: Path | str | None = None) -> Path | None:
    """Kiểm tra sự tồn tại của file PDF Bảng thành phần dinh dưỡng thực phẩm Việt Nam 2017."""
    target = Path(path) if path else VIETNAM_FCT_2017_PDF_PATH
    if target.exists():
        return target
    return None


def download_file(url: str, dest: Path, *, overwrite: bool = False, timeout: int = 30) -> Path:
    """Tải file từ URL về đường dẫn đích nếu chưa tồn tại (hoặc khi overwrite=True)."""
    if dest.exists() and not overwrite:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (FitnessNutritionETL/1.0)"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp, open(dest, "wb") as f:
        f.write(resp.read())
    return dest


def ensure_raw_file(
    local_path: Path,
    remote_url: str | None = None,
    *,
    download_if_missing: bool = False,
) -> Path | None:
    """Kiểm tra file raw local; nếu thiếu và cho phép tải thì tải từ remote_url."""
    if local_path.exists():
        return local_path
    if download_if_missing and remote_url:
        try:
            return download_file(remote_url, local_path)
        except Exception as exc:
            print(f"[!] Không thể tải {remote_url}: {exc}")
            return None
    return None


def extract_exercises_json(
    path: Path | str | None = None,
    *,
    download_if_missing: bool = False,
) -> list[dict[str, Any]]:
    """Đọc danh sách bài tập từ free-exercise-db JSON."""
    target = Path(path) if path else RAW_DATA_DIR / "exercises.json"
    resolved = ensure_raw_file(target, GITHUB_EXERCISES_JSON_URL, download_if_missing=download_if_missing)
    if not resolved:
        return []
    with open(resolved, mode="r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def extract_compendium_csv(
    path: Path | str | None = None,
    *,
    download_if_missing: bool = False,
) -> list[dict[str, str]]:
    """
    Đọc dữ liệu Ainsworth Compendium CSV.
    Hỗ trợ cả định dạng pipe '|' 8 cột (2 dòng header, cột 2011 ở vị trí 4..7)
    lẫn định dạng CSV chuẩn có header ('code', 'met', 'description', 'category').
    """
    target = Path(path) if path else RAW_DATA_DIR / "compendium_github.csv"
    resolved = ensure_raw_file(target, GITHUB_COMPENDIUM_CSV_URL, download_if_missing=download_if_missing)
    if not resolved:
        return []

    with open(resolved, mode="r", encoding="utf-8-sig", errors="ignore") as f:
        sample = f.read(512)
        f.seek(0)

        if "|" in sample:
            rows: list[dict[str, str]] = []
            reader = csv.reader(f, delimiter="|")
            for row in reader:
                if len(row) >= 8:
                    code, met_str, desc, cat = (c.strip() for c in row[4:8])
                elif len(row) >= 4:
                    code, met_str, cat, desc = (c.strip() for c in row[:4])
                else:
                    continue
                if code.lower() in {"codes", ""} or "compendium" in code.lower():
                    continue
                rows.append({"code": code, "met": met_str, "description": desc, "category": cat})
            return rows

        dict_reader = csv.DictReader(f)
        return [
            {
                "code": (r.get("code") or r.get("Activity Code") or r.get("CODE") or "").strip(),
                "met": (r.get("met") or r.get("METs") or r.get("MET") or "0").strip(),
                "description": (
                    r.get("description") or r.get("Specific Activity Description") or r.get("activity") or ""
                ).strip(),
                "category": (r.get("category") or r.get("Heading") or "General Activity").strip(),
            }
            for r in dict_reader
        ]


def _read_csv_dicts(path: Path | str) -> list[dict[str, str]]:
    target = Path(path)
    if not target.exists():
        return []
    with open(target, mode="r", encoding="utf-8-sig", errors="ignore") as f:
        return list(csv.DictReader(f))


def extract_kaggle_exercise_csv(path: Path | str | None = None) -> list[dict[str, str]]:
    """Đọc Kaggle exercise_dataset.csv."""
    return _read_csv_dicts(path or RAW_DATA_DIR / "exercise_dataset.csv")


def extract_megagym_csv(path: Path | str | None = None) -> list[dict[str, str]]:
    """Đọc Kaggle megaGymDataset.csv."""
    return _read_csv_dicts(path or RAW_DATA_DIR / "megaGymDataset.csv")
