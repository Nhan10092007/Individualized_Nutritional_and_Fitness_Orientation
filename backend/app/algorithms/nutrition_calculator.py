import math
import random
from typing import List, Dict, Any, Tuple, Optional, Set
from app.schemas.nutrition import (
    MealPlanRequest,
    MealPlanResponse,
    DailyMealPlan,
    SingleMealOutput,
    SelectedFoodItem,
)

FIXED_3_MEAL_RATIOS = [
    ("Bữa Sáng", 0.30),
    ("Bữa Trưa", 0.40),
    ("Bữa Tối", 0.30),
]

# Chuẩn Viện Dinh Dưỡng TP.HCM / Bộ Y tế 2016 & WHO
NIN_CARB_MIN_PCT = 45.0
NIN_CARB_MAX_PCT = 65.0
NIN_PRO_MIN_PCT = 10.0
NIN_PRO_MAX_PCT = 35.0
NIN_FAT_MIN_PCT = 20.0
NIN_FAT_MAX_PCT = 29.9   # WHO: tổng chất béo < 30%
WHO_SAT_FAT_MAX_PCT = 10.0  # WHO: chất béo bão hòa < 10%

# Danh mục thực phẩm chuẩn hóa theo 4 nhóm: Protein, Carb, Fat, Rau củ
PROTEIN_CORE_KEYWORDS = (
    "thịt bò",
    "bắp bò",
    "ức gà",
    "đùi gà",
    "cánh gà",
    "thịt gà",
    "thịt heo",
    "sườn non",
    "ba chỉ",
    "nạc dăm",
    "tôm",
    "cá thu",
    "cá hồi",
    "cá basa",
    "cá điêu hồng",
    "trứng gà",
)
CARB_CORE_KEYWORDS = (
    "cơm trắng",
    "cơm",
    "yến mạch",
    "bánh mì sandwich",
    "bánh mì",
    "khoai lang",
    "bún",
)
RAW_GRAIN_KEYWORDS = (
    "gạo tẻ",
    "gạo nếp",
    "gạo lứt",
    "gạo thơm",
    "gạo trắng",
)
FAT_CORE_KEYWORDS = (
    "bơ đậu phộng",
    "bơ sáp",
    "bơ trái",
    "dầu oliu",
    "dầu ô-liu",
    "dầu ăn",
    "hạt điều",
    "hạnh nhân",
    "óc chó",
    "đậu phộng",
    "lạc",
)
VEGGIE_CORE_KEYWORDS = (
    "rau ",
    "cải ",
    "bắp cải",
    "súp lơ",
    "bông cải",
    "cà chua",
    "cà rốt",
    "dưa leo",
    "dưa chuột",
    "bí xanh",
    "bí đao",
    "bí đỏ",
    "xà lách",
    "nấm ",
    "giá đỗ",
)
NON_VEGGIE_KEYWORDS = (
    "sữa",
    "bơ",
    "hạt",
    "lạc",
    "đậu phộng",
    "dầu",
    "phô mai",
    "dưa hấu",
    "cam ",
    "ổi",
    "đu đủ",
    "thanh long",
    "xoài",
    "táo",
    "chuối",
)

# Phân loại đạm theo mục tiêu & bệnh lý nền (Edge Case 7)
HYPERTENSION_AVOID_PRO_KEYWORDS = (
    "ba chỉ",
    "ba rọi",
    "sườn non",
    "cánh gà",
    "đùi gà góc tư",
    "có da",
    "thịt heo xay",
    "thịt bò xay",
)
FAT_LOSS_AVOID_PRO_KEYWORDS = (
    "ba chỉ",
    "ba rọi",
    "sườn non",
    "cánh gà",
)

# Từ khóa ghép món tự nhiên theo ẩm thực Việt Nam (Edge Case 6)
BREAKFAST_CARB_KEYWORDS = ("bánh mì sandwich", "bánh mì", "yến mạch", "khoai lang", "bún")
MAIN_MEAL_CARB_KEYWORDS = ("cơm trắng", "cơm", "khoai lang", "bún")
STAPLE_RICE_KEYWORDS = ("cơm trắng", "cơm")

BREAD_PRO_KEYWORDS = ("trứng gà", "trứng", "ức gà", "thịt heo nạc thăn", "thịt bò thăn")
BREAD_VEGGIE_KEYWORDS = ("dưa leo", "dưa chuột", "cà chua", "xà lách")
BREAD_FAT_KEYWORDS = ("bơ đậu phộng", "bơ sáp", "bơ trái", "dầu oliu", "dầu ô-liu")

OATS_PRO_KEYWORDS = ("trứng gà", "trứng", "ức gà")
OATS_FAT_KEYWORDS = ("bơ đậu phộng", "hạt điều", "bơ sáp", "bơ trái")

POTATO_PRO_KEYWORDS = ("trứng gà", "trứng", "ức gà", "thịt heo nạc thăn", "tôm")
POTATO_VEGGIE_KEYWORDS = ("súp lơ", "bông cải", "dưa leo", "dưa chuột", "cà chua", "xà lách")
POTATO_FAT_KEYWORDS = ("dầu oliu", "dầu ô-liu", "bơ sáp", "bơ trái", "hạt điều")

BUN_PRO_KEYWORDS = ("thịt bò", "bắp bò", "thịt heo", "ức gà", "tôm")
BUN_VEGGIE_KEYWORDS = ("giá đỗ", "xà lách", "dưa leo", "dưa chuột", "cà chua", "rau muống")
OLIVE_OIL_KEYWORDS = ("dầu oliu", "dầu ô-liu", "dầu ăn")
MAIN_MEAL_FAT_KEYWORDS = ("dầu oliu", "dầu ô-liu", "dầu ăn", "hạt điều", "bơ sáp", "bơ trái")
FISH_KEYWORDS = ("cá ",)


def format_budget_warning(extra_vnd: float) -> str:
    """Tạo thông báo chuẩn khi ngân sách thấp hơn chi phí tối thiểu để đạt sàn calo."""
    amount = max(1, int(math.ceil(extra_vnd)))
    formatted = f"{amount:,}".replace(",", ".")
    return f"Bạn nên thêm {formatted} VNĐ để đảm bảo đủ lượng calories cần thiết cho 1 ngày."


def _matches_any(name: str, keywords: Tuple[str, ...]) -> bool:
    low = name.lower()
    return any(kw in low for kw in keywords)


def estimate_sat_fat_ratio(food_name: str) -> float:
    """
    Ước lượng tỷ lệ chất béo bão hòa trên tổng chất béo theo dữ liệu USDA / Viện Dinh Dưỡng
    để kiểm soát tiêu chuẩn WHO (chất béo bão hòa < 10% tổng năng lượng).
    """
    low = food_name.lower()
    if any(kw in low for kw in ("dầu oliu", "dầu ô-liu", "bơ sáp", "bơ trái")):
        return 0.14
    if any(kw in low for kw in ("hạt điều", "hạnh nhân", "óc chó")):
        return 0.18
    if any(kw in low for kw in ("bơ đậu phộng", "đậu phộng", "lạc")):
        return 0.20
    if any(kw in low for kw in ("cá ", "tôm")):
        return 0.23
    if "ức gà" in low:
        return 0.28
    if any(kw in low for kw in ("đùi gà", "cánh gà", "trứng")):
        return 0.31
    if any(kw in low for kw in ("ba chỉ", "ba rọi", "sườn non", "thịt heo xay", "thịt bò xay")):
        return 0.41
    if any(kw in low for kw in ("thịt bò", "bắp bò", "thịt heo", "nạc dăm")):
        return 0.36
    return 0.25


def _fmt_vi_num(val: float) -> str:
    if abs(val - round(val)) < 0.05:
        return str(int(round(val)))
    return f"{val:.1f}".replace(".", ",")


def build_unit_hint(food_name: str, grams: float) -> str:
    """
    Quy đổi đơn vị đời thực song song với gam & làm rõ sống/chín (Edge Case 1).
    """
    low = food_name.lower()
    if "trứng" in low:
        eggs = max(1, int(round(grams / 50.0)))
        return f"~{eggs} quả (cân sống)"
    if "cơm" in low:
        bowls = max(0.5, round((grams / 150.0) * 2.0) / 2.0)
        return f"~{_fmt_vi_num(bowls)} chén (đã chín)"
    if "bánh mì sandwich" in low:
        slices = max(1, int(round(grams / 30.0)))
        return f"~{slices} lát (ăn liền)"
    if "bánh mì" in low:
        loaves = max(0.5, round((grams / 100.0) * 2.0) / 2.0)
        return f"~{_fmt_vi_num(loaves)} ổ (ăn liền)"
    if "yến mạch" in low:
        return "cân khô trước khi nấu"
    if "bún" in low:
        return "bún tươi (đã chín)"
    if any(kw in low for kw in ("dầu oliu", "dầu ô-liu")):
        tsp = max(1.0, round(grams / 5.0, 1))
        return f"~{_fmt_vi_num(tsp)} muỗng cà phê (dùng chế biến)"
    if "bơ đậu phộng" in low:
        tbsp = max(0.5, round((grams / 15.0) * 2.0) / 2.0)
        return f"~{_fmt_vi_num(tbsp)} muỗng canh"
    if any(kw in low for kw in ("bơ sáp", "bơ trái")):
        if grams <= 55:
            return "~1/4 quả (thịt bơ)"
        if grams <= 80:
            return "~1/3 quả (thịt bơ)"
        return "~1/2 quả (thịt bơ)"
    if "hạt điều" in low:
        nuts = max(5, int(round(grams / 1.5)))
        return f"~{nuts} hạt"
    if any(kw in low for kw in ("luộc", "áp chảo", "nướng", "chín", "rang")):
        return "đã chế biến chín"
    if any(kw in low for kw in VEGGIE_CORE_KEYWORDS):
        return "cân tươi trước khi chế biến"
    if any(kw in low for kw in ("khoai", "thịt", "bò", "gà", "heo", "sườn", "cá ", "tôm")):
        return "cân sống trước khi nấu"
    return "định lượng tham khảo"


def build_dietary_notes(fitness_goal: Optional[str], medical_conditions: List[str]) -> List[str]:
    """Tạo ghi chú dinh dưỡng minh bạch theo hồ sơ cá nhân & chuẩn Viện Dinh Dưỡng."""
    notes: List[str] = []
    conds = {c.strip().lower() for c in (medical_conditions or [])}
    goal = (fitness_goal or "maintain").strip().lower()

    if "hypertension" in conds:
        notes.append(
            "Huyết áp cao: đã loại bỏ thịt nhiều mỡ bão hòa (ba chỉ, sườn non, da gà), "
            "giới hạn tối đa 2 quả trứng/bữa và ưu tiên cá giàu Omega-3, đạm nạc."
        )
    if goal == "fat_loss":
        notes.append(
            "Mục tiêu giảm mỡ: ưu tiên nguồn đạm nạc ít béo bão hòa để kiểm soát tổng chất béo < 30%."
        )
    notes.append(
        "Cân đối theo khuyến nghị Viện Dinh Dưỡng TP.HCM & WHO: Carb 45–65%, Đạm 10–35%, Chất béo 20–30% (< 30%), béo bão hòa < 10%."
    )
    return notes


def compute_macro_percentages(
    items: List[SelectedFoodItem],
) -> Tuple[float, float, float, float, bool]:
    """
    Tính % năng lượng từ Protein, Carbs, Fat và ước lượng % chất béo bão hòa,
    kèm cờ is_nin_compliant theo chuẩn Viện Dinh Dưỡng TP.HCM & WHO.
    """
    total_pro = sum(i.protein_g for i in items)
    total_carb = sum(i.carbs_g for i in items)
    total_fat = sum(i.fat_g for i in items)
    total_sat_fat = sum(i.fat_g * estimate_sat_fat_ratio(i.name) for i in items)

    pro_cal = total_pro * 4.0
    carb_cal = total_carb * 4.0
    fat_cal = total_fat * 9.0
    macro_cal = max(pro_cal + carb_cal + fat_cal, 1.0)

    pro_pct = round((pro_cal / macro_cal) * 100.0, 1)
    carb_pct = round((carb_cal / macro_cal) * 100.0, 1)
    fat_pct = round((fat_cal / macro_cal) * 100.0, 1)
    sat_fat_pct = round(((total_sat_fat * 9.0) / macro_cal) * 100.0, 1)

    compliant = (
        NIN_PRO_MIN_PCT <= pro_pct <= NIN_PRO_MAX_PCT
        and NIN_CARB_MIN_PCT <= carb_pct <= NIN_CARB_MAX_PCT
        and NIN_FAT_MIN_PCT <= fat_pct < 30.0
        and sat_fat_pct < WHO_SAT_FAT_MAX_PCT
    )
    return pro_pct, carb_pct, fat_pct, sat_fat_pct, compliant


def _normalize_nin_macro_targets(
    target_calories: float,
    target_protein_g: float,
    target_carbs_g: float,
    target_fat_g: float,
) -> Tuple[float, float, float, float, float, float]:
    """
    Chỉnh nhẹ tỷ lệ mục tiêu nội bộ vào vùng an toàn bên trong biên độ Viện Dinh Dưỡng & WHO
    (C: 47.5-62.5%, P: 13-32.5%, F: 21-28%) để sau làm tròn gam không bị trượt ra ngoài ranh giới.
    Trả về: (adj_pro_g, adj_carb_g, adj_fat_g, p_pct, c_pct, f_pct)
    """
    raw_p_cal = max(target_protein_g, 0.0) * 4.0
    raw_c_cal = max(target_carbs_g, 0.0) * 4.0
    raw_f_cal = max(target_fat_g, 0.0) * 9.0
    raw_sum = raw_p_cal + raw_c_cal + raw_f_cal

    if raw_sum <= 0:
        raw_p_pct, raw_c_pct, raw_f_pct = 0.22, 0.52, 0.26
    else:
        raw_p_pct = raw_p_cal / raw_sum
        raw_c_pct = raw_c_cal / raw_sum
        raw_f_pct = raw_f_cal / raw_sum

    f_pct = min(max(raw_f_pct, 0.215), 0.275)
    rem = 1.0 - f_pct
    c_low = max(0.475, rem - 0.325)
    c_high = min(0.625, rem - 0.13)
    c_pct = min(max(raw_c_pct, c_low), c_high)
    p_pct = round(1.0 - f_pct - c_pct, 4)

    adj_pro_g = (target_calories * p_pct) / 4.0
    adj_carb_g = (target_calories * c_pct) / 4.0
    adj_fat_g = (target_calories * f_pct) / 9.0
    return adj_pro_g, adj_carb_g, adj_fat_g, p_pct * 100.0, c_pct * 100.0, f_pct * 100.0


def _get_portion_rules(
    food_name: str,
    role: str,
    meal_target_cal: float,
    is_hypertension: bool = False,
) -> Tuple[float, float, int]:
    """
    Trả về (min_g, max_g, step_g) thực tế cho từng loại thực phẩm (Edge Cases 1, 2, 3).
    """
    low = food_name.lower()
    is_high_cal = meal_target_cal >= 1050.0
    is_low_cal = meal_target_cal <= 400.0

    if role == "protein":
        if "trứng" in low:
            # Trứng làm tròn theo quả (50g), tối đa 2 quả (huyết áp cao / bữa nhỏ) hoặc 3 quả
            max_egg = 100.0 if (is_hypertension or is_low_cal) else 150.0
            return 50.0, max_egg, 50
        max_p = 320.0 if is_high_cal else (180.0 if is_low_cal else 270.0)
        return 60.0, max_p, 1

    if role == "carb":
        if "yến mạch" in low:
            # Yến mạch cân khô: không vượt quá 90g/bữa (110g nếu bulk rất cao)
            return 35.0, (110.0 if is_high_cal else 90.0), 1
        if "bánh mì sandwich" in low:
            # Làm tròn theo lát (30g/lát): 1-4 lát
            min_s = 30.0 if is_low_cal else 60.0
            max_s = 150.0 if is_high_cal else 120.0
            return min_s, max_s, 30
        if "bánh mì" in low:
            return (50.0 if is_low_cal else 60.0), (160.0 if is_high_cal else 140.0), 1
        if "cơm" in low:
            # Không để phần cơm kỳ quặc dưới nửa chén (80g) và không dồn 700g vào 1 bữa
            max_c = 440.0 if is_high_cal else 360.0
            return 80.0, max_c, 1
        # Khoai lang / bún
        max_other_c = 420.0 if is_high_cal else 350.0
        return 80.0, max_other_c, 1

    if role == "fat":
        if any(kw in low for kw in ("dầu oliu", "dầu ô-liu", "dầu ăn")):
            return 5.0, (25.0 if is_high_cal else 20.0), 1
        if any(kw in low for kw in ("bơ đậu phộng", "hạt điều", "hạnh nhân", "óc chó")):
            return 10.0, (40.0 if is_high_cal else 32.0), 1
        if any(kw in low for kw in ("bơ sáp", "bơ trái")):
            return 40.0, (110.0 if is_high_cal else 90.0), 1
        return 10.0, 60.0, 1

    # Veggie
    return (80.0 if is_low_cal else 90.0), 150.0, 1


def _round_grams_up(grams: float, step_g: int = 1) -> float:
    """Làm tròn định lượng gam LÊN hàng đơn vị (hoặc bội số quả/lát nguyên)."""
    if grams <= 0:
        return 0.0
    step = max(1, int(step_g))
    return float(math.ceil(grams / step) * step)


def categorize_foods_by_macro(food_db: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Subtask 1: Phân nhóm thực phẩm chuẩn xác thành 4 nhóm:
    1. Chất béo tốt (fat) | 2. Tinh bột (carb) | 3. Đạm (protein) | 4. Rau củ (veggie)
    """
    if not food_db:
        raise ValueError("Danh sách thực phẩm đầu vào đang trống.")

    used_ids: Set[int] = set()

    # 1. Nhóm Chất béo tốt (tách trước để bơ đậu phộng / hạt điều không bị nhầm sang Đạm)
    fat_sources = [f for f in food_db if _matches_any(f["name"], FAT_CORE_KEYWORDS)]
    if not fat_sources:
        fat_sources = [
            f
            for f in food_db
            if f["fat_g"] >= 14
            and f["protein_g"] < 15
            and f["carbs_g"] < 20
            and not _matches_any(f["name"], PROTEIN_CORE_KEYWORDS)
        ]
    fat_sources.sort(key=lambda x: x["cost_per_100g"] / max(x["calories"], 1.0))
    used_ids |= {f["id"] for f in fat_sources}

    # 2. Nhóm Tinh bột (cơm trắng, yến mạch, bánh mì sandwich, khoai lang, bún)
    has_cooked_rice = any(
        _matches_any(f["name"], STAPLE_RICE_KEYWORDS) and not _matches_any(f["name"], RAW_GRAIN_KEYWORDS)
        for f in food_db
    )
    carb_sources = [
        f
        for f in food_db
        if f["id"] not in used_ids
        and _matches_any(f["name"], CARB_CORE_KEYWORDS)
        and not (has_cooked_rice and _matches_any(f["name"], RAW_GRAIN_KEYWORDS))
    ]
    if not carb_sources:
        carb_sources = [
            f
            for f in food_db
            if f["id"] not in used_ids and f["carbs_g"] >= 20 and f["protein_g"] < 15
        ]
    carb_sources.sort(key=lambda x: x["cost_per_100g"] / max(x["calories"], 1.0))
    used_ids |= {f["id"] for f in carb_sources}

    # 3. Nhóm Đạm (thịt bò, thịt gà, thịt heo, tôm, cá thu/hồi/basa/điêu hồng, trứng gà)
    protein_sources = [
        f
        for f in food_db
        if f["id"] not in used_ids
        and _matches_any(f["name"], PROTEIN_CORE_KEYWORDS)
        and "nấm" not in f["name"].lower()
    ]
    if not protein_sources:
        protein_sources = [
            f
            for f in food_db
            if f["id"] not in used_ids and f["protein_g"] >= 12
        ]
    protein_sources.sort(key=lambda x: x["cost_per_100g"] / max(x["protein_g"], 1.0))
    used_ids |= {f["id"] for f in protein_sources}

    if not (protein_sources and carb_sources):
        raise ValueError("Cơ sở dữ liệu thiếu nguồn Protein hoặc Tinh bột để cân bằng bữa ăn.")

    # 4. Nhóm Rau củ xanh (loại trừ trái cây, sữa, hạt)
    veggie_sources = [
        f
        for f in food_db
        if f["id"] not in used_ids
        and _matches_any(f["name"], VEGGIE_CORE_KEYWORDS)
        and not _matches_any(f["name"], NON_VEGGIE_KEYWORDS)
    ]
    if not veggie_sources:
        veggie_sources = [
            f
            for f in food_db
            if f["id"] not in used_ids
            and f["calories"] <= 55
            and f["fat_g"] < 5
            and not _matches_any(f["name"], NON_VEGGIE_KEYWORDS)
        ]
    veggie_sources.sort(key=lambda x: x["cost_per_100g"])

    if not fat_sources:
        fat_sources = sorted(
            [f for f in food_db if f["id"] not in used_ids and f["fat_g"] >= 5],
            key=lambda x: x["cost_per_100g"] / max(x["calories"], 1.0),
        )

    return {
        "protein": protein_sources,
        "carb": carb_sources,
        "fat": fat_sources,
        "veggie": veggie_sources,
    }


def _filter_proteins_for_profile(
    proteins: List[Dict[str, Any]],
    fitness_goal: Optional[str],
    medical_conditions: List[str],
) -> List[Dict[str, Any]]:
    """
    Lọc nguồn đạm theo bệnh lý nền (huyết áp cao) và mục tiêu (giảm mỡ) (Edge Case 7).
    Luôn giữ fallback an toàn nếu bộ dữ liệu quá nhỏ.
    """
    if not proteins:
        return []

    conds = {c.strip().lower() for c in (medical_conditions or [])}
    goal = (fitness_goal or "maintain").strip().lower()
    filtered = list(proteins)

    if "hypertension" in conds:
        lean_heart = [p for p in filtered if not _matches_any(p["name"], HYPERTENSION_AVOID_PRO_KEYWORDS)]
        if lean_heart:
            filtered = lean_heart

    if goal == "fat_loss":
        lean_cut = [p for p in filtered if not _matches_any(p["name"], FAT_LOSS_AVOID_PRO_KEYWORDS)]
        if lean_cut:
            filtered = lean_cut

    return filtered


def _pick_cost_aware_pool(items: List[Dict[str, Any]], daily_budget_vnd: float) -> List[Dict[str, Any]]:
    """Giữ các món tối ưu chi phí khi ngân sách thấp, mở rộng toàn bộ khi ngân sách thoải mái."""
    if not items:
        return []
    affordable = [f for f in items if f["cost_per_100g"] <= daily_budget_vnd * 0.45]
    base_pool = affordable if len(affordable) >= 2 else items
    limit = 10 if daily_budget_vnd <= 100000 else len(base_pool)
    return base_pool[: max(3, min(len(base_pool), limit))]


def _pick_food_for_meal(
    pool: List[Dict[str, Any]],
    rng: random.Random,
    preferred_keywords: Tuple[str, ...] = (),
    avoid_ids: Optional[Set[int]] = None,
    target_cal_density: Optional[float] = None,
    prefer_lean: bool = False,
) -> Optional[Dict[str, Any]]:
    """Chọn ngẫu nhiên có trọng số theo từng buổi, ưu tiên không trùng món vừa ăn."""
    if not pool:
        return None

    avoid_ids = avoid_ids or set()
    candidates = pool

    if preferred_keywords:
        matched = [f for f in pool if _matches_any(f["name"], preferred_keywords)]
        if matched:
            candidates = matched

    non_repeated = [f for f in candidates if f["id"] not in avoid_ids]
    active_pool = non_repeated if non_repeated else candidates

    if len(active_pool) == 1:
        return active_pool[0]

    weights: List[float] = []
    for f in active_pool:
        w = 1.0
        if target_cal_density and target_cal_density > 0:
            diff_ratio = abs(f["calories"] - target_cal_density) / max(target_cal_density, 50.0)
            w = 1.0 / (1.0 + 0.6 * diff_ratio)
        if prefer_lean and f["fat_g"] > 12.0:
            w *= 0.45
        weights.append(max(w, 0.15))

    return rng.choices(active_pool, weights=weights, k=1)[0]


def _build_selected_item(food_obj: Dict[str, Any], grams: float, step_g: int = 1) -> SelectedFoodItem:
    """Tạo SelectedFoodItem với định lượng gam luôn được làm tròn lên hàng đơn vị (hoặc bội số thực tế)."""
    ceiled_grams = _round_grams_up(grams, step_g)
    factor = ceiled_grams / 100.0
    return SelectedFoodItem(
        food_id=food_obj["id"],
        name=food_obj["name"],
        grams=ceiled_grams,
        unit_hint=build_unit_hint(food_obj["name"], ceiled_grams),
        calories=round(food_obj["calories"] * factor, 1),
        protein_g=round(food_obj["protein_g"] * factor, 1),
        carbs_g=round(food_obj["carbs_g"] * factor, 1),
        fat_g=round(food_obj["fat_g"] * factor, 1),
        cost_vnd=round(food_obj["cost_per_100g"] * factor, 0),
    )


def _sum_slot_metrics(slot: Dict[str, Any]) -> Tuple[float, float, float, float, float]:
    """Tính tổng (cal, pro, carb, fat, cost) của 1 meal slot từ các role hiện tại."""
    cal = pro = carb = fat = cost = 0.0
    for role in ("carb", "protein", "veggie", "fat"):
        entry = slot["roles"].get(role)
        if not entry:
            continue
        f, g = entry
        if not f or g <= 0:
            continue
        factor = g / 100.0
        cal += round(f["calories"] * factor, 1)
        pro += round(f["protein_g"] * factor, 1)
        carb += round(f["carbs_g"] * factor, 1)
        fat += round(f["fat_g"] * factor, 1)
        cost += round(f["cost_per_100g"] * factor, 0)
    return cal, pro, carb, fat, cost


def _init_meal_slot(
    meal_name: str,
    ratio: float,
    is_breakfast: bool,
    combo: Tuple[Dict[str, Any], Dict[str, Any], Optional[Dict[str, Any]], Optional[Dict[str, Any]]],
    meal_target_cal: float,
    meal_target_pro: float,
    meal_target_carb: float,
    meal_target_fat: float,
    is_hypertension: bool,
) -> Dict[str, Any]:
    """Khởi tạo định lượng hợp lý cho 1 bữa ăn theo phần ăn thực tế và làm tròn lên."""
    c_food, p_food, v_food, f_food = combo

    p_min, p_max, p_step = _get_portion_rules(p_food["name"], "protein", meal_target_cal, is_hypertension)
    c_min, c_max, c_step = _get_portion_rules(c_food["name"], "carb", meal_target_cal, is_hypertension)

    raw_p = (meal_target_pro / max(p_food["protein_g"], 1.0)) * 100.0
    p_grams = _round_grams_up(min(max(raw_p, p_min), p_max), p_step)

    rem_carb = max(meal_target_carb - (p_food["carbs_g"] * p_grams / 100.0), 10.0)
    raw_c = (rem_carb / max(c_food["carbs_g"], 1.0)) * 100.0
    c_grams = _round_grams_up(min(max(raw_c, c_min), c_max), c_step)

    v_grams = 0.0
    if v_food:
        v_min, v_max, v_step = _get_portion_rules(v_food["name"], "veggie", meal_target_cal, is_hypertension)
        default_v = 90.0 if is_breakfast else 115.0
        if meal_target_cal <= 400.0:
            default_v = 80.0 if is_breakfast else 95.0
        v_grams = _round_grams_up(min(max(default_v, v_min), v_max), v_step)

    base_fat = (
        (p_food["fat_g"] * p_grams / 100.0)
        + (c_food["fat_g"] * c_grams / 100.0)
        + ((v_food["fat_g"] * v_grams / 100.0) if v_food else 0.0)
    )
    rem_fat = meal_target_fat - base_fat
    f_grams = 0.0
    if f_food and f_food["id"] not in {p_food["id"], c_food["id"], v_food["id"] if v_food else -1}:
        f_min, f_max, f_step = _get_portion_rules(f_food["name"], "fat", meal_target_cal, is_hypertension)
        if rem_fat >= 2.0 and f_food["fat_g"] > 0:
            raw_f = (rem_fat / f_food["fat_g"]) * 100.0
            f_grams = _round_grams_up(min(max(raw_f, f_min), f_max), f_step)

    roles: Dict[str, Tuple[Optional[Dict[str, Any]], float]] = {
        "carb": (c_food, c_grams),
        "protein": (p_food, p_grams),
        "veggie": (v_food, v_grams),
        "fat": (f_food, f_grams),
    }

    return {
        "meal_name": meal_name,
        "ratio": ratio,
        "is_breakfast": is_breakfast,
        "target_cal": meal_target_cal,
        "roles": roles,
    }


def _sync_lunch_dinner_fat_parity(meal_slots: List[Dict[str, Any]], is_hypertension: bool) -> None:
    """
    Bảo đảm Bữa Trưa (idx 1) và Bữa Tối (idx 2) luôn có CÙNG danh sách món ăn 100% (Edge Case 6):
    nếu 1 trong 2 bữa có món chất béo (ví dụ dầu oliu) thì bữa kia cũng có ít nhất f_min.
    """
    if len(meal_slots) < 3:
        return
    lunch = meal_slots[1]
    dinner = meal_slots[2]
    lf, lg = lunch["roles"]["fat"]
    df, dg = dinner["roles"]["fat"]
    if not lf or not df or lf["id"] != df["id"]:
        return

    if lg > 0 and dg <= 0:
        f_min, _, f_step = _get_portion_rules(df["name"], "fat", dinner["target_cal"], is_hypertension)
        dinner["roles"]["fat"] = (df, _round_grams_up(f_min, f_step))
    elif dg > 0 and lg <= 0:
        f_min, _, f_step = _get_portion_rules(lf["name"], "fat", lunch["target_cal"], is_hypertension)
        lunch["roles"]["fat"] = (lf, _round_grams_up(f_min, f_step))


def _day_totals_from_slots(meal_slots: List[Dict[str, Any]]) -> Dict[str, float]:
    total_cal = total_pro = total_carb = total_fat = total_cost = total_sat_fat = 0.0
    for slot in meal_slots:
        for role in ("carb", "protein", "veggie", "fat"):
            f, g = slot["roles"][role]
            if not f or g <= 0:
                continue
            factor = g / 100.0
            i_fat = round(f["fat_g"] * factor, 1)
            total_cal += round(f["calories"] * factor, 1)
            total_pro += round(f["protein_g"] * factor, 1)
            total_carb += round(f["carbs_g"] * factor, 1)
            total_fat += i_fat
            total_sat_fat += i_fat * estimate_sat_fat_ratio(f["name"])
            total_cost += round(f["cost_per_100g"] * factor, 0)

    pro_cal = total_pro * 4.0
    carb_cal = total_carb * 4.0
    fat_cal = total_fat * 9.0
    macro_cal = max(pro_cal + carb_cal + fat_cal, 1.0)

    pro_pct = round((pro_cal / macro_cal) * 100.0, 1)
    carb_pct = round((carb_cal / macro_cal) * 100.0, 1)
    fat_pct = round((fat_cal / macro_cal) * 100.0, 1)
    sat_fat_pct = round(((total_sat_fat * 9.0) / macro_cal) * 100.0, 1)

    is_compliant = (
        NIN_PRO_MIN_PCT <= pro_pct <= NIN_PRO_MAX_PCT
        and NIN_CARB_MIN_PCT <= carb_pct <= NIN_CARB_MAX_PCT
        and NIN_FAT_MIN_PCT <= fat_pct < 30.0
        and sat_fat_pct < WHO_SAT_FAT_MAX_PCT
    )
    return {
        "cal": total_cal,
        "pro": total_pro,
        "carb": total_carb,
        "fat": total_fat,
        "cost": total_cost,
        "pro_pct": pro_pct,
        "carb_pct": carb_pct,
        "fat_pct": fat_pct,
        "sat_fat_pct": sat_fat_pct,
        "is_compliant": is_compliant,
    }


def _adjust_role_distributed(
    meal_slots: List[Dict[str, Any]],
    role: str,
    direction: int,
    is_hypertension: bool,
    allow_remove_fat: bool = False,
    relax_max_factor: float = 1.0,
) -> bool:
    """
    Điều chỉnh khối lượng của `role` (direction = +1 tăng / -1 giảm) phân bổ đều cho bữa đang lệch
    nhiều nhất so với tỷ lệ 30/40/30 (Edge Case 2 - không bao giờ dồn hết vào 1 món).
    Luôn giữ tính đồng nhất món giữa Bữa Trưa và Bữa Tối (Edge Case 6).
    """
    day_cal = max(sum(_sum_slot_metrics(s)[0] for s in meal_slots), 1.0)

    # Sắp xếp thứ tự ưu tiên bữa: nếu tăng -> ưu tiên bữa đang hụt tỷ lệ calo nhất; nếu giảm -> bữa đang thừa nhất
    order = sorted(
        range(len(meal_slots)),
        key=lambda idx: (_sum_slot_metrics(meal_slots[idx])[0] / day_cal) - meal_slots[idx]["ratio"],
        reverse=(direction < 0),
    )

    for idx in order:
        slot = meal_slots[idx]
        f, g = slot["roles"][role]
        if not f:
            continue

        min_g, max_g, step_g = _get_portion_rules(f["name"], role, slot["target_cal"], is_hypertension)
        # Không bao giờ nới trần số quả trứng (luôn giữ tối đa 2-3 quả/bữa kể cả khi bulk cao)
        eff_max = max_g if "trứng" in f["name"].lower() else (max_g * relax_max_factor)

        # Chọn bước nhảy vừa phải (tinh hơn với dầu ăn / hạt)
        if step_g > 1:
            delta = float(step_g)
        elif role == "fat" and f["fat_g"] >= 80:
            delta = 2.0
        elif role == "fat":
            delta = 5.0
        else:
            delta = 10.0

        if direction > 0:
            if g <= 0:
                if role != "fat":
                    continue
                new_g = _round_grams_up(min_g, step_g)
                slot["roles"][role] = (f, new_g)
                if idx in (1, 2):
                    _sync_lunch_dinner_fat_parity(meal_slots, is_hypertension)
                return True
            if g + step_g <= eff_max:
                inc = min(delta, eff_max - g)
                new_g = _round_grams_up(g + max(float(step_g), inc), step_g)
                if new_g <= eff_max + 0.1:
                    slot["roles"][role] = (f, new_g)
                    return True
        else:
            if g <= 0:
                continue
            if g - step_g >= min_g:
                dec = min(delta, g - min_g)
                # Giảm theo bội số step_g
                steps_down = max(1, int(dec // step_g))
                new_g = max(min_g, g - steps_down * step_g)
                if new_g < g:
                    slot["roles"][role] = (f, new_g)
                    return True
            elif allow_remove_fat and role == "fat":
                # Nếu xóa chất béo ở Trưa hoặc Tối -> xóa ĐỒNG THỜI cả Trưa & Tối để giữ 100% cùng món
                if idx in (1, 2) and len(meal_slots) >= 3:
                    lf, _ = meal_slots[1]["roles"]["fat"]
                    df, _ = meal_slots[2]["roles"]["fat"]
                    meal_slots[1]["roles"]["fat"] = (lf, 0.0)
                    meal_slots[2]["roles"]["fat"] = (df, 0.0)
                else:
                    slot["roles"]["fat"] = (f, 0.0)
                return True

    return False


def _rebalance_day_slots(
    meal_slots: List[Dict[str, Any]],
    target_calories: float,
    min_calories_floor: float,
    target_p_pct: float,
    target_c_pct: float,
    target_f_pct: float,
    daily_budget_vnd: float,
    is_hypertension: bool,
) -> Dict[str, float]:
    """
    Cân bằng toàn ngày theo 3 ưu tiên nghiêm ngặt:
    1. Đạt ngưỡng calo an toàn >= min_calories_floor (BMR / Hard Floor) & bám sát target_calories.
    2. Tuân thủ chuẩn Viện Dinh Dưỡng TP.HCM & WHO:
       Carb 45-65%, Protein 10-35%, Lipid 20-30% (<30%), Béo bão hòa < 10%.
    3. Tối ưu chi phí trong daily_budget_vnd (nhưng KHÔNG phá vỡ ưu tiên 1 & 2).
    """
    _sync_lunch_dinner_fat_parity(meal_slots, is_hypertension)

    low_cal_tol = max(min_calories_floor, target_calories * 0.95)
    high_cal_tol = max(min_calories_floor * 1.06, target_calories * 1.05)

    # Vòng 1: Cân chỉnh Calo bám sát mục tiêu (phân bổ đều cả 3 bữa)
    for _ in range(45):
        m = _day_totals_from_slots(meal_slots)
        if m["cal"] < low_cal_tol:
            # Ưu tiên tăng nhóm macro đang thấp hơn mục tiêu (nhưng không đẩy fat >= 29%)
            candidates = [
                ("carb", target_c_pct - m["carb_pct"]),
                ("protein", target_p_pct - m["pro_pct"]),
                ("fat", (target_f_pct - m["fat_pct"]) if m["fat_pct"] < 28.0 else -99.0),
            ]
            candidates.sort(key=lambda x: x[1], reverse=True)
            moved = False
            for role, _ in candidates:
                if _adjust_role_distributed(meal_slots, role, +1, is_hypertension):
                    moved = True
                    break
            if not moved:
                # Cho phép nới mềm mức trần khẩu phần nếu là user bulk cực cao (>3200 kcal)
                for role, _ in candidates:
                    if _adjust_role_distributed(meal_slots, role, +1, is_hypertension, relax_max_factor=1.35):
                        moved = True
                        break
            if not moved:
                break
        elif m["cal"] > high_cal_tol:
            candidates = [
                ("fat", m["fat_pct"] - target_f_pct),
                ("protein", m["pro_pct"] - target_p_pct),
                ("carb", m["carb_pct"] - target_c_pct),
            ]
            candidates.sort(key=lambda x: x[1], reverse=True)
            moved = False
            for role, _ in candidates:
                if _adjust_role_distributed(
                    meal_slots,
                    role,
                    -1,
                    is_hypertension,
                    allow_remove_fat=(m["fat_pct"] > 28.5),
                ):
                    moved = True
                    break
            if not moved:
                break
        else:
            break

    # Vòng 2: Kiểm soát ngân sách (chỉ cắt giảm khi vẫn giữ được calo >= min_calories_floor)
    if daily_budget_vnd > 0:
        for _ in range(25):
            m = _day_totals_from_slots(meal_slots)
            if m["cost"] <= daily_budget_vnd:
                break
            if min_calories_floor > 0 and m["cal"] <= min_calories_floor * 1.015:
                break
            # Cắt giảm đạm đắt trước (nếu còn biên độ trên 13%), sau đó mới tới chất béo/tinh bột
            trim_order = []
            if m["pro_pct"] > 14.0:
                trim_order.append("protein")
            if m["fat_pct"] > 21.5:
                trim_order.append("fat")
            if m["carb_pct"] > 48.0:
                trim_order.append("carb")
            moved = False
            for role in trim_order:
                if _adjust_role_distributed(meal_slots, role, -1, is_hypertension):
                    after = _day_totals_from_slots(meal_slots)
                    if min_calories_floor > 0 and after["cal"] < min_calories_floor:
                        _adjust_role_distributed(meal_slots, role, +1, is_hypertension)
                        continue
                    moved = True
                    break
            if not moved:
                break

    # Vòng 3: Sửa triệt để mọi sai lệch Macro so với Viện Dinh Dưỡng TP.HCM & WHO
    for _ in range(60):
        m = _day_totals_from_slots(meal_slots)
        if m["is_compliant"] and (min_calories_floor <= 0 or m["cal"] >= min_calories_floor):
            break

        changed = False

        # 3a. Tổng chất béo >= 30% HOẶC chất béo bão hòa >= 10%
        if m["fat_pct"] >= 29.9 or m["sat_fat_pct"] >= WHO_SAT_FAT_MAX_PCT:
            if _adjust_role_distributed(meal_slots, "fat", -1, is_hypertension, allow_remove_fat=True):
                changed = True
            elif _adjust_role_distributed(meal_slots, "protein", -1, is_hypertension):
                changed = True
            # Bù lại năng lượng bằng Carb nếu calo tụt xuống gần sàn
            after = _day_totals_from_slots(meal_slots)
            if after["cal"] < max(min_calories_floor, target_calories * 0.94) and after["carb_pct"] < 63.0:
                _adjust_role_distributed(meal_slots, "carb", +1, is_hypertension, relax_max_factor=1.25)
                changed = True

        # 3b. Chất béo < 20%
        elif m["fat_pct"] < NIN_FAT_MIN_PCT:
            if _adjust_role_distributed(meal_slots, "fat", +1, is_hypertension, relax_max_factor=1.25):
                changed = True
                after = _day_totals_from_slots(meal_slots)
                if after["cal"] > high_cal_tol:
                    if after["carb_pct"] > 48.0:
                        _adjust_role_distributed(meal_slots, "carb", -1, is_hypertension)
                    elif after["pro_pct"] > 15.0:
                        _adjust_role_distributed(meal_slots, "protein", -1, is_hypertension)

        # 3c. Carbohydrate < 45%
        elif m["carb_pct"] < NIN_CARB_MIN_PCT:
            if _adjust_role_distributed(meal_slots, "carb", +1, is_hypertension, relax_max_factor=1.35):
                changed = True
            after = _day_totals_from_slots(meal_slots)
            if after["cal"] > high_cal_tol:
                if after["pro_pct"] > 16.0 and _adjust_role_distributed(meal_slots, "protein", -1, is_hypertension):
                    changed = True
                elif after["fat_pct"] > 22.0 and _adjust_role_distributed(meal_slots, "fat", -1, is_hypertension):
                    changed = True

        # 3d. Carbohydrate > 65%
        elif m["carb_pct"] > NIN_CARB_MAX_PCT:
            if _adjust_role_distributed(meal_slots, "carb", -1, is_hypertension):
                changed = True
            after = _day_totals_from_slots(meal_slots)
            if after["cal"] < low_cal_tol:
                if after["pro_pct"] < 33.0 and _adjust_role_distributed(meal_slots, "protein", +1, is_hypertension):
                    changed = True
                elif after["fat_pct"] < 28.0 and _adjust_role_distributed(meal_slots, "fat", +1, is_hypertension):
                    changed = True

        # 3e. Protein > 35%
        elif m["pro_pct"] > NIN_PRO_MAX_PCT:
            if _adjust_role_distributed(meal_slots, "protein", -1, is_hypertension):
                changed = True
            if _day_totals_from_slots(meal_slots)["cal"] < low_cal_tol:
                if _adjust_role_distributed(meal_slots, "carb", +1, is_hypertension, relax_max_factor=1.35):
                    changed = True

        # 3f. Protein < 10%
        elif m["pro_pct"] < NIN_PRO_MIN_PCT:
            if _adjust_role_distributed(meal_slots, "protein", +1, is_hypertension, relax_max_factor=1.25):
                changed = True

        # 3g. Bảo đảm cứng sàn calo (BMR / Hard Floor) phân bổ đều cho 3 bữa
        m_now = _day_totals_from_slots(meal_slots)
        if min_calories_floor > 0 and m_now["cal"] < min_calories_floor:
            boost_order = [
                ("carb", target_c_pct - m_now["carb_pct"]),
                ("protein", target_p_pct - m_now["pro_pct"]),
                ("fat", (target_f_pct - m_now["fat_pct"]) if m_now["fat_pct"] < 28.5 else -99.0),
            ]
            boost_order.sort(key=lambda x: x[1], reverse=True)
            for role, _ in boost_order:
                if _adjust_role_distributed(meal_slots, role, +1, is_hypertension, relax_max_factor=1.5):
                    changed = True
                    break

        if not changed:
            break

    # Chốt đồng nhất món Trưa = Tối và kiểm tra cuối sàn calo
    _sync_lunch_dinner_fat_parity(meal_slots, is_hypertension)
    final_m = _day_totals_from_slots(meal_slots)
    if min_calories_floor > 0 and final_m["cal"] < min_calories_floor:
        for _ in range(30):
            final_m = _day_totals_from_slots(meal_slots)
            if final_m["cal"] >= min_calories_floor:
                break
            role = "carb" if final_m["carb_pct"] <= 62.0 else ("protein" if final_m["pro_pct"] <= 33.0 else "fat")
            if not _adjust_role_distributed(meal_slots, role, +1, is_hypertension, relax_max_factor=1.8):
                break

    return _day_totals_from_slots(meal_slots)


def _evaluate_day_plan(
    breakfast_combo: Tuple[Dict[str, Any], Dict[str, Any], Optional[Dict[str, Any]], Optional[Dict[str, Any]]],
    main_combo: Tuple[Dict[str, Any], Dict[str, Any], Optional[Dict[str, Any]], Optional[Dict[str, Any]]],
    target_calories: float,
    min_calories_floor: float,
    target_protein_g: float,
    target_carbs_g: float,
    target_fat_g: float,
    target_p_pct: float,
    target_c_pct: float,
    target_f_pct: float,
    daily_budget_vnd: float,
    is_hypertension: bool,
) -> Dict[str, Any]:
    """
    Sinh 1 ngày ăn hoàn chỉnh:
    - Bữa Sáng dùng breakfast_combo (30%)
    - Bữa Trưa (40%) và Bữa Tối (30%) DÙNG CHUNG 100% món ăn trong main_combo
    - Cân bằng calo & macro toàn ngày đạt chuẩn Viện Dinh Dưỡng & WHO
    """
    meal_slots: List[Dict[str, Any]] = []
    for idx, (meal_name, ratio) in enumerate(FIXED_3_MEAL_RATIOS):
        is_breakfast = idx == 0
        combo = breakfast_combo if is_breakfast else main_combo
        slot = _init_meal_slot(
            meal_name=meal_name,
            ratio=ratio,
            is_breakfast=is_breakfast,
            combo=combo,
            meal_target_cal=target_calories * ratio,
            meal_target_pro=target_protein_g * ratio,
            meal_target_carb=target_carbs_g * ratio,
            meal_target_fat=target_fat_g * ratio,
            is_hypertension=is_hypertension,
        )
        meal_slots.append(slot)

    metrics = _rebalance_day_slots(
        meal_slots=meal_slots,
        target_calories=target_calories,
        min_calories_floor=min_calories_floor,
        target_p_pct=target_p_pct,
        target_c_pct=target_c_pct,
        target_f_pct=target_f_pct,
        daily_budget_vnd=daily_budget_vnd,
        is_hypertension=is_hypertension,
    )

    meal_entries: List[Dict[str, Any]] = []
    for slot in meal_slots:
        items: List[SelectedFoodItem] = []
        for role in ("carb", "protein", "veggie", "fat"):
            f, g = slot["roles"][role]
            if not f or g <= 0:
                continue
            _, _, step_g = _get_portion_rules(f["name"], role, slot["target_cal"], is_hypertension)
            items.append(_build_selected_item(f, g, step_g))

        meal_entries.append(
            {
                "meal_name": slot["meal_name"],
                "items": items,
                "cal": sum(i.calories for i in items),
                "pro": sum(i.protein_g for i in items),
                "carb": sum(i.carbs_g for i in items),
                "fat": sum(i.fat_g for i in items),
                "cost": sum(i.cost_vnd for i in items),
            }
        )

    all_items = [it for m in meal_entries for it in m["items"]]
    pro_pct, carb_pct, fat_pct, sat_fat_pct, is_compliant = compute_macro_percentages(all_items)

    return {
        "meals": meal_entries,
        "cal": sum(m["cal"] for m in meal_entries),
        "pro": sum(m["pro"] for m in meal_entries),
        "carb": sum(m["carb"] for m in meal_entries),
        "fat": sum(m["fat"] for m in meal_entries),
        "cost": sum(m["cost"] for m in meal_entries),
        "pro_pct": pro_pct,
        "carb_pct": carb_pct,
        "fat_pct": fat_pct,
        "sat_fat_pct": sat_fat_pct,
        "is_compliant": is_compliant,
        "breakfast_combo": breakfast_combo,
        "main_combo": main_combo,
    }


def _sample_breakfast_combo(
    carb_pool: List[Dict[str, Any]],
    protein_pool: List[Dict[str, Any]],
    veggie_pool: List[Dict[str, Any]],
    fat_pool: List[Dict[str, Any]],
    rng: random.Random,
    avoid_c: Set[int],
    avoid_p: Set[int],
    avoid_v: Set[int],
    desired_carb_cal: float,
    desired_pro_cal: float,
    prefer_lean: bool,
) -> Tuple[Dict[str, Any], Dict[str, Any], Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Ghép bữa sáng theo các mẫu bữa sáng tự nhiên của người Việt (Edge Case 6)."""
    c_food = _pick_food_for_meal(
        carb_pool,
        rng,
        BREAKFAST_CARB_KEYWORDS,
        avoid_ids=avoid_c,
        target_cal_density=desired_carb_cal,
    )
    c_name = (c_food["name"] if c_food else "").lower()

    if "yến mạch" in c_name:
        p_food = _pick_food_for_meal(protein_pool, rng, OATS_PRO_KEYWORDS, avoid_ids=avoid_p, prefer_lean=prefer_lean)
        v_food = None  # Không ghép rau canh với yến mạch
        f_food = _pick_food_for_meal(fat_pool, rng, OATS_FAT_KEYWORDS)
    elif "bánh mì" in c_name:
        p_food = _pick_food_for_meal(protein_pool, rng, BREAD_PRO_KEYWORDS, avoid_ids=avoid_p, prefer_lean=prefer_lean)
        v_food = _pick_food_for_meal(veggie_pool, rng, BREAD_VEGGIE_KEYWORDS, avoid_ids=avoid_v)
        f_food = _pick_food_for_meal(fat_pool, rng, BREAD_FAT_KEYWORDS)
    elif "bún" in c_name:
        p_food = _pick_food_for_meal(protein_pool, rng, BUN_PRO_KEYWORDS, avoid_ids=avoid_p, prefer_lean=prefer_lean)
        v_food = _pick_food_for_meal(veggie_pool, rng, BUN_VEGGIE_KEYWORDS, avoid_ids=avoid_v)
        f_food = _pick_food_for_meal(fat_pool, rng, OLIVE_OIL_KEYWORDS)
    else:
        # Khoai lang hoặc carb khác
        p_food = _pick_food_for_meal(protein_pool, rng, POTATO_PRO_KEYWORDS, avoid_ids=avoid_p, prefer_lean=prefer_lean)
        v_food = _pick_food_for_meal(veggie_pool, rng, POTATO_VEGGIE_KEYWORDS, avoid_ids=avoid_v)
        f_food = _pick_food_for_meal(fat_pool, rng, POTATO_FAT_KEYWORDS)

    return c_food, p_food, v_food, f_food


def _sample_main_combo(
    carb_pool: List[Dict[str, Any]],
    protein_pool: List[Dict[str, Any]],
    veggie_pool: List[Dict[str, Any]],
    fat_pool: List[Dict[str, Any]],
    rng: random.Random,
    avoid_c: Set[int],
    avoid_p: Set[int],
    avoid_v: Set[int],
    desired_carb_cal: float,
    desired_pro_cal: float,
    prefer_lean: bool,
    daily_target_pro: float,
) -> Tuple[Dict[str, Any], Dict[str, Any], Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Ghép bữa Trưa & Tối kiểu cơm gia đình Việt Nam (dùng chung 100% món)."""
    rice_items = [f for f in carb_pool if _matches_any(f["name"], STAPLE_RICE_KEYWORDS)]
    if rice_items and rng.random() < 0.80:
        c_food = rice_items[0]
    else:
        c_food = _pick_food_for_meal(
            carb_pool,
            rng,
            MAIN_MEAL_CARB_KEYWORDS,
            avoid_ids=avoid_c,
            target_cal_density=desired_carb_cal,
        )

    c_name = (c_food["name"] if c_food else "").lower()
    is_bun = "bún" in c_name

    # Tránh dùng trứng làm nguồn đạm duy nhất cho cả Trưa + Tối khi nhu cầu đạm cao (để không vượt 3 quả/bữa)
    main_pro_pool = protein_pool
    if is_bun:
        bun_pros = [p for p in protein_pool if _matches_any(p["name"], BUN_PRO_KEYWORDS)]
        if bun_pros:
            main_pro_pool = bun_pros
    elif daily_target_pro >= 95.0:
        non_egg_pros = [p for p in protein_pool if "trứng" not in p["name"].lower()]
        if non_egg_pros:
            main_pro_pool = non_egg_pros

    p_food = _pick_food_for_meal(
        main_pro_pool,
        rng,
        (),
        avoid_ids=avoid_p,
        target_cal_density=desired_pro_cal,
        prefer_lean=prefer_lean,
    )

    if is_bun:
        v_food = _pick_food_for_meal(veggie_pool, rng, BUN_VEGGIE_KEYWORDS, avoid_ids=avoid_v)
        f_food = _pick_food_for_meal(fat_pool, rng, OLIVE_OIL_KEYWORDS)
    else:
        v_food = _pick_food_for_meal(veggie_pool, rng, (), avoid_ids=avoid_v)
        # Ưu tiên dầu oliu dùng chế biến món xào/áp chảo (~85%) để hợp ẩm thực cơm gia đình
        olive_items = [f for f in fat_pool if _matches_any(f["name"], OLIVE_OIL_KEYWORDS)]
        is_fish = _matches_any(p_food["name"], FISH_KEYWORDS) if p_food else False
        if olive_items and (is_fish or rng.random() < 0.85):
            f_food = olive_items[0]
        else:
            f_food = _pick_food_for_meal(fat_pool, rng, MAIN_MEAL_FAT_KEYWORDS)

    return c_food, p_food, v_food, f_food


def _find_cheapest_valid_day(
    grouped: Dict[str, List[Dict[str, Any]]],
    filtered_proteins: List[Dict[str, Any]],
    effective_target_cal: float,
    min_calories_floor: float,
    target_protein_g: float,
    target_carbs_g: float,
    target_fat_g: float,
    target_p_pct: float,
    target_c_pct: float,
    target_f_pct: float,
    daily_budget_vnd: float,
    is_hypertension: bool,
    recent_b_carb_ids: Set[int],
    recent_main_pro_ids: Set[int],
    recent_main_veg_ids: Set[int],
    week_pro_counts: Dict[int, int],
) -> Dict[str, Any]:
    """
    Fallback ngân sách eo hẹp (Edge Case 4):
    - Xoay vòng trong top các món giá rẻ hợp lý (không lặp 7 ngày giống hệt nhau).
    - Nếu nhiều tổ hợp giá rẻ đều nằm trong ngân sách -> ưu tiên món chưa ăn hôm qua để đa dạng.
    - Nếu TẤT CẢ đều vượt ngân sách -> chọn phương án rẻ nhất đạt chuẩn Viện Dinh Dưỡng & sàn calo
      (chỉ cho xoay vòng các món rẻ tương đương trong biên +1.500 VNĐ để không đội giá cảnh báo).
    """
    cheapest_carbs = sorted(
        grouped["carb"],
        key=lambda x: x["cost_per_100g"] / max(x["calories"], 1.0),
    )
    rice_carbs = [c for c in cheapest_carbs if _matches_any(c["name"], STAPLE_RICE_KEYWORDS)]
    main_carb_candidates = (rice_carbs + [c for c in cheapest_carbs if c not in rice_carbs])[:2]

    # Top 6 đạm giá rẻ (ưu tiên cân bằng cả cost/cal và cost/protein, tránh trứng làm đạm chính nếu cần nhiều đạm)
    pros_by_p = sorted(filtered_proteins, key=lambda x: x["cost_per_100g"] / max(x["protein_g"], 1.0))[:5]
    pros_by_c = sorted(filtered_proteins, key=lambda x: x["cost_per_100g"] / max(x["calories"], 1.0))[:4]
    pro_candidates: List[Dict[str, Any]] = []
    seen_p: Set[int] = set()
    for p in pros_by_p + pros_by_c:
        if p["id"] not in seen_p:
            seen_p.add(p["id"])
            pro_candidates.append(p)
    non_egg_main = [p for p in pro_candidates if "trứng" not in p["name"].lower()]
    if non_egg_main and target_protein_g >= 95.0:
        pro_candidates = non_egg_main

    # Xoay vòng carb bữa sáng giá rẻ
    breakfast_carbs = [c for c in grouped["carb"] if _matches_any(c["name"], BREAKFAST_CARB_KEYWORDS)]
    breakfast_carbs.sort(key=lambda x: x["cost_per_100g"] / max(x["calories"], 1.0))
    non_rep_b_carbs = [c for c in breakfast_carbs if c["id"] not in recent_b_carb_ids]
    b_carb_candidates = (non_rep_b_carbs[:2] + breakfast_carbs[:2])[:3] if breakfast_carbs else cheapest_carbs[:1]

    # Xoay vòng rau xanh giá rẻ (top 6 rau rẻ nhất chỉ chênh 200-800đ/100g)
    cheap_vegs = grouped["veggie"][:6]
    non_rep_vegs = [v for v in cheap_vegs if v["id"] not in recent_main_veg_ids]
    chosen_main_veg = non_rep_vegs[0] if non_rep_vegs else (cheap_vegs[0] if cheap_vegs else None)

    olive_fats = [f for f in grouped["fat"] if _matches_any(f["name"], OLIVE_OIL_KEYWORDS)]
    main_fat = olive_fats[0] if olive_fats else (grouped["fat"][0] if grouped["fat"] else None)

    def _make_b_combo(bc: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any], Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        bc_low = bc["name"].lower()
        if "bún" in bc_low:
            b_pros = [p for p in pro_candidates if _matches_any(p["name"], BUN_PRO_KEYWORDS)]
            bp = b_pros[0] if b_pros else pro_candidates[0]
            b_vegs = [v for v in cheap_vegs if _matches_any(v["name"], BUN_VEGGIE_KEYWORDS)]
            bv = b_vegs[0] if b_vegs else chosen_main_veg
            bf = main_fat
        elif "yến mạch" in bc_low:
            b_pros = [p for p in filtered_proteins if _matches_any(p["name"], OATS_PRO_KEYWORDS)]
            b_pros.sort(key=lambda x: x["cost_per_100g"] / max(x["protein_g"], 1.0))
            bp = b_pros[0] if b_pros else pro_candidates[0]
            bv = None
            oats_f = [f for f in grouped["fat"] if _matches_any(f["name"], OATS_FAT_KEYWORDS)]
            bf = oats_f[0] if oats_f else main_fat
        elif "bánh mì" in bc_low:
            b_pros = [p for p in filtered_proteins if _matches_any(p["name"], BREAD_PRO_KEYWORDS)]
            b_pros.sort(key=lambda x: x["cost_per_100g"] / max(x["protein_g"], 1.0))
            bp = b_pros[0] if b_pros else pro_candidates[0]
            b_vegs = [v for v in grouped["veggie"] if _matches_any(v["name"], BREAD_VEGGIE_KEYWORDS)]
            bv = b_vegs[0] if b_vegs else chosen_main_veg
            bread_f = [f for f in grouped["fat"] if _matches_any(f["name"], BREAD_FAT_KEYWORDS)]
            bf = bread_f[0] if bread_f else main_fat
        else:
            b_pros = [p for p in filtered_proteins if _matches_any(p["name"], POTATO_PRO_KEYWORDS)]
            b_pros.sort(key=lambda x: x["cost_per_100g"] / max(x["protein_g"], 1.0))
            bp = b_pros[0] if b_pros else pro_candidates[0]
            b_vegs = [v for v in grouped["veggie"] if _matches_any(v["name"], POTATO_VEGGIE_KEYWORDS)]
            bv = b_vegs[0] if b_vegs else chosen_main_veg
            pot_f = [f for f in grouped["fat"] if _matches_any(f["name"], POTATO_FAT_KEYWORDS)]
            bf = pot_f[0] if pot_f else main_fat
        return bc, bp, bv, bf

    target_levels = [effective_target_cal]
    if min_calories_floor > 0 and min_calories_floor < effective_target_cal:
        target_levels.append(min_calories_floor)

    within_budget_days: List[Dict[str, Any]] = []
    over_budget_days: List[Dict[str, Any]] = []

    for tgt_cal in target_levels:
        scale_ratio = tgt_cal / max(effective_target_cal, 1.0)
        for bc in b_carb_candidates:
            b_combo = _make_b_combo(bc)
            for mc in main_carb_candidates[:1]:
                for mp in pro_candidates:
                    m_combo = (mc, mp, chosen_main_veg, main_fat)
                    day_eval = _evaluate_day_plan(
                        breakfast_combo=b_combo,
                        main_combo=m_combo,
                        target_calories=tgt_cal,
                        min_calories_floor=min_calories_floor,
                        target_protein_g=target_protein_g * scale_ratio,
                        target_carbs_g=target_carbs_g * scale_ratio,
                        target_fat_g=target_fat_g * scale_ratio,
                        target_p_pct=target_p_pct,
                        target_c_pct=target_c_pct,
                        target_f_pct=target_f_pct,
                        daily_budget_vnd=daily_budget_vnd,
                        is_hypertension=is_hypertension,
                    )
                    if day_eval["cost"] <= daily_budget_vnd:
                        within_budget_days.append(day_eval)
                    else:
                        over_budget_days.append(day_eval)

        if within_budget_days:
            # Ưu tiên đạt chuẩn Viện Dinh Dưỡng -> tránh lặp đạm hôm qua -> ít xuất hiện trong tuần -> sát calo
            within_budget_days.sort(
                key=lambda d: (
                    0 if d["is_compliant"] else 1,
                    1 if d["main_combo"][1]["id"] in recent_main_pro_ids else 0,
                    week_pro_counts.get(d["main_combo"][1]["id"], 0),
                    1 if d["breakfast_combo"][0]["id"] in recent_b_carb_ids else 0,
                    abs(d["cal"] - effective_target_cal),
                )
            )
            return within_budget_days[0]

    # Trường hợp tất cả đều vượt ngân sách: ưu tiên đạt chuẩn Viện Dinh Dưỡng & chi phí THẤP NHẤT
    compliant_over = [d for d in over_budget_days if d["is_compliant"]]
    pool_over = compliant_over if compliant_over else over_budget_days
    min_cost = min(d["cost"] for d in pool_over)

    # Nếu có món khác không lặp hôm qua mà giá chỉ chênh <= 1.500 VNĐ so với đáy thì cho phép xoay vòng
    near_min = [d for d in pool_over if d["cost"] <= min_cost + 1500.0]
    near_min.sort(
        key=lambda d: (
            1 if d["main_combo"][1]["id"] in recent_main_pro_ids else 0,
            week_pro_counts.get(d["main_combo"][1]["id"], 0),
            d["cost"],
        )
    )
    return near_min[0]


def generate_optimal_meal_plan(
    request: MealPlanRequest,
    food_db: List[Dict[str, Any]],
    days: int = 7,
    seed: Optional[int] = None,
) -> MealPlanResponse:
    """
    Subtask 2: Thuật toán A5 - Sinh thực đơn 7 ngày hợp lý theo buổi Sáng, Trưa, Tối.
    - Bảo đảm tuyệt đối calories mỗi ngày >= BMR và Hard Floor (min_calories_floor).
    - Tuân thủ biên độ Viện Dinh Dưỡng TP.HCM & WHO:
      Carbohydrate 45-65%, Protein 10-35%, Lipid 20-30% (<30%), chất béo bão hòa < 10%.
    - Cá nhân hóa theo mục tiêu (fat_loss/muscle_gain/maintain) và bệnh lý nền (hypertension).
    - Bữa Trưa & Bữa Tối dùng chung 100% món ăn gia đình, Bữa Sáng tách riêng hợp lý.
    - Xoay vòng món đa dạng cả tuần kể cả khi ngân sách thấp; nếu chọn món rẻ nhất vẫn thiếu calo
      thì tăng chi phí đủ sàn calo và cảnh báo chính xác số tiền cần bổ sung.
    - Định lượng gam làm tròn lên hàng đơn vị (trứng theo quả 50g tối đa 2-3 quả, sandwich theo lát 30g).
    """
    rng = random.Random(seed)
    num_days = max(1, min(int(days), 7))
    grouped = categorize_foods_by_macro(food_db)

    fitness_goal = (request.fitness_goal or "maintain").strip().lower()
    medical_conditions = list(request.medical_conditions or [])
    is_hypertension = "hypertension" in {c.strip().lower() for c in medical_conditions}
    prefer_lean = is_hypertension or fitness_goal == "fat_loss"

    filtered_proteins = _filter_proteins_for_profile(grouped["protein"], fitness_goal, medical_conditions)

    min_calories_floor = float(request.min_calories_floor or 0.0)
    effective_target_cal = max(request.target_calories, min_calories_floor)

    adj_pro_g, adj_carb_g, adj_fat_g, tgt_p_pct, tgt_c_pct, tgt_f_pct = _normalize_nin_macro_targets(
        target_calories=effective_target_cal,
        target_protein_g=request.target_protein_g,
        target_carbs_g=request.target_carbs_g,
        target_fat_g=request.target_fat_g,
    )

    protein_pool = _pick_cost_aware_pool(filtered_proteins, request.max_budget_vnd)
    carb_pool = _pick_cost_aware_pool(grouped["carb"], request.max_budget_vnd)
    fat_pool = _pick_cost_aware_pool(grouped["fat"], request.max_budget_vnd)
    veggie_pool = _pick_cost_aware_pool(grouped["veggie"], request.max_budget_vnd)

    desired_carb_cal_density = min(max(effective_target_cal / 14.0, 90.0), 260.0)
    desired_pro_cal_density = min(max(effective_target_cal / 12.0, 120.0), 260.0)

    weekly_plans: List[DailyMealPlan] = []
    grand_cal = grand_pro = grand_carb = grand_fat = grand_cost = 0.0
    all_week_items: List[SelectedFoodItem] = []
    max_extra_budget_needed = 0.0
    days_over_budget = 0

    recent_b_carb_ids: Set[int] = set()
    recent_b_pro_ids: Set[int] = set()
    recent_main_pro_ids: Set[int] = set()
    recent_main_veg_ids: Set[int] = set()
    week_pro_counts: Dict[int, int] = {}

    num_candidates = 10

    for day_index in range(1, num_days + 1):
        best_day: Optional[Dict[str, Any]] = None
        best_score = float("inf")

        for _ in range(num_candidates):
            b_combo = _sample_breakfast_combo(
                carb_pool=carb_pool,
                protein_pool=protein_pool,
                veggie_pool=veggie_pool,
                fat_pool=fat_pool,
                rng=rng,
                avoid_c=recent_b_carb_ids,
                avoid_p=recent_b_pro_ids,
                avoid_v=recent_main_veg_ids,
                desired_carb_cal=desired_carb_cal_density,
                desired_pro_cal=desired_pro_cal_density,
                prefer_lean=prefer_lean,
            )
            main_avoid_p = recent_main_pro_ids | ({b_combo[1]["id"]} if b_combo[1] else set())
            m_combo = _sample_main_combo(
                carb_pool=carb_pool,
                protein_pool=protein_pool,
                veggie_pool=veggie_pool,
                fat_pool=fat_pool,
                rng=rng,
                avoid_c=set(),
                avoid_p=main_avoid_p,
                avoid_v=recent_main_veg_ids,
                desired_carb_cal=desired_carb_cal_density,
                desired_pro_cal=desired_pro_cal_density,
                prefer_lean=prefer_lean,
                daily_target_pro=adj_pro_g,
            )

            day_eval = _evaluate_day_plan(
                breakfast_combo=b_combo,
                main_combo=m_combo,
                target_calories=effective_target_cal,
                min_calories_floor=min_calories_floor,
                target_protein_g=adj_pro_g,
                target_carbs_g=adj_carb_g,
                target_fat_g=adj_fat_g,
                target_p_pct=tgt_p_pct,
                target_c_pct=tgt_c_pct,
                target_f_pct=tgt_f_pct,
                daily_budget_vnd=request.max_budget_vnd,
                is_hypertension=is_hypertension,
            )

            cal_err = abs(day_eval["cal"] - effective_target_cal) / max(effective_target_cal, 1.0)
            pro_err = abs(day_eval["pro_pct"] - tgt_p_pct) / 100.0
            carb_err = abs(day_eval["carb_pct"] - tgt_c_pct) / 100.0
            fat_err = abs(day_eval["fat_pct"] - tgt_f_pct) / 100.0

            budget_over = max(0.0, day_eval["cost"] - request.max_budget_vnd)
            budget_penalty = (4.0 + budget_over / max(request.max_budget_vnd, 1.0)) if budget_over > 0 else 0.0
            floor_penalty = 20.0 if (min_calories_floor > 0 and day_eval["cal"] < min_calories_floor) else 0.0
            nin_penalty = 0.0 if day_eval["is_compliant"] else 15.0
            repeat_penalty = 0.25 * week_pro_counts.get(m_combo[1]["id"], 0)

            score = (
                cal_err * 1.6
                + pro_err * 1.2
                + carb_err * 1.2
                + fat_err * 1.2
                + budget_penalty
                + floor_penalty
                + nin_penalty
                + repeat_penalty
                + rng.uniform(0.0, 0.03)
            )
            if score < best_score:
                best_score = score
                best_day = day_eval

        # Nếu tổ hợp ngẫu nhiên vượt ngân sách HOẶC chưa đạt chuẩn Viện Dinh Dưỡng -> gọi fallback đa dạng giá rẻ
        if best_day is None or best_day["cost"] > request.max_budget_vnd or not best_day["is_compliant"]:
            cheapest_day = _find_cheapest_valid_day(
                grouped=grouped,
                filtered_proteins=filtered_proteins,
                effective_target_cal=effective_target_cal,
                min_calories_floor=min_calories_floor,
                target_protein_g=adj_pro_g,
                target_carbs_g=adj_carb_g,
                target_fat_g=adj_fat_g,
                target_p_pct=tgt_p_pct,
                target_c_pct=tgt_c_pct,
                target_f_pct=tgt_f_pct,
                daily_budget_vnd=request.max_budget_vnd,
                is_hypertension=is_hypertension,
                recent_b_carb_ids=recent_b_carb_ids,
                recent_main_pro_ids=recent_main_pro_ids,
                recent_main_veg_ids=recent_main_veg_ids,
                week_pro_counts=week_pro_counts,
            )
            if cheapest_day is not None:
                if best_day is None:
                    best_day = cheapest_day
                elif cheapest_day["is_compliant"] and not best_day["is_compliant"]:
                    best_day = cheapest_day
                elif best_day["cost"] > request.max_budget_vnd and cheapest_day["cost"] < best_day["cost"]:
                    best_day = cheapest_day

        # Cập nhật lịch sử món để ngày hôm sau xoay vòng đa dạng
        b_c, b_p, _, _ = best_day["breakfast_combo"]
        _, m_p, m_v, _ = best_day["main_combo"]
        if b_c:
            recent_b_carb_ids = {b_c["id"]}
        if b_p:
            recent_b_pro_ids = {b_p["id"]}
        if m_p:
            recent_main_pro_ids = {m_p["id"]}
            week_pro_counts[m_p["id"]] = week_pro_counts.get(m_p["id"], 0) + 1
        if m_v:
            recent_main_veg_ids = {m_v["id"]}

        daily_cal = round(best_day["cal"], 1)
        daily_cost = round(best_day["cost"], 0)

        extra_needed = 0.0
        day_warning: Optional[str] = None
        if daily_cost > request.max_budget_vnd:
            extra_needed = float(math.ceil(daily_cost - request.max_budget_vnd))
            day_warning = format_budget_warning(extra_needed)
            days_over_budget += 1
            if extra_needed > max_extra_budget_needed:
                max_extra_budget_needed = extra_needed

        daily_meals_output = [
            SingleMealOutput(
                meal_name=m["meal_name"],
                total_calories=round(m["cal"], 1),
                total_cost_vnd=round(m["cost"], 0),
                items=m["items"],
            )
            for m in best_day["meals"]
        ]
        for m in best_day["meals"]:
            all_week_items.extend(m["items"])

        weekly_plans.append(
            DailyMealPlan(
                day_of_week=day_index,
                daily_total_calories=daily_cal,
                daily_total_cost=daily_cost,
                extra_budget_needed_vnd=extra_needed,
                budget_warning=day_warning,
                protein_pct=best_day["pro_pct"],
                carbs_pct=best_day["carb_pct"],
                fat_pct=best_day["fat_pct"],
                saturated_fat_pct=best_day["sat_fat_pct"],
                is_nin_compliant=best_day["is_compliant"],
                meals=daily_meals_output,
            )
        )

        grand_cal += best_day["cal"]
        grand_pro += best_day["pro"]
        grand_carb += best_day["carb"]
        grand_fat += best_day["fat"]
        grand_cost += best_day["cost"]

    avg_cost = grand_cost / num_days
    overall_warning = format_budget_warning(max_extra_budget_needed) if max_extra_budget_needed > 0 else None
    w_pro_pct, w_carb_pct, w_fat_pct, w_sat_pct, w_compliant = compute_macro_percentages(all_week_items)
    all_days_compliant = all(bool(d.is_nin_compliant) for d in weekly_plans) and w_compliant

    return MealPlanResponse(
        total_calories=round(grand_cal / num_days, 1),
        total_protein_g=round(grand_pro / num_days, 1),
        total_carbs_g=round(grand_carb / num_days, 1),
        total_fat_g=round(grand_fat / num_days, 1),
        total_cost_vnd=round(avg_cost, 0),
        budget_remaining_vnd=round(request.max_budget_vnd - avg_cost, 0),
        min_calories_floor=round(min_calories_floor, 1) if min_calories_floor > 0 else None,
        extra_budget_needed_vnd=max_extra_budget_needed,
        days_over_budget=days_over_budget,
        budget_warning=overall_warning,
        protein_pct=w_pro_pct,
        carbs_pct=w_carb_pct,
        fat_pct=w_fat_pct,
        saturated_fat_pct=w_sat_pct,
        is_nin_compliant=all_days_compliant,
        dietary_notes=build_dietary_notes(fitness_goal, medical_conditions),
        weekly_plan=weekly_plans,
    )
