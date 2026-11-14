from typing import List, Dict, Any
from app.schemas.nutrition import (
    MealPlanRequest,
    MealPlanResponse,
    SingleMealOutput,
    SelectedFoodItem,
)

# Cố định tỷ lệ 3 bữa ăn trong ngày: Sáng (30%), Trưa (40%), Tối (30%)
FIXED_3_MEAL_RATIOS = [
    ("Bữa Sáng", 0.30),
    ("Bữa Trưa", 0.40),
    ("Bữa Tối", 0.30),
]


def categorize_foods_by_macro(food_db: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Subtask 1: Phân nhóm thực phẩm theo Macro chủ đạo (Đạm, Tinh bột, Rau/Chất béo)
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
    veggie_fat_sources = sorted(
        [f for f in food_db if f not in protein_sources and f not in carb_sources],
        key=lambda x: x["cost_per_100g"],
    )

    if not (protein_sources and carb_sources):
        raise ValueError("Cơ sở dữ liệu thiếu nguồn Protein hoặc Tinh bột để cân bằng bữa ăn.")

    return {
        "protein": protein_sources,
        "carb": carb_sources,
        "veggie": veggie_fat_sources,
    }


def generate_optimal_meal_plan(
    request: MealPlanRequest, food_db: List[Dict[str, Any]]
) -> MealPlanResponse:
    """
    Subtask 2: Thuật toán A5 - Sinh thực đơn 3 bữa theo ngân sách và macro.
    """
    grouped = categorize_foods_by_macro(food_db)
    protein_sources = grouped["protein"]
    carb_sources = grouped["carb"]
    veggie_sources = grouped["veggie"]

    meals_output: List[SingleMealOutput] = []
    total_cal = total_pro = total_carb = total_fat = total_cost = 0.0

    for idx, (meal_name, ratio) in enumerate(FIXED_3_MEAL_RATIOS):
        meal_target_pro = request.target_protein_g * ratio
        meal_target_carb = request.target_carbs_g * ratio
        meal_budget = request.max_budget_vnd * ratio

        p_food = protein_sources[idx % len(protein_sources)]
        c_food = carb_sources[idx % len(carb_sources)]
        v_food = veggie_sources[idx % len(veggie_sources)] if veggie_sources else None

        # 1. Tính định lượng gram cho món Đạm (50g - 300g)
        p_grams = min(max((meal_target_pro / max(p_food["protein_g"], 1)) * 100, 50.0), 300.0)

        # 2. Tính định lượng gram cho món Tinh bột (50g - 350g)
        rem_carb = max(meal_target_carb - (p_food["carbs_g"] * p_grams / 100), 10.0)
        c_grams = min(max((rem_carb / max(c_food["carbs_g"], 1)) * 100, 50.0), 350.0)

        v_grams = 100.0 if v_food else 0.0
        v_cost = (v_food["cost_per_100g"] * v_grams / 100) if v_food else 0.0

        # Kiểm tra ràng buộc Ngân sách bữa ăn (bao gồm cả tiền rau)
        est_main_cost = (p_food["cost_per_100g"] * p_grams / 100) + (
            c_food["cost_per_100g"] * c_grams / 100
        )
        available_main_budget = max(meal_budget - v_cost, meal_budget * 0.5)

        if est_main_cost > available_main_budget and est_main_cost > 0:
            scale_factor = available_main_budget / est_main_cost
            p_grams *= scale_factor
            c_grams *= scale_factor

        # Nếu tổng chi phí vẫn vượt ngân sách bữa, thu nhỏ tất cả các món trong bữa
        total_est = (
            (p_food["cost_per_100g"] * p_grams / 100)
            + (c_food["cost_per_100g"] * c_grams / 100)
            + v_cost
        )
        if total_est > meal_budget and total_est > 0:
            full_scale = meal_budget / total_est
            p_grams *= full_scale
            c_grams *= full_scale
            v_grams *= full_scale

        raw_selections = [(p_food, p_grams), (c_food, c_grams)]
        if v_food and v_grams > 0:
            raw_selections.append((v_food, v_grams))

        selected_items: List[SelectedFoodItem] = []
        meal_cal = meal_cost = 0.0

        for food_obj, grams in raw_selections:
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
                    grams=round(grams, 0),
                    calories=item_cal,
                    protein_g=item_pro,
                    carbs_g=item_carb,
                    fat_g=item_fat,
                    cost_vnd=item_cost,
                )
            )

            meal_cal += item_cal
            meal_cost += item_cost
            total_pro += item_pro
            total_carb += item_carb
            total_fat += item_fat

        total_cal += meal_cal
        total_cost += meal_cost

        meals_output.append(
            SingleMealOutput(
                meal_name=meal_name,
                total_calories=round(meal_cal, 1),
                total_cost_vnd=round(meal_cost, 0),
                items=selected_items,
            )
        )

    return MealPlanResponse(
        total_calories=round(total_cal, 1),
        total_protein_g=round(total_pro, 1),
        total_carbs_g=round(total_carb, 1),
        total_fat_g=round(total_fat, 1),
        total_cost_vnd=round(total_cost, 0),
        budget_remaining_vnd=round(request.max_budget_vnd - total_cost, 0),
        meals=meals_output,
    )