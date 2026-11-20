from typing import List, Dict, Any, Tuple
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
    limit = 8 if daily_budget_vnd <= 100000 else len(items)
    return items[: max(3, min(len(items), limit))]


def _pick_food_for_meal(
    pool: List[Dict[str, Any]],
    meal_idx: int,
    day_offset: int,
    preferred_keywords: Tuple[str, ...] = (),
) -> Dict[str, Any] | None:
    """
    Chọn món ăn hợp lý theo từng buổi (Sáng vs Trưa/Tối) và xoay vòng không trùng lặp.
    """
    if not pool:
        return None

    if preferred_keywords:
        matched = [f for f in pool if any(kw in f["name"].lower() for kw in preferred_keywords)]
        if matched:
            return matched[(day_offset + meal_idx) % len(matched)]

    # Công thức (day_offset * 3 + meal_idx) giúp Sáng, Trưa, Tối đổi món liên tục
    return pool[(day_offset * 3 + meal_idx) % len(pool)]


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


def generate_optimal_meal_plan(
    request: MealPlanRequest,
    food_db: List[Dict[str, Any]],
    days: int = 7,
) -> MealPlanResponse:
    """
    Subtask 2: Thuật toán A5 - Sinh thực đơn 7 ngày hợp lý theo buổi Sáng, Trưa, Tối.
    Cấu trúc mỗi bữa: 1 Tinh bột + 1 Đạm + 1 Rau (+ 1 Món thêm để đủ Calo/Fat).
    """
    num_days = max(1, min(int(days), 7))
    grouped = categorize_foods_by_macro(food_db)

    protein_pool = _pick_cost_aware_pool(grouped["protein"], request.max_budget_vnd)
    carb_pool = _pick_cost_aware_pool(grouped["carb"], request.max_budget_vnd)
    fat_pool = _pick_cost_aware_pool(grouped["fat"], request.max_budget_vnd)
    veggie_pool = _pick_cost_aware_pool(grouped["veggie"], request.max_budget_vnd)

    weekly_plans: List[DailyMealPlan] = []
    grand_cal = grand_pro = grand_carb = grand_fat = grand_cost = 0.0

    for day_index in range(1, num_days + 1):
        daily_meals_output: List[SingleMealOutput] = []
        daily_cal = daily_pro = daily_carb = daily_fat = daily_cost = 0.0
        day_offset = day_index - 1

        for idx, (meal_name, ratio) in enumerate(FIXED_3_MEAL_RATIOS):
            meal_target_pro = request.target_protein_g * ratio
            meal_target_carb = request.target_carbs_g * ratio
            meal_target_fat = request.target_fat_g * ratio
            meal_target_cal = request.target_calories * ratio
            meal_budget = request.max_budget_vnd * ratio

            is_breakfast = idx == 0

            # Bốc món hợp lý theo buổi (Sáng ưu tiên đồ ăn sáng, Trưa/Tối ưu tiên cơm & món mặn)
            c_food = _pick_food_for_meal(
                carb_pool, idx, day_offset,
                BREAKFAST_CARB_KEYWORDS if is_breakfast else MAIN_MEAL_CARB_KEYWORDS,
            )
            p_food = _pick_food_for_meal(
                protein_pool, idx, day_offset,
                BREAKFAST_PRO_KEYWORDS if is_breakfast else (),
            )
            v_food = _pick_food_for_meal(veggie_pool, idx, day_offset)
            f_food = _pick_food_for_meal(fat_pool, idx, day_offset)

            # 1. Tính định lượng cơ bản cho 3 món chính: Tinh bột, Đạm, Rau
            p_grams = min(max((meal_target_pro / max(p_food["protein_g"], 1)) * 100.0, 50.0), 280.0)
            rem_carb = max(meal_target_carb - (p_food["carbs_g"] * p_grams / 100.0), 10.0)
            c_grams = min(max((rem_carb / max(c_food["carbs_g"], 1)) * 100.0, 50.0), 320.0)
            # Bữa sáng ăn lượng rau vừa phải (100g), Bữa trưa/tối ăn đầy đặn hơn (130g)
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
                elif rem_cal > meal_target_cal * 0.08 and f_food["calories"] > 0:
                    f_grams = min(max((rem_cal / f_food["calories"]) * 100.0, 15.0), max_extra_g)

            # 3. Cân bằng hai chiều theo target_calories (bù nếu thiếu <90%, hạ nếu vượt >110%)
            raw_cal, raw_fat, _ = _sum_metrics([
                (p_food, p_grams),
                (c_food, c_grams),
                (v_food, v_grams),
                (f_food, f_grams),
            ])
            if meal_target_cal > 0:
                if raw_cal < meal_target_cal * 0.90:
                    cal_gap = meal_target_cal - raw_cal
                    # Ưu tiên đẩy món thứ 4 lên trước nếu còn dư biên độ
                    if f_food and f_food["calories"] > 0 and raw_fat < meal_target_fat * 1.2:
                        max_extra_g = 25.0 if f_food["fat_g"] >= 80 else (80.0 if f_food["fat_g"] >= 10 else 200.0)
                        add_f = min(max(0.0, max_extra_g - f_grams), (cal_gap * 0.5 / f_food["calories"]) * 100.0)
                        f_grams += add_f

                    # Phần Calo còn thiếu chia đều cho Tinh bột và Đạm trong ngưỡng hợp lý
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
                if raw_cal > meal_target_cal * 1.10:
                    cal_scale = meal_target_cal / raw_cal
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

            # Đóng gói đúng thứ tự chuẩn: 1. Tinh bột -> 2. Đạm -> 3. Rau -> 4. Món thêm
            raw_selections: List[Tuple[Dict[str, Any], float]] = [
                (c_food, float(round_fn(c_grams))),
                (p_food, float(round_fn(p_grams))),
            ]
            if v_food and round_fn(v_grams) > 0:
                raw_selections.append((v_food, float(round_fn(v_grams))))
            if f_food and round_fn(f_grams) > 0:
                raw_selections.append((f_food, float(round_fn(f_grams))))

            selected_items: List[SelectedFoodItem] = []
            meal_cal = meal_cost = 0.0

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
                meal_cost += item_cost
                daily_pro += item_pro
                daily_carb += item_carb
                daily_fat += item_fat

            daily_cal += meal_cal
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