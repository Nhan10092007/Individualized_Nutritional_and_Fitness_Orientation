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

# Từ khóa giúp phân bổ món ăn hợp lý cho Bữa Sáng vs Bữa Trưa/Tối
BREAKFAST_CARB_KEYWORDS = ("bánh mì", "yến mạch", "phở", "bún", "miến", "khoai", "ngô", "xôi", "mì")
MAIN_MEAL_CARB_KEYWORDS = ("cơm", "bún", "khoai", "miến", "mì")
BREAKFAST_PRO_KEYWORDS = ("trứng", "ức gà", "đậu hũ", "bò thăn", "heo nạc thăn", "cá ngừ", "tôm")
NON_VEGGIE_KEYWORDS = ("sữa", "bơ", "hạt", "lạc", "đậu phộng", "dầu", "phô mai")


def categorize_foods_by_macro(food_db: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Subtask 1: Phân nhóm thực phẩm chuẩn xác thành 4 nhóm:
    1. Tinh bột (carb) | 2. Đạm (protein) | 3. Rau củ (veggie) | 4. Món thêm/Chất béo (fat)
    """
    if not food_db:
        raise ValueError("Danh sách thực phẩm đầu vào đang trống.")

    # 1. Nhóm Đạm (Protein >= 15g/100g)
    protein_sources = sorted(
        [f for f in food_db if f["protein_g"] >= 15],
        key=lambda x: x["cost_per_100g"] / max(x["protein_g"], 1),
    )

    # 2. Nhóm Tinh bột (Carbs >= 20g/100g và Protein < 15g/100g)
    carb_sources = sorted(
        [f for f in food_db if f["carbs_g"] >= 20 and f["protein_g"] < 15],
        key=lambda x: x["cost_per_100g"] / max(x["carbs_g"], 1),
    )

    if not (protein_sources and carb_sources):
        raise ValueError("Cơ sở dữ liệu thiếu nguồn Protein hoặc Tinh bột để cân bằng bữa ăn.")

    used_ids = {f["id"] for f in protein_sources} | {f["id"] for f in carb_sources}

    # 3. Nhóm Rau củ xanh (Calo thấp <= 55 kcal, Fat < 5g và không phải sữa/hạt)
    veggie_sources = sorted(
        [
            f for f in food_db
            if f["id"] not in used_ids
            and f["calories"] <= 55
            and f["fat_g"] < 5
            and not any(kw in f["name"].lower() for kw in NON_VEGGIE_KEYWORDS)
        ],
        key=lambda x: x["cost_per_100g"],
    )
    used_ids |= {f["id"] for f in veggie_sources}

    # 4. Nhóm Món thêm / Chất béo tốt (Sữa chua, sữa tươi, quả bơ, các loại hạt, dầu oliu...)
    fat_sources = sorted(
        [f for f in food_db if f["id"] not in used_ids],
        key=lambda x: x["cost_per_100g"] / max(x["calories"], 1),
    )

    # Fallback an toàn nếu bộ dữ liệu test quá nhỏ (ví dụ chỉ có 3-4 món trong Unit Test)
    if not veggie_sources and fat_sources:
        veggie_sources = [f for f in fat_sources if f["fat_g"] < 10] or fat_sources[:1]
    if not fat_sources and veggie_sources:
        fat_sources = [f for f in food_db if f["id"] not in {v["id"] for v in veggie_sources} and f["fat_g"] >= 5]

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
    # Lọc các món có đơn giá 100g không vượt quá 45% ngân sách cả ngày (nếu còn lựa chọn rẻ hơn)
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
) -> Dict[str, Any] | None:
    """
    Chọn ngẫu nhiên có trọng số (Weighted Random) theo từng buổi,
    ưu tiên không trùng món vừa ăn (avoid_ids) và phù hợp mật độ Calo mục tiêu.
    """
    if not pool:
        return None

    avoid_ids = avoid_ids or set()
    candidates = pool

    if preferred_keywords:
        matched = [f for f in pool if any(kw in f["name"].lower() for kw in preferred_keywords)]
        if matched:
            candidates = matched

    # Ưu tiên các món chưa xuất hiện trong các bữa gần nhất
    non_repeated = [f for f in candidates if f["id"] not in avoid_ids]
    active_pool = non_repeated if non_repeated else candidates

    if len(active_pool) == 1:
        return active_pool[0]

    # Tính trọng số ngẫu nhiên: nếu có target_cal_density thì ưu tiên nhẹ các món gần mật độ calo mong muốn
    weights: List[float] = []
    for f in active_pool:
        w = 1.0
        if target_cal_density and target_cal_density > 0:
            diff_ratio = abs(f["calories"] - target_cal_density) / max(target_cal_density, 50.0)
            w = 1.0 / (1.0 + 0.6 * diff_ratio)
        weights.append(max(w, 0.15))

    return rng.choices(active_pool, weights=weights, k=1)[0]


def _sum_metrics(selections: List[Tuple[Dict[str, Any] | None, float]]) -> Tuple[float, float, float]:
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


def _compute_meal_portions(
    c_food: Dict[str, Any],
    p_food: Dict[str, Any],
    v_food: Dict[str, Any] | None,
    f_food: Dict[str, Any] | None,
    meal_target_cal: float,
    meal_target_pro: float,
    meal_target_carb: float,
    meal_target_fat: float,
    meal_budget: float,
    is_breakfast: bool,
) -> Tuple[List[SelectedFoodItem], float, float, float, float, float]:
    """
    Tính định lượng (grams) cho tổ hợp (c_food, p_food, v_food, f_food) để bám sát
    target_calories, macros và không vượt ngân sách bữa ăn.
    Trả về: (selected_items, meal_cal, meal_pro, meal_carb, meal_fat, meal_cost)
    """
    # 1. Tính định lượng cơ bản cho 3 món chính: Tinh bột, Đạm, Rau
    p_grams = min(max((meal_target_pro / max(p_food["protein_g"], 1)) * 100.0, 50.0), 280.0)
    rem_carb = max(meal_target_carb - (p_food["carbs_g"] * p_grams / 100.0), 10.0)
    c_grams = min(max((rem_carb / max(c_food["carbs_g"], 1)) * 100.0, 50.0), 320.0)
    v_grams = (100.0 if is_breakfast else 130.0) if v_food else 0.0
    f_grams = 0.0

    # 2. Bổ sung món thứ 4 (Món phụ / Chất béo) nếu thiếu Fat HOẶC thiếu Calo
    base_cal, base_fat, _ = _sum_metrics([(p_food, p_grams), (c_food, c_grams), (v_food, v_grams)])
    rem_fat = meal_target_fat - base_fat
    rem_cal = meal_target_cal - base_cal

    if f_food and f_food["id"] not in {p_food["id"], c_food["id"], v_food["id"] if v_food else -1}:
        if f_food["fat_g"] >= 80:
            max_extra_g = 20.0   # Dầu oliu / dầu mè: tối đa 20g
        elif f_food["fat_g"] >= 10:
            max_extra_g = 70.0   # Quả bơ / các loại hạt: tối đa 70g
        else:
            max_extra_g = 180.0  # Sữa tươi / sữa chua: tối đa 180g

        if rem_fat > 2.0 and f_food["fat_g"] > 0:
            f_grams = min(max((rem_fat / f_food["fat_g"]) * 100.0, 10.0), max_extra_g)
        elif rem_cal > meal_target_cal * 0.05 and f_food["calories"] > 0:
            f_grams = min(max((rem_cal / f_food["calories"]) * 100.0, 15.0), max_extra_g)

    # 3. Cân bằng hai chiều liên tục theo meal_target_cal (bù nếu thiếu <96%, hạ nếu vượt >104%)
    raw_cal, raw_fat, _ = _sum_metrics([
        (p_food, p_grams),
        (c_food, c_grams),
        (v_food, v_grams),
        (f_food, f_grams),
    ])
    if meal_target_cal > 0:
        if raw_cal < meal_target_cal * 0.96:
            cal_gap = meal_target_cal - raw_cal
            if f_food and f_food["calories"] > 0 and raw_fat < meal_target_fat * 1.25:
                max_extra_g = 25.0 if f_food["fat_g"] >= 80 else (80.0 if f_food["fat_g"] >= 10 else 200.0)
                add_f = min(max(0.0, max_extra_g - f_grams), (cal_gap * 0.5 / f_food["calories"]) * 100.0)
                f_grams += add_f

            raw_cal, _, _ = _sum_metrics([
                (p_food, p_grams), (c_food, c_grams), (v_food, v_grams), (f_food, f_grams)
            ])
            rem_gap = max(0.0, meal_target_cal - raw_cal)
            if rem_gap > 0 and c_food["calories"] > 0:
                c_grams = min(c_grams + (rem_gap * 0.65 / c_food["calories"]) * 100.0, 360.0)
            if rem_gap > 0 and p_food["calories"] > 0:
                p_grams = min(p_grams + (rem_gap * 0.35 / p_food["calories"]) * 100.0, 300.0)

        raw_cal, _, _ = _sum_metrics([
            (p_food, p_grams), (c_food, c_grams), (v_food, v_grams), (f_food, f_grams)
        ])
        if raw_cal > meal_target_cal * 1.04:
            v_cal = (v_food["calories"] * v_grams / 100.0) if v_food else 0.0
            scalable_cal = max(raw_cal - v_cal, 1.0)
            target_scalable = max(meal_target_cal - v_cal, meal_target_cal * 0.7)
            cal_scale = target_scalable / scalable_cal
            p_grams *= cal_scale
            c_grams *= cal_scale
            f_grams *= cal_scale

    # 4. Kiểm soát ngân sách chặt chẽ: giữ nguyên rau, co giãn các món chính nếu vượt tiền
    v_cost = (v_food["cost_per_100g"] * v_grams / 100.0) if v_food else 0.0
    _, _, main_cost = _sum_metrics([(p_food, p_grams), (c_food, c_grams), (f_food, f_grams)])
    available_main_budget = max(meal_budget - v_cost, meal_budget * 0.5)

    if main_cost > available_main_budget and main_cost > 0:
        scale = available_main_budget / main_cost
        p_grams *= scale
        c_grams *= scale
        f_grams *= scale

    _, _, total_est = _sum_metrics([
        (p_food, p_grams),
        (c_food, c_grams),
        (v_food, v_grams),
        (f_food, f_grams),
    ])
    if total_est > meal_budget and total_est > 0:
        full_scale = meal_budget / total_est
        p_grams *= full_scale
        c_grams *= full_scale
        f_grams *= full_scale
        v_grams *= full_scale

    round_fn = int if total_est >= meal_budget * 0.98 else (lambda g: round(g, 0))

    raw_selections: List[Tuple[Dict[str, Any], float]] = [
        (c_food, float(round_fn(c_grams))),
        (p_food, float(round_fn(p_grams))),
    ]
    if v_food and round_fn(v_grams) > 0:
        raw_selections.append((v_food, float(round_fn(v_grams))))
    if f_food and round_fn(f_grams) > 0:
        raw_selections.append((f_food, float(round_fn(f_grams))))

    selected_items: List[SelectedFoodItem] = []
    meal_cal = meal_pro = meal_carb = meal_fat = meal_cost = 0.0

    for food_obj, grams in raw_selections:
        if grams <= 0:
            continue
        factor = grams / 100.0
        item_cal = round(food_obj["calories"] * factor, 1)
        item_pro = round(food_obj["protein_g"] * factor, 1)
        item_carb = round(food_obj["carbs_g"] * factor, 1)
        item_fat = round(food_obj["fat_g"] * factor, 1)
        item_cost = round(food_obj["cost_per_100g"] * factor, 0)

        selected_items.append(
            SelectedFoodItem(
                food_id=food_obj["id"],
                name=food_obj["name"],
                grams=grams,
                calories=item_cal,
                protein_g=item_pro,
                carbs_g=item_carb,
                fat_g=item_fat,
                cost_vnd=item_cost,
            )
        )

        meal_cal += item_cal
        meal_pro += item_pro
        meal_carb += item_carb
        meal_fat += item_fat
        meal_cost += item_cost

    return selected_items, meal_cal, meal_pro, meal_carb, meal_fat, meal_cost


def generate_optimal_meal_plan(
    request: MealPlanRequest,
    food_db: List[Dict[str, Any]],
    days: int = 7,
    seed: Optional[int] = None,
) -> MealPlanResponse:
    """
    Subtask 2: Thuật toán A5 - Sinh thực đơn 7 ngày hợp lý theo buổi Sáng, Trưa, Tối.
    - Randomize món ăn qua Candidate Sampling + Weighted Choice (tránh lặp món liên tiếp).
    - Tự động điều chỉnh mục tiêu Bữa Tối để bù trừ Calo thực tế trong ngày, đảm bảo
      trung bình Calo mỗi ngày luôn xấp xỉ sát nhất với request.target_calories.
    """
    rng = random.Random(seed)
    num_days = max(1, min(int(days), 7))
    grouped = categorize_foods_by_macro(food_db)

    protein_pool = _pick_cost_aware_pool(grouped["protein"], request.max_budget_vnd)
    carb_pool = _pick_cost_aware_pool(grouped["carb"], request.max_budget_vnd)
    fat_pool = _pick_cost_aware_pool(grouped["fat"], request.max_budget_vnd)
    veggie_pool = _pick_cost_aware_pool(grouped["veggie"], request.max_budget_vnd)

    # Mật độ calo tham chiếu theo mục tiêu năng lượng để gợi ý chọn món phù hợp
    desired_carb_cal_density = min(max(request.target_calories / 14.0, 90.0), 260.0)
    desired_pro_cal_density = min(max(request.target_calories / 12.0, 120.0), 260.0)

    weekly_plans: List[DailyMealPlan] = []
    grand_cal = grand_pro = grand_carb = grand_fat = grand_cost = 0.0

    recent_carb_ids: Set[int] = set()
    recent_pro_ids: Set[int] = set()
    recent_veg_ids: Set[int] = set()

    num_candidates = 6  # Số tổ hợp ngẫu nhiên thử nghiệm cho mỗi bữa

    for day_index in range(1, num_days + 1):
        daily_meals_output: List[SingleMealOutput] = []
        daily_cal = daily_pro = daily_carb = daily_fat = daily_cost = 0.0
        used_today_ids: Set[int] = set()

        for idx, (meal_name, ratio) in enumerate(FIXED_3_MEAL_RATIOS):
            # Ở Bữa Tối (idx == 2), tự động bù trừ lượng Calo và Ngân sách còn lại trong ngày
            if idx == len(FIXED_3_MEAL_RATIOS) - 1:
                rem_daily_cal = request.target_calories - daily_cal
                meal_target_cal = min(
                    max(rem_daily_cal, request.target_calories * 0.18),
                    request.target_calories * 0.45,
                )
                meal_budget = max(request.max_budget_vnd - daily_cost, request.max_budget_vnd * 0.15)
            else:
                meal_target_cal = request.target_calories * ratio
                meal_budget = request.max_budget_vnd * ratio

            meal_target_pro = request.target_protein_g * ratio
            meal_target_carb = request.target_carbs_g * ratio
            meal_target_fat = request.target_fat_g * ratio

            is_breakfast = idx == 0

            best_candidate = None
            best_score = float("inf")

            avoid_c = used_today_ids | recent_carb_ids
            avoid_p = used_today_ids | recent_pro_ids
            avoid_v = used_today_ids | recent_veg_ids

            for _ in range(num_candidates):
                c_food = _pick_food_for_meal(
                    carb_pool,
                    rng,
                    BREAKFAST_CARB_KEYWORDS if is_breakfast else MAIN_MEAL_CARB_KEYWORDS,
                    avoid_ids=avoid_c,
                    target_cal_density=desired_carb_cal_density,
                )
                p_food = _pick_food_for_meal(
                    protein_pool,
                    rng,
                    BREAKFAST_PRO_KEYWORDS if is_breakfast else (),
                    avoid_ids=avoid_p,
                    target_cal_density=desired_pro_cal_density,
                )
                v_food = _pick_food_for_meal(veggie_pool, rng, avoid_ids=avoid_v)
                f_food = _pick_food_for_meal(fat_pool, rng, avoid_ids=used_today_ids)

                items, m_cal, m_pro, m_carb, m_fat, m_cost = _compute_meal_portions(
                    c_food=c_food,
                    p_food=p_food,
                    v_food=v_food,
                    f_food=f_food,
                    meal_target_cal=meal_target_cal,
                    meal_target_pro=meal_target_pro,
                    meal_target_carb=meal_target_carb,
                    meal_target_fat=meal_target_fat,
                    meal_budget=meal_budget,
                    is_breakfast=is_breakfast,
                )

                # Điểm đánh giá độ khớp Calo + Macro + Ngân sách (càng nhỏ càng tốt)
                cal_err = abs(m_cal - meal_target_cal) / max(meal_target_cal, 1.0)
                pro_err = abs(m_pro - meal_target_pro) / max(meal_target_pro, 1.0)
                carb_err = abs(m_carb - meal_target_carb) / max(meal_target_carb, 1.0)
                fat_err = abs(m_fat - meal_target_fat) / max(meal_target_fat, 1.0)
                budget_penalty = 2.0 if m_cost > meal_budget else 0.0

                # Thêm nhiễu ngẫu nhiên nhỏ (0..0.04) để các tổ hợp bám sát calo ngang nhau vẫn được xoay vòng đa dạng
                score = (
                    cal_err * 1.5
                    + pro_err * 0.4
                    + carb_err * 0.3
                    + fat_err * 0.3
                    + budget_penalty
                    + rng.uniform(0.0, 0.04)
                )

                if score < best_score:
                    best_score = score
                    best_candidate = (items, m_cal, m_pro, m_carb, m_fat, m_cost, c_food, p_food, v_food)

            selected_items, meal_cal, meal_pro, meal_carb, meal_fat, meal_cost, chosen_c, chosen_p, chosen_v = best_candidate

            # Cập nhật lịch sử món để bữa tiếp theo đổi món mới
            if chosen_c:
                used_today_ids.add(chosen_c["id"])
                recent_carb_ids = {chosen_c["id"]}
            if chosen_p:
                used_today_ids.add(chosen_p["id"])
                recent_pro_ids = {chosen_p["id"]}
            if chosen_v:
                used_today_ids.add(chosen_v["id"])
                recent_veg_ids = {chosen_v["id"]}

            daily_cal += meal_cal
            daily_pro += meal_pro
            daily_carb += meal_carb
            daily_fat += meal_fat
            daily_cost += meal_cost

            daily_meals_output.append(
                SingleMealOutput(
                    meal_name=meal_name,
                    total_calories=round(meal_cal, 1),
                    total_cost_vnd=round(meal_cost, 0),
                    items=selected_items,
                )
            )

        weekly_plans.append(
            DailyMealPlan(
                day_of_week=day_index,
                daily_total_calories=round(daily_cal, 1),
                daily_total_cost=round(daily_cost, 0),
                meals=daily_meals_output,
            )
        )

        grand_cal += daily_cal
        grand_pro += daily_pro
        grand_carb += daily_carb
        grand_fat += daily_fat
        grand_cost += daily_cost

    avg_cost = grand_cost / num_days
    return MealPlanResponse(
        total_calories=round(grand_cal / num_days, 1),
        total_protein_g=round(grand_pro / num_days, 1),
        total_carbs_g=round(grand_carb / num_days, 1),
        total_fat_g=round(grand_fat / num_days, 1),
        total_cost_vnd=round(avg_cost, 0),
        budget_remaining_vnd=round(request.max_budget_vnd - avg_cost, 0),
        weekly_plan=weekly_plans,
    )