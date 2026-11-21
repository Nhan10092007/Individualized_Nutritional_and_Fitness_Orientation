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

# Từ khóa phân bổ hợp lý theo từng bữa ăn
BREAKFAST_CARB_KEYWORDS = ("bánh mì sandwich", "bánh mì", "yến mạch", "khoai lang", "bún")
MAIN_MEAL_CARB_KEYWORDS = ("cơm trắng", "cơm", "khoai lang", "bún")
STAPLE_RICE_KEYWORDS = ("cơm trắng", "cơm")
BREAKFAST_PRO_KEYWORDS = ("trứng gà", "trứng", "ức gà", "thịt heo nạc thăn", "thịt bò thăn", "tôm")
BREAKFAST_VEGGIE_KEYWORDS = ("dưa leo", "dưa chuột", "cà chua", "xà lách", "súp lơ", "bông cải")
SWEET_BREAKFAST_FAT_KEYWORDS = ("bơ đậu phộng", "bơ sáp", "bơ trái", "hạt điều")
SAVORY_MEAL_FAT_KEYWORDS = ("dầu oliu", "dầu ô-liu", "bơ sáp", "bơ trái", "hạt điều")


def format_budget_warning(extra_vnd: float) -> str:
    """Tạo thông báo chuẩn khi ngân sách thấp hơn chi phí tối thiểu để đạt sàn calo."""
    amount = max(1, int(math.ceil(extra_vnd)))
    formatted = f"{amount:,}".replace(",", ".")
    return f"Bạn nên thêm {formatted} VNĐ để đảm bảo đủ lượng calories cần thiết cho 1 ngày."


def _matches_any(name: str, keywords: Tuple[str, ...]) -> bool:
    low = name.lower()
    return any(kw in low for kw in keywords)


