"""
Bước 3 (Transform & Map MET):
Chuẩn hóa cấu trúc dữ liệu thô theo ORM model `Exercise` + gắn chỉ số MET (Ainsworth 2011)
+ suy luận nhãn chống chỉ định y khoa (`banned_for`, `clinical_reason`) phục vụ thuật toán A3.
"""

from typing import Any

from scripts.etl.asset_handler import AssetHandler

KEYWORD_MET_RULES: list[tuple[tuple[str, ...], float]] = [
    (("sprint", "burpee", "jumping jack", "jump rope", "rope jump", "rope skipping"), 9.5),
    (("running", "treadmill"), 8.3),
    (("jogging",), 7.0),
    (("rowing", "stair", "stepmill"), 7.0),
    (("bicycling", "cycling", "spinning", "bike"), 6.8),
    (("elliptical",), 5.0),
    (("skating",), 7.0),
    (("swimming",), 7.5),
    (("box jump", "box skip", "bound", "plyometric"), 7.0),
    (("clean", "snatch", "jerk", "deadlift", "squat", "thruster", "kettlebell"), 6.0),
    (("walk", "farmer's walk", "farmer walk"), 4.5),
    (("plank", "isometric"), 3.8),
    (("yoga", "pilates"), 3.0),
    (("stretch", "foam roll", "mobility", "hamstring"), 2.3),
]

CATEGORY_BASE_MET: dict[str, float] = {
    "cardio": 7.0,
    "plyometrics": 6.8,
    "strongman": 6.5,
    "olympic weightlifting": 6.0,
    "powerlifting": 6.0,
    "strength": 4.5,
    "stretching": 2.3,
}

LEVEL_ADJUSTMENT: dict[str, float] = {
    "beginner": -0.5,
    "intermediate": 0.0,
    "expert": 1.0,
}

KNEE_HIGH_LOAD_KEYWORDS = (
    "squat", "lunge", "leg extension", "box jump", "burpee", "step-up", "step up",
    "bound", "depth jump", "pistol", "sissy", "split jump", "tuck jump",
)
HYPERTENSION_VALSALVA_KEYWORDS = (
    "deadlift", "back squat", "front squat", "overhead squat", "barbell squat",
    "clean", "snatch", "jerk", "decline", "inverted", "handstand",
    "plank", "isometric hold", "atlas stone", "heavy",
)


def intensity_from_met(met: float) -> str:
    """Phân loại cường độ theo ngưỡng Ainsworth / ACSM."""
    if met < 3.0:
        return "Light"
    if met < 6.0:
        return "Moderate"
    return "Vigorous"


def map_met_for_exercise(
    name: str,
    category: str = "strength",
    level: str | None = None,
    mechanic: str | None = None,
) -> float:
    """Ước lượng chỉ số MET chuẩn hóa cho các dataset không có cột MET sẵn."""
    lower_name = name.lower()
    for keywords, met_val in KEYWORD_MET_RULES:
        if any(kw in lower_name for kw in keywords):
            return met_val

    base = CATEGORY_BASE_MET.get((category or "strength").lower(), 4.5)
    adj = LEVEL_ADJUSTMENT.get((level or "").lower(), 0.0)
    if mechanic and mechanic.lower() == "compound" and base >= 4.0:
        adj += 0.5
    return round(max(1.8, base + adj), 1)


def infer_clinical_tags(name: str, category: str = "") -> tuple[list[str], str]:
    """Suy luận `banned_for` và `clinical_reason` phục vụ bộ lọc A3."""
    lower_name = name.lower()
    lower_cat = (category or "").lower()
    banned: list[str] = []
    reasons: list[str] = []

    if any(kw in lower_name for kw in KNEE_HIGH_LOAD_KEYWORDS) or (
        lower_cat == "plyometrics" and any(kw in lower_name for kw in ("jump", "hop", "skip", "leap"))
    ):
        banned.append("knee_osteoarthritis")
        reasons.append("Gập gối sâu hoặc tiếp đất va đập mạnh nén lên sụn khớp gối")

    if any(kw in lower_name for kw in HYPERTENSION_VALSALVA_KEYWORDS) or lower_cat in {
        "powerlifting",
        "olympic weightlifting",
        "strongman",
    }:
        banned.append("hypertension")
        reasons.append("Nguy cơ nín thở Valsalva, tư thế dốc đầu hoặc co cơ tĩnh kéo dài làm tăng huyết áp")

    return banned, "; ".join(reasons)


def _normalize_str_list(values: Any) -> list[str]:
    if not values:
        return []
    return [str(v).strip() for v in values if str(v).strip()]


def transform_exercises_json(
    raw_items: list[dict[str, Any]],
    asset_handler: AssetHandler | None = None,
) -> list[dict[str, Any]]:
    """Chuẩn hóa dữ liệu từ free-exercise-db (exercises.json) sang schema ORM `Exercise`."""
    handler = asset_handler or AssetHandler()
    transformed: list[dict[str, Any]] = []

    for item in raw_items:
        ex_id = str(item.get("id") or "").strip()
        name = str(item.get("name") or "").strip()
        if not ex_id or not name:
            continue

        category = str(item.get("category") or "strength").strip().title()
        level = (item.get("level") or "").strip().lower() or None
        mechanic = (item.get("mechanic") or "").strip().lower() or None
        equipment = (item.get("equipment") or "").strip().lower() or None

        met = map_met_for_exercise(name, category=category, level=level, mechanic=mechanic)
        image_urls, thumbnail_url, video_url = handler.resolve_exercise_media(item.get("images"))
        instructions = _normalize_str_list(item.get("instructions"))
        primary_muscles = _normalize_str_list(item.get("primaryMuscles"))
        secondary_muscles = _normalize_str_list(item.get("secondaryMuscles"))
        banned_for, clinical_reason = infer_clinical_tags(name, category=category)

        desc = " ".join(instructions[:2]) if instructions else f"{category} exercise ({equipment or 'general'})"

        transformed.append({
            "code": f"EXDB_{ex_id}",
            "category": category,
            "name_vi": name,
            "name_en": name,
            "met_value": met,
            "intensity_level": intensity_from_met(met),
            "description": desc,
            "source": "free-exercise-db",
            "primary_muscles": primary_muscles,
            "secondary_muscles": secondary_muscles,
            "equipment": equipment,
            "level": level,
            "instructions": instructions,
            "image_urls": image_urls,
            "thumbnail_url": thumbnail_url,
            "video_url": video_url,
            "banned_for": banned_for,
            "clinical_reason": clinical_reason or None,
        })

    if handler.upload_enabled:
        handler.save_manifest()
    return transformed


def transform_compendium_rows(raw_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Chuẩn hóa các dòng từ Ainsworth Compendium CSV sang schema ORM `Exercise`."""
    transformed: list[dict[str, Any]] = []
    for row in raw_rows:
        code = row.get("code", "").strip()
        desc = row.get("description", "").strip()
        category = (row.get("category") or "General Activity").strip().replace("_", " ").title()
        try:
            met = float(row.get("met", "0"))
        except ValueError:
            continue
        if not code or not desc or met <= 0:
            continue

        banned_for, clinical_reason = infer_clinical_tags(desc, category=category)
        transformed.append({
            "code": code,
            "category": category,
            "name_vi": f"{desc} ({category})",
            "name_en": desc,
            "met_value": round(met, 2),
            "intensity_level": intensity_from_met(met),
            "description": f"Compendium Code {code} - {category}",
            "source": "GitHub Ainsworth 2011",
            "primary_muscles": [],
            "secondary_muscles": [],
            "equipment": None,
            "level": None,
            "instructions": [],
            "image_urls": [],
            "thumbnail_url": None,
            "video_url": None,
            "banned_for": banned_for,
            "clinical_reason": clinical_reason or None,
        })
    return transformed


def transform_kaggle_rows(raw_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    """
    Chuẩn hóa Kaggle exercise_dataset.csv sang schema ORM `Exercise`.
    Công thức quy đổi từ mức 155 lb (70.3068 kg) trong 1 giờ:
    MET = (Cal/1h @ 155 lb) / 73.822
    """
    transformed: list[dict[str, Any]] = []
    for idx, row in enumerate(raw_rows, start=1):
        name = (row.get("Activity, Exercise or Sport (1 hour)") or row.get("Activity") or "").strip()
        cal_155 = row.get("155 lb") or row.get("155")
        if not name or not cal_155:
            continue
        try:
            cal_val = float(str(cal_155).replace(",", "").strip())
            met = round(cal_val / 73.822, 1)
        except ValueError:
            continue
        if met <= 0:
            continue

        lower_name = name.lower()
        category = "Fitness & Sports"
        if any(w in lower_name for w in ("run", "jog")):
            category = "Running"
        elif any(w in lower_name for w in ("cycl", "bicycl", "bike")):
            category = "Cycling"
        elif any(w in lower_name for w in ("walk", "hike")):
            category = "Walking"
        elif any(w in lower_name for w in ("swim", "water")):
            category = "Water Activities"

        banned_for, clinical_reason = infer_clinical_tags(name, category=category)
        transformed.append({
            "code": f"KAGGLE_{idx:04d}",
            "category": category,
            "name_vi": name,
            "name_en": name,
            "met_value": met,
            "intensity_level": intensity_from_met(met),
            "description": f"Kaggle activity, cal/hour @ 155lb = {cal_val}",
            "source": "Kaggle Dataset",
            "primary_muscles": [],
            "secondary_muscles": [],
            "equipment": None,
            "level": None,
            "instructions": [],
            "image_urls": [],
            "thumbnail_url": None,
            "video_url": None,
            "banned_for": banned_for,
            "clinical_reason": clinical_reason or None,
        })
    return transformed


def transform_megagym_rows(raw_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Chuẩn hóa Kaggle megaGymDataset.csv sang schema ORM `Exercise`."""
    transformed: list[dict[str, Any]] = []
    for idx, row in enumerate(raw_rows, start=1):
        name = (row.get("Title") or "").strip()
        if not name:
            continue
        category = (row.get("Type") or "Strength").strip().title()
        level = (row.get("Level") or "").strip().lower() or None
        equipment = (row.get("Equipment") or "").strip().lower() or None
        body_part = (row.get("BodyPart") or "").strip().lower()
        desc = (row.get("Desc") or "").strip() or f"{category} exercise for {body_part or 'full body'}"

        met = map_met_for_exercise(name, category=category, level=level)
        banned_for, clinical_reason = infer_clinical_tags(name, category=category)

        transformed.append({
            "code": f"MEGAGYM_{idx:04d}",
            "category": category,
            "name_vi": name,
            "name_en": name,
            "met_value": met,
            "intensity_level": intensity_from_met(met),
            "description": desc,
            "source": "Kaggle MegaGym",
            "primary_muscles": [body_part] if body_part else [],
            "secondary_muscles": [],
            "equipment": equipment,
            "level": level,
            "instructions": [],
            "image_urls": [],
            "thumbnail_url": None,
            "video_url": None,
            "banned_for": banned_for,
            "clinical_reason": clinical_reason or None,
        })
    return transformed
