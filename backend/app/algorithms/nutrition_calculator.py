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


def categorize_foods_by_macro(food_db: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Subtask 1: Phân nhóm thực phẩm theo Macro chủ đạo (Đạm, Tinh bột, Chất béo, Rau củ)
    và sắp xếp ưu tiên theo chi phí tối ưu (rẻ mà giàu dinh dưỡng).
    """
    if not food_db:
        raise ValueError("Danh sách thực phẩm đầu vào đang trống.")

    protein_sources = sorted(
        [f for f in food_db if f["protein_g"] >= 15],
        key=lambda x: x["cost_per_100g"] / max(x["protein_g"], 1),
    )
    carb_sources = sorted(
        [f for f in food_db if f["carbs_g"] >= 20 and f["protein_g"] < 15],
        key=lambda x: x["cost_per_100g"] / max(x["carbs_g"], 1),
    )
    used_ids = {f["id"] for f in protein_sources} | {f["id"] for f in carb_sources}
    fat_sources = sorted(
        [f for f in food_db if f["id"] not in used_ids and f["fat_g"] >= 10],
        key=lambda x: x["cost_per_100g"] / max(x["fat_g"], 1),
    )
    used_ids |= {f["id"] for f in fat_sources}
    veggie_sources = sorted(
        [f for f in food_db if f["id"] not in used_ids],
        key=lambda x: x["cost_per_100g"],
    )

    if not (protein_sources and carb_sources):
        raise ValueError("Cơ sở dữ liệu thiếu nguồn Protein hoặc Tinh bột để cân bằng bữa ăn.")

    return {
        "protein": protein_sources,
        "carb": carb_sources,
        "fat": fat_sources,
        "veggie": veggie_sources,
    }


def _pick_cost_aware_pool(items: List[Dict[str, Any]], daily_budget_vnd: float) -> List[Dict[str, Any]]:
    """Keep top cost-efficient candidates when budget is modest so variety does not blow budget."""
    if not items:
        return []
    limit = 6 if daily_budget_vnd <= 100000 else len(items)
    return items[: max(3, min(len(items), limit))]


def _sum_metrics(selections: List[Tuple[Dict[str, Any], float]]) -> Tuple[float, float, float]:
    """Return (calories, fat_g, cost_vnd) for a list of (food_dict, grams)."""
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
    Subtask 2: Thuật toán A5 - Sinh thực đơn nhiều ngày (mặc định 7 ngày) cân bằng
    Protein, Carbs, Fat, Calo và tuân thủ ngân sách tối đa/ngày.
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

            p_food = protein_pool[(day_offset + idx) % len(protein_pool)]
            c_food = carb_pool[(day_offset + idx) % len(carb_pool)]
            f_food = fat_pool[(day_offset + idx) % len(fat_pool)] if fat_pool else None
            v_food = veggie_pool[(day_offset + idx) % len(veggie_pool)] if veggie_pool else None

            # 1. Định lượng cơ bản theo mục tiêu Protein, Carb và phần rau cố định
            p_grams = min(max((meal_target_pro / max(p_food["protein_g"], 1)) * 100, 50.0), 300.0)
            rem_carb = max(meal_target_carb - (p_food["carbs_g"] * p_grams / 100), 10.0)
            c_grams = min(max((rem_carb / max(c_food["carbs_g"], 1)) * 100, 50.0), 350.0)
            v_grams = 100.0 if v_food else 0.0
            f_grams = 0.0

            # 2. Bổ sung chất béo lành mạnh theo target_fat_g nếu còn thiếu fat
            _, base_fat, _ = _sum_metrics([(p_food, p_grams), (c_food, c_grams), (v_food, v_grams)])
            rem_fat = meal_target_fat - base_fat
            if f_food and rem_fat > 2.0:
                max_fat_grams = 25.0 if f_food["fat_g"] >= 80 else 80.0
                f_grams = min(max((rem_fat / max(f_food["fat_g"], 1)) * 100, 5.0), max_fat_grams)

            # 3. Cân bằng hai chiều theo target_calories (bù nếu thiếu <90%, hạ nếu vượt >110%)
            raw_cal, _, _ = _sum_metrics([
                (p_food, p_grams),
                (c_food, c_grams),
                (f_food, f_grams),
                (v_food, v_grams),
            ])
            if meal_target_cal > 0:
                if raw_cal < meal_target_cal * 0.90 and c_food["calories"] > 0:
                    cal_gap = meal_target_cal - raw_cal
                    extra_c_grams = (cal_gap / c_food["calories"]) * 100.0
                    c_grams = min(c_grams + extra_c_grams, 450.0)

                    raw_cal, raw_fat, _ = _sum_metrics([
                        (p_food, p_grams),
                        (c_food, c_grams),
                        (f_food, f_grams),
                        (v_food, v_grams),
                    ])
                    if raw_cal < meal_target_cal * 0.92 and p_food["calories"] > 0:
                        rem_gap = meal_target_cal - raw_cal
                        p_grams = min(p_grams + (rem_gap * 0.5 / p_food["calories"]) * 100.0, 320.0)
                        if f_food and f_food["calories"] > 0 and raw_fat < meal_target_fat * 1.15:
                            max_fat_grams = 30.0 if f_food["fat_g"] >= 80 else 90.0
                            fat_room_grams = max(0.0, ((meal_target_fat * 1.15 - raw_fat) / max(f_food["fat_g"], 1)) * 100.0)
                            f_grams = min(f_grams + fat_room_grams, max_fat_grams)

                raw_cal, _, _ = _sum_metrics([
                    (p_food, p_grams),
                    (c_food, c_grams),
                    (f_food, f_grams),
                    (v_food, v_grams),
                ])
                if raw_cal > meal_target_cal * 1.10:
                    cal_scale = meal_target_cal / raw_cal
                    p_grams *= cal_scale
                    c_grams *= cal_scale
                    f_grams *= cal_scale

            # 4. Kiểm soát ngân sách chặt chẽ: ưu tiên rau, sau đó đảm bảo tổng <= meal_budget
            v_cost = (v_food["cost_per_100g"] * v_grams / 100) if v_food else 0.0
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
                (f_food, f_grams),
                (v_food, v_grams),
            ])
            if total_est > meal_budget and total_est > 0:
                full_scale = meal_budget / total_est
                p_grams *= full_scale
                c_grams *= full_scale
                f_grams *= full_scale
                v_grams *= full_scale

            round_fn = int if total_est >= meal_budget * 0.98 else (lambda g: round(g, 0))
            raw_selections = [
                (p_food, float(round_fn(p_grams))),
                (c_food, float(round_fn(c_grams))),
            ]
            if f_food and round_fn(f_grams) > 0:
                raw_selections.append((f_food, float(round_fn(f_grams))))
            if v_food and round_fn(v_grams) > 0:
                raw_selections.append((v_food, float(round_fn(v_grams))))

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