def categorize_foods_by_macro(food_db: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Subtask 1: Phân nhóm thực phẩm chuẩn xác thành 4 nhóm:
    1. Chất béo tốt (fat) | 2. Tinh bột (carb) | 3. Đạm (protein) | 4. Rau củ (veggie)
    Ưu tiên phân loại chính xác các nhóm thực phẩm quen thuộc (trứng gà vào Đạm,
    yến mạch vào Tinh bột, bơ đậu phộng & hạt điều vào Chất béo, cơm trắng thay gạo sống).
    """
    if not food_db:
        raise ValueError("Danh sách thực phẩm đầu vào đang trống.")

    used_ids: Set[int] = set()

    # 1. Nhóm Chất béo tốt (ưu tiên tách trước để bơ đậu phộng / hạt điều không bị nhầm sang Đạm)
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

    # 2. Nhóm Tinh bột (ưu tiên cơm trắng, yến mạch, bánh mì sandwich, khoai lang, bún)
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
    # Loại trừ "nấm" để "Nấm đùi gà" không bị khớp nhầm với từ khóa "đùi gà"
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

    # Fallback an toàn cho bộ dữ liệu nhỏ trong unit test
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
        weights.append(max(w, 0.15))

    return rng.choices(active_pool, weights=weights, k=1)[0]


def _sum_metrics(selections: List[Tuple[Optional[Dict[str, Any]], float]]) -> Tuple[float, float, float]:
    """Trả về (calories, fat_g, cost_vnd) cho danh sách (food_dict, grams)."""
    total_cal = total_fat = total_cost = 0.0
    for food_obj, grams in selections:
        if not food_obj or grams <= 0:
            continue
        factor = grams / 100.0
        total_cal += food_obj["calories"] * factor
        total_fat += food_obj["fat_g"] * factor
        total_cost += food_obj["cost_per_100g"] * factor
    return total_cal, total_fat, total_cost


def _build_selected_item(food_obj: Dict[str, Any], grams: float) -> SelectedFoodItem:
    """Tạo SelectedFoodItem với định lượng gam luôn được làm tròn lên hàng đơn vị."""
    ceiled_grams = float(math.ceil(grams))
    factor = ceiled_grams / 100.0
    return SelectedFoodItem(
        food_id=food_obj["id"],
        name=food_obj["name"],
        grams=ceiled_grams,
        calories=round(food_obj["calories"] * factor, 1),
        protein_g=round(food_obj["protein_g"] * factor, 1),
        carbs_g=round(food_obj["carbs_g"] * factor, 1),
        fat_g=round(food_obj["fat_g"] * factor, 1),
        cost_vnd=round(food_obj["cost_per_100g"] * factor, 0),
    )


def _compute_meal_portions(
    c_food: Dict[str, Any],
    p_food: Dict[str, Any],
    v_food: Optional[Dict[str, Any]],
    f_food: Optional[Dict[str, Any]],
    meal_target_cal: float,
    meal_min_cal: float,
    meal_target_pro: float,
    meal_target_carb: float,
    meal_target_fat: float,
    meal_budget: float,
    is_breakfast: bool,
    allow_exceed_budget: bool = False,
) -> Tuple[List[SelectedFoodItem], float, float, float, float, float]:
    """
    Tính định lượng (grams) cho tổ hợp (c_food, p_food, v_food, f_food) để:
    - Bám sát target_calories và macros
    - KHÔNG bao giờ cắt giảm calories xuống dưới meal_min_cal (sàn BMR/hard floor)
    - Làm tròn định lượng gam lên hàng đơn vị (math.ceil)
    """
    effective_target = max(meal_target_cal, meal_min_cal)

    # 1. Định lượng cơ bản cho 3 món chính: Đạm, Tinh bột, Rau
    p_grams = min(max((meal_target_pro / max(p_food["protein_g"], 1.0)) * 100.0, 50.0), 300.0)
    rem_carb = max(meal_target_carb - (p_food["carbs_g"] * p_grams / 100.0), 10.0)
    c_grams = min(max((rem_carb / max(c_food["carbs_g"], 1.0)) * 100.0, 50.0), 380.0)
    v_grams = (90.0 if is_breakfast else 120.0) if v_food else 0.0
    f_grams = 0.0

    # 2. Bổ sung món Chất béo tốt nếu thiếu Fat HOẶC thiếu Calo
    base_cal, base_fat, _ = _sum_metrics([(p_food, p_grams), (c_food, c_grams), (v_food, v_grams)])
    rem_fat = meal_target_fat - base_fat
    rem_cal = effective_target - base_cal

    if f_food and f_food["id"] not in {p_food["id"], c_food["id"], v_food["id"] if v_food else -1}:
        if f_food["fat_g"] >= 80:
            max_extra_g = 22.0   # Dầu oliu: tối đa 22g
        elif f_food["fat_g"] >= 35:
            max_extra_g = 45.0   # Bơ đậu phộng / hạt điều: tối đa 45g
        elif f_food["fat_g"] >= 10:
            max_extra_g = 90.0   # Bơ sáp tươi: tối đa 90g
        else:
            max_extra_g = 150.0

        if rem_fat > 2.0 and f_food["fat_g"] > 0:
            f_grams = min(max((rem_fat / f_food["fat_g"]) * 100.0, 8.0), max_extra_g)
        elif rem_cal > effective_target * 0.05 and f_food["calories"] > 0:
            f_grams = min(max((rem_cal / f_food["calories"]) * 100.0, 10.0), max_extra_g)

    # 3. Cân bằng hai chiều theo effective_target (bù nếu thiếu <96%, hạ nếu vượt >104%)
    raw_cal, raw_fat, _ = _sum_metrics([
        (p_food, p_grams),
        (c_food, c_grams),
        (v_food, v_grams),
        (f_food, f_grams),
    ])
    if effective_target > 0:
        if raw_cal < effective_target * 0.96:
            cal_gap = effective_target - raw_cal
            if f_food and f_food["calories"] > 0 and raw_fat < meal_target_fat * 1.3:
                max_extra_g = 25.0 if f_food["fat_g"] >= 80 else (50.0 if f_food["fat_g"] >= 35 else 110.0)
                add_f = min(max(0.0, max_extra_g - f_grams), (cal_gap * 0.45 / f_food["calories"]) * 100.0)
                f_grams += add_f

            raw_cal, _, _ = _sum_metrics([
                (p_food, p_grams), (c_food, c_grams), (v_food, v_grams), (f_food, f_grams)
            ])
            rem_gap = max(0.0, effective_target - raw_cal)
            if rem_gap > 0 and c_food["calories"] > 0:
                c_grams = min(c_grams + (rem_gap * 0.65 / c_food["calories"]) * 100.0, 450.0)
            if rem_gap > 0 and p_food["calories"] > 0:
                p_grams = min(p_grams + (rem_gap * 0.35 / p_food["calories"]) * 100.0, 340.0)

        raw_cal, _, _ = _sum_metrics([
            (p_food, p_grams), (c_food, c_grams), (v_food, v_grams), (f_food, f_grams)
        ])
        if raw_cal > effective_target * 1.04:
            v_cal = (v_food["calories"] * v_grams / 100.0) if v_food else 0.0
            scalable_cal = max(raw_cal - v_cal, 1.0)
            target_scalable = max(effective_target - v_cal, effective_target * 0.7)
            cal_scale = target_scalable / scalable_cal
            p_grams *= cal_scale
            c_grams *= cal_scale
            f_grams *= cal_scale

    # 4. Kiểm soát ngân sách NHƯNG bảo vệ tuyệt đối ngưỡng meal_min_cal (không hạ dưới sàn BMR/Hard Floor)
    if not allow_exceed_budget and meal_budget > 0:
        cur_cal, _, total_est = _sum_metrics([
            (p_food, p_grams),
            (c_food, c_grams),
            (v_food, v_grams),
            (f_food, f_grams),
        ])
        if total_est > meal_budget and total_est > 0:
            desired_scale = meal_budget / total_est
            if meal_min_cal > 0 and cur_cal > 0:
                min_cal_scale = min(1.0, meal_min_cal / cur_cal)
                applied_scale = max(desired_scale, min_cal_scale)
            else:
                applied_scale = desired_scale

            if applied_scale < 1.0:
                p_grams *= applied_scale
                c_grams *= applied_scale
                f_grams *= applied_scale
                v_grams *= applied_scale

    # 5. Đảm bảo sau bước co giãn không bị tụt dưới meal_min_cal
    if meal_min_cal > 0:
        cur_cal, _, _ = _sum_metrics([
            (p_food, p_grams),
            (c_food, c_grams),
            (v_food, v_grams),
            (f_food, f_grams),
        ])
        if cur_cal < meal_min_cal and cur_cal > 0:
            # Ưu tiên bù bằng nguồn năng lượng rẻ nhất trong bữa ăn (carb hoặc fat)
            deficit = meal_min_cal - cur_cal
            boost_candidates: List[Tuple[float, str]] = []
            if c_food["calories"] > 0:
                boost_candidates.append((c_food["cost_per_100g"] / c_food["calories"], "c"))
            if f_food and f_grams > 0 and f_food["calories"] > 0:
                boost_candidates.append((f_food["cost_per_100g"] / f_food["calories"], "f"))
            if p_food["calories"] > 0:
                boost_candidates.append((p_food["cost_per_100g"] / p_food["calories"], "p"))
            boost_candidates.sort(key=lambda x: x[0])

            for _, tag in boost_candidates:
                if deficit <= 0:
                    break
                if tag == "c":
                    add_g = (deficit / c_food["calories"]) * 100.0
                    c_grams += add_g
                    deficit = 0.0
                elif tag == "f" and f_food:
                    max_f = 30.0 if f_food["fat_g"] >= 80 else (60.0 if f_food["fat_g"] >= 35 else 120.0)
                    can_add = max(0.0, max_f - f_grams)
                    add_g = min(can_add, (deficit / f_food["calories"]) * 100.0)
                    f_grams += add_g
                    deficit -= (add_g / 100.0) * f_food["calories"]
                elif tag == "p":
                    add_g = (deficit / p_food["calories"]) * 100.0
                    p_grams += add_g
                    deficit = 0.0

    # 6. Làm tròn định lượng gam LÊN hàng đơn vị (math.ceil) và tính lại chính xác macro/chi phí
    raw_selections: List[Tuple[Dict[str, Any], float]] = []
    if c_grams >= 0.5:
        raw_selections.append((c_food, c_grams))
    if p_grams >= 0.5:
        raw_selections.append((p_food, p_grams))
    if v_food and v_grams >= 0.5:
        raw_selections.append((v_food, v_grams))
    if f_food and f_grams >= 0.5:
        raw_selections.append((f_food, f_grams))

    selected_items: List[SelectedFoodItem] = []
    meal_cal = meal_pro = meal_carb = meal_fat = meal_cost = 0.0

    for food_obj, grams in raw_selections:
        item = _build_selected_item(food_obj, grams)
        selected_items.append(item)
        meal_cal += item.calories
        meal_pro += item.protein_g
        meal_carb += item.carbs_g
        meal_fat += item.fat_g
        meal_cost += item.cost_vnd

    return selected_items, meal_cal, meal_pro, meal_carb, meal_fat, meal_cost


def _top_up_day_to_floor(
    meal_entries: List[Dict[str, Any]],
    food_lookup: Dict[int, Dict[str, Any]],
    min_daily_calories: float,
) -> None:
    """
    Đảm bảo tổng calo cả ngày >= min_daily_calories bằng cách tăng định lượng (số nguyên gram)
    của món có chi phí trên mỗi kcal thấp nhất trong ngày.
    """
    if min_daily_calories <= 0:
        return

    total_cal = sum(m["cal"] for m in meal_entries)
    if total_cal >= min_daily_calories:
        return

    # Tìm món có cost/kcal rẻ nhất trong các bữa (ưu tiên món tinh bột/chất béo có kcal cao)
    best_target: Optional[Tuple[float, int, int]] = None
    for m_idx, entry in enumerate(meal_entries):
        for i_idx, item in enumerate(entry["items"]):
            f = food_lookup.get(item.food_id)
            if not f or f["calories"] <= 40:
                continue
            cost_per_cal = f["cost_per_100g"] / max(f["calories"], 1.0)
            if best_target is None or cost_per_cal < best_target[0]:
                best_target = (cost_per_cal, m_idx, i_idx)

    if best_target is None:
        return

    _, m_idx, i_idx = best_target
    entry = meal_entries[m_idx]
    item = entry["items"][i_idx]
    f = food_lookup[item.food_id]

    deficit = min_daily_calories - total_cal
    extra_grams = math.ceil((deficit / f["calories"]) * 100.0)
    new_grams = item.grams + extra_grams
    updated_item = _build_selected_item(f, new_grams)

    entry["items"][i_idx] = updated_item
    entry["cal"] = sum(it.calories for it in entry["items"])
    entry["pro"] = sum(it.protein_g for it in entry["items"])
    entry["carb"] = sum(it.carbs_g for it in entry["items"])
    entry["fat"] = sum(it.fat_g for it in entry["items"])
    entry["cost"] = sum(it.cost_vnd for it in entry["items"])


def _evaluate_day_plan(
    breakfast_combo: Tuple[Dict[str, Any], Dict[str, Any], Optional[Dict[str, Any]], Optional[Dict[str, Any]]],
    main_combo: Tuple[Dict[str, Any], Dict[str, Any], Optional[Dict[str, Any]], Optional[Dict[str, Any]]],
    food_lookup: Dict[int, Dict[str, Any]],
    target_calories: float,
    min_calories_floor: float,
    target_protein_g: float,
    target_carbs_g: float,
    target_fat_g: float,
    daily_budget_vnd: float,
    allow_exceed_budget: bool = False,
) -> Dict[str, Any]:
    """
    Sinh 1 ngày ăn hoàn chỉnh:
    - Bữa Sáng dùng breakfast_combo (30%)
    - Bữa Trưa (40%) và Bữa Tối (30%) DÙNG CHUNG main_combo (đúng thói quen bữa ăn gia đình)
    """
    meal_entries: List[Dict[str, Any]] = []
    daily_cal = daily_pro = daily_carb = daily_fat = daily_cost = 0.0

    for idx, (meal_name, ratio) in enumerate(FIXED_3_MEAL_RATIOS):
        is_breakfast = idx == 0
        c_food, p_food, v_food, f_food = breakfast_combo if is_breakfast else main_combo

        if idx == len(FIXED_3_MEAL_RATIOS) - 1:
            rem_daily_cal = target_calories - daily_cal
            meal_target_cal = min(
                max(rem_daily_cal, target_calories * 0.20),
                target_calories * 0.45,
            )
            meal_min_cal = max(min_calories_floor - daily_cal, 0.0)
            meal_budget = max(daily_budget_vnd - daily_cost, daily_budget_vnd * 0.15)
        else:
            meal_target_cal = target_calories * ratio
            meal_min_cal = min_calories_floor * ratio
            meal_budget = daily_budget_vnd * ratio

        meal_target_pro = target_protein_g * ratio
        meal_target_carb = target_carbs_g * ratio
        meal_target_fat = target_fat_g * ratio

        items, m_cal, m_pro, m_carb, m_fat, m_cost = _compute_meal_portions(
            c_food=c_food,
            p_food=p_food,
            v_food=v_food,
            f_food=f_food,
            meal_target_cal=meal_target_cal,
            meal_min_cal=meal_min_cal,
            meal_target_pro=meal_target_pro,
            meal_target_carb=meal_target_carb,
            meal_target_fat=meal_target_fat,
            meal_budget=meal_budget,
            is_breakfast=is_breakfast,
            allow_exceed_budget=allow_exceed_budget,
        )

        meal_entries.append(
            {
                "meal_name": meal_name,
                "items": items,
                "cal": m_cal,
                "pro": m_pro,
                "carb": m_carb,
                "fat": m_fat,
                "cost": m_cost,
            }
        )
        daily_cal += m_cal
        daily_pro += m_pro
        daily_carb += m_carb
        daily_fat += m_fat
        daily_cost += m_cost

    # Bảo đảm cứng: tổng calo cả ngày >= min_calories_floor (BMR / Hard Floor)
    if min_calories_floor > 0 and daily_cal < min_calories_floor:
        _top_up_day_to_floor(meal_entries, food_lookup, min_calories_floor)
        daily_cal = sum(m["cal"] for m in meal_entries)
        daily_pro = sum(m["pro"] for m in meal_entries)
        daily_carb = sum(m["carb"] for m in meal_entries)
        daily_fat = sum(m["fat"] for m in meal_entries)
        daily_cost = sum(m["cost"] for m in meal_entries)

    return {
        "meals": meal_entries,
        "cal": daily_cal,
        "pro": daily_pro,
        "carb": daily_carb,
        "fat": daily_fat,
        "cost": daily_cost,
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
) -> Tuple[Dict[str, Any], Dict[str, Any], Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    c_food = _pick_food_for_meal(
        carb_pool,
        rng,
        BREAKFAST_CARB_KEYWORDS,
        avoid_ids=avoid_c,
        target_cal_density=desired_carb_cal,
    )
    p_food = _pick_food_for_meal(
        protein_pool,
        rng,
        BREAKFAST_PRO_KEYWORDS,
        avoid_ids=avoid_p,
        target_cal_density=desired_pro_cal,
    )
    c_name = (c_food["name"] if c_food else "").lower()
    is_oats = "yến mạch" in c_name
    is_bread = "bánh mì" in c_name

    # Yến mạch không ghép với rau xanh nấu canh; bánh mì ghép rau salad nhẹ
    if is_oats:
        v_food = None
    else:
        v_food = _pick_food_for_meal(
            veggie_pool,
            rng,
            BREAKFAST_VEGGIE_KEYWORDS,
            avoid_ids=avoid_v,
        )

    fat_keywords = SWEET_BREAKFAST_FAT_KEYWORDS if (is_oats or is_bread) else SAVORY_MEAL_FAT_KEYWORDS
    f_food = _pick_food_for_meal(fat_pool, rng, fat_keywords)
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
) -> Tuple[Dict[str, Any], Dict[str, Any], Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    # Bữa Trưa & Tối: ưu tiên Cơm trắng (75% các ngày nếu có), còn lại đổi sang khoai lang / bún
    rice_items = [f for f in carb_pool if _matches_any(f["name"], STAPLE_RICE_KEYWORDS)]
    if rice_items and rng.random() < 0.75:
        c_food = rice_items[0]
    else:
        c_food = _pick_food_for_meal(
            carb_pool,
            rng,
            MAIN_MEAL_CARB_KEYWORDS,
            avoid_ids=avoid_c,
            target_cal_density=desired_carb_cal,
        )

    p_food = _pick_food_for_meal(
        protein_pool,
        rng,
        (),
        avoid_ids=avoid_p,
        target_cal_density=desired_pro_cal,
    )
    v_food = _pick_food_for_meal(veggie_pool, rng, (), avoid_ids=avoid_v)
    f_food = _pick_food_for_meal(fat_pool, rng, SAVORY_MEAL_FAT_KEYWORDS)
    return c_food, p_food, v_food, f_food


def _find_cheapest_valid_day(
    grouped: Dict[str, List[Dict[str, Any]]],
    food_lookup: Dict[int, Dict[str, Any]],
    effective_target_cal: float,
    min_calories_floor: float,
    target_protein_g: float,
    target_carbs_g: float,
    target_fat_g: float,
    daily_budget_vnd: float,
) -> Dict[str, Any]:
    """
    Thử các tổ hợp món có chi phí trên mỗi kcal/đạm THẤP NHẤT trong cơ sở dữ liệu
    trước khi quyết định cần tăng ngân sách.
    """
    cheapest_carbs = sorted(
        grouped["carb"],
        key=lambda x: x["cost_per_100g"] / max(x["calories"], 1.0),
    )[:3]
    cheapest_pros = sorted(
        grouped["protein"],
        key=lambda x: x["cost_per_100g"] / max(x["calories"], 1.0),
    )[:4]
    cheapest_pros_by_p = sorted(
        grouped["protein"],
        key=lambda x: x["cost_per_100g"] / max(x["protein_g"], 1.0),
    )[:2]

    # Gộp danh sách đạm rẻ nhất không trùng lặp
    pro_candidates: List[Dict[str, Any]] = []
    seen_p: Set[int] = set()
    for p in cheapest_pros + cheapest_pros_by_p:
        if p["id"] not in seen_p:
            seen_p.add(p["id"])
            pro_candidates.append(p)

    # Ưu tiên cơm trắng nếu nằm trong nhóm tinh bột rẻ nhất
    rice_carbs = [c for c in cheapest_carbs if _matches_any(c["name"], STAPLE_RICE_KEYWORDS)]
    main_carb_candidates = (rice_carbs + [c for c in cheapest_carbs if c not in rice_carbs])[:2]

    breakfast_carbs = [c for c in grouped["carb"] if _matches_any(c["name"], BREAKFAST_CARB_KEYWORDS)]
    breakfast_carbs.sort(key=lambda x: x["cost_per_100g"] / max(x["calories"], 1.0))
    b_carb = breakfast_carbs[0] if breakfast_carbs else cheapest_carbs[0]

    breakfast_pros = [p for p in grouped["protein"] if _matches_any(p["name"], BREAKFAST_PRO_KEYWORDS)]
    breakfast_pros.sort(key=lambda x: x["cost_per_100g"] / max(x["calories"], 1.0))
    b_pro = breakfast_pros[0] if breakfast_pros else pro_candidates[0]

    cheapest_veg = grouped["veggie"][0] if grouped["veggie"] else None
    b_veg = None if "yến mạch" in b_carb["name"].lower() else cheapest_veg

    savory_fats = [f for f in grouped["fat"] if _matches_any(f["name"], SAVORY_MEAL_FAT_KEYWORDS)]
    savory_fats.sort(key=lambda x: x["cost_per_100g"] / max(x["calories"], 1.0))
    cheapest_fat = savory_fats[0] if savory_fats else (grouped["fat"][0] if grouped["fat"] else None)

    sweet_fats = [f for f in grouped["fat"] if _matches_any(f["name"], SWEET_BREAKFAST_FAT_KEYWORDS)]
    sweet_fats.sort(key=lambda x: x["cost_per_100g"] / max(x["calories"], 1.0))
    b_fat = (
        sweet_fats[0]
        if ("yến mạch" in b_carb["name"].lower() or "bánh mì" in b_carb["name"].lower()) and sweet_fats
        else cheapest_fat
    )

    best_within_budget: Optional[Dict[str, Any]] = None
    best_over_budget: Optional[Dict[str, Any]] = None

    # Thử cả 2 mức mục tiêu: effective_target_cal trước, nếu vẫn vượt tiền thì thử sát min_calories_floor
    target_levels = [effective_target_cal]
    if min_calories_floor > 0 and min_calories_floor < effective_target_cal:
        target_levels.append(min_calories_floor)

    for tgt_cal in target_levels:
        scale_ratio = tgt_cal / max(effective_target_cal, 1.0)
        for mc in main_carb_candidates:
            for mp in pro_candidates:
                b_combo = (b_carb, b_pro, b_veg, b_fat)
                m_combo = (mc, mp, cheapest_veg, cheapest_fat)
                day_plan = _evaluate_day_plan(
                    breakfast_combo=b_combo,
                    main_combo=m_combo,
                    food_lookup=food_lookup,
                    target_calories=tgt_cal,
                    min_calories_floor=min_calories_floor,
                    target_protein_g=target_protein_g * scale_ratio,
                    target_carbs_g=target_carbs_g * scale_ratio,
                    target_fat_g=target_fat_g * scale_ratio,
                    daily_budget_vnd=daily_budget_vnd,
                    allow_exceed_budget=False,
                )
                if day_plan["cost"] <= daily_budget_vnd:
                    if best_within_budget is None or abs(day_plan["cal"] - effective_target_cal) < abs(
                        best_within_budget["cal"] - effective_target_cal
                    ):
                        best_within_budget = day_plan
                else:
                    if best_over_budget is None or day_plan["cost"] < best_over_budget["cost"]:
                        best_over_budget = day_plan

        if best_within_budget is not None:
            return best_within_budget

    return best_over_budget


def generate_optimal_meal_plan(
    request: MealPlanRequest,
    food_db: List[Dict[str, Any]],
    days: int = 7,
    seed: Optional[int] = None,
) -> MealPlanResponse:
    """
    Subtask 2: Thuật toán A5 - Sinh thực đơn 7 ngày hợp lý theo buổi Sáng, Trưa, Tối.
    - Bảo đảm tuyệt đối calories mỗi ngày >= BMR và Hard Floor (min_calories_floor).
    - Nếu ngân sách không đủ, tự động thử các món rẻ nhất trước; nếu vẫn chưa đủ sàn calo,
      tăng định lượng/giá lên đủ calo cần thiết và trả về thông báo số tiền cần thêm.
    - Bữa Trưa & Bữa Tối dùng chung món ăn (đúng thực tế gia đình), Bữa Sáng tách riêng hợp lý.
    - Mọi định lượng gam đều được làm tròn lên hàng đơn vị (math.ceil).
    """
    rng = random.Random(seed)
    num_days = max(1, min(int(days), 7))
    grouped = categorize_foods_by_macro(food_db)
    food_lookup = {f["id"]: f for f in food_db}

    min_calories_floor = float(request.min_calories_floor or 0.0)
    effective_target_cal = max(request.target_calories, min_calories_floor)

    protein_pool = _pick_cost_aware_pool(grouped["protein"], request.max_budget_vnd)
    carb_pool = _pick_cost_aware_pool(grouped["carb"], request.max_budget_vnd)
    fat_pool = _pick_cost_aware_pool(grouped["fat"], request.max_budget_vnd)
    veggie_pool = _pick_cost_aware_pool(grouped["veggie"], request.max_budget_vnd)

    desired_carb_cal_density = min(max(effective_target_cal / 14.0, 90.0), 260.0)
    desired_pro_cal_density = min(max(effective_target_cal / 12.0, 120.0), 260.0)

    weekly_plans: List[DailyMealPlan] = []
    grand_cal = grand_pro = grand_carb = grand_fat = grand_cost = 0.0
    max_extra_budget_needed = 0.0

    recent_b_carb_ids: Set[int] = set()
    recent_b_pro_ids: Set[int] = set()
    recent_main_pro_ids: Set[int] = set()
    recent_main_veg_ids: Set[int] = set()

    num_candidates = 8

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
            )
            m_combo = _sample_main_combo(
                carb_pool=carb_pool,
                protein_pool=protein_pool,
                veggie_pool=veggie_pool,
                fat_pool=fat_pool,
                rng=rng,
                avoid_c=set(),
                avoid_p=recent_main_pro_ids,
                avoid_v=recent_main_veg_ids,
                desired_carb_cal=desired_carb_cal_density,
                desired_pro_cal=desired_pro_cal_density,
            )

            day_eval = _evaluate_day_plan(
                breakfast_combo=b_combo,
                main_combo=m_combo,
                food_lookup=food_lookup,
                target_calories=effective_target_cal,
                min_calories_floor=min_calories_floor,
                target_protein_g=request.target_protein_g,
                target_carbs_g=request.target_carbs_g,
                target_fat_g=request.target_fat_g,
                daily_budget_vnd=request.max_budget_vnd,
                allow_exceed_budget=False,
            )

            cal_err = abs(day_eval["cal"] - effective_target_cal) / max(effective_target_cal, 1.0)
            pro_err = abs(day_eval["pro"] - request.target_protein_g) / max(request.target_protein_g, 1.0)
            carb_err = abs(day_eval["carb"] - request.target_carbs_g) / max(request.target_carbs_g, 1.0)
            fat_err = abs(day_eval["fat"] - request.target_fat_g) / max(request.target_fat_g, 1.0)
            budget_over = max(0.0, day_eval["cost"] - request.max_budget_vnd)
            budget_penalty = (3.0 + budget_over / max(request.max_budget_vnd, 1.0)) if budget_over > 0 else 0.0
            floor_penalty = 10.0 if (min_calories_floor > 0 and day_eval["cal"] < min_calories_floor) else 0.0

            score = (
                cal_err * 1.5
                + pro_err * 0.4
                + carb_err * 0.3
                + fat_err * 0.3
                + budget_penalty
                + floor_penalty
                + rng.uniform(0.0, 0.04)
            )
            if score < best_score:
                best_score = score
                best_day = day_eval

        # Nếu tổ hợp ngẫu nhiên vẫn vượt ngân sách, tự động thử các món RẺ NHẤT trước
        if best_day is None or best_day["cost"] > request.max_budget_vnd:
            cheapest_day = _find_cheapest_valid_day(
                grouped=grouped,
                food_lookup=food_lookup,
                effective_target_cal=effective_target_cal,
                min_calories_floor=min_calories_floor,
                target_protein_g=request.target_protein_g,
                target_carbs_g=request.target_carbs_g,
                target_fat_g=request.target_fat_g,
                daily_budget_vnd=request.max_budget_vnd,
            )
            if cheapest_day is not None and (best_day is None or cheapest_day["cost"] < best_day["cost"]):
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
        if m_v:
            recent_main_veg_ids = {m_v["id"]}

        daily_cal = round(best_day["cal"], 1)
        daily_cost = round(best_day["cost"], 0)

        extra_needed = 0.0
        day_warning: Optional[str] = None
        if daily_cost > request.max_budget_vnd:
            extra_needed = float(math.ceil(daily_cost - request.max_budget_vnd))
            day_warning = format_budget_warning(extra_needed)
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

        weekly_plans.append(
            DailyMealPlan(
                day_of_week=day_index,
                daily_total_calories=daily_cal,
                daily_total_cost=daily_cost,
                extra_budget_needed_vnd=extra_needed,
                budget_warning=day_warning,
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

    return MealPlanResponse(
        total_calories=round(grand_cal / num_days, 1),
        total_protein_g=round(grand_pro / num_days, 1),
        total_carbs_g=round(grand_carb / num_days, 1),
        total_fat_g=round(grand_fat / num_days, 1),
        total_cost_vnd=round(avg_cost, 0),
        budget_remaining_vnd=round(request.max_budget_vnd - avg_cost, 0),
        min_calories_floor=round(min_calories_floor, 1) if min_calories_floor > 0 else None,
        extra_budget_needed_vnd=max_extra_budget_needed,
        budget_warning=overall_warning,
        weekly_plan=weekly_plans,
    )
