from typing import List, Dict, Any
import random
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

DAYS_OF_WEEK_VI = [
    "Thứ 2",
    "Thứ 3",
    "Thứ 4",
    "Thứ 5",
    "Thứ 6",
    "Thứ 7",
    "Chủ nhật",
]


def categorize_foods_by_macro(food_db: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
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


def generate_optimal_meal_plan(request: MealPlanRequest, food_db: List[Dict[str, Any]]) -> MealPlanResponse:
    grouped = categorize_foods_by_macro(food_db)
    all_proteins = grouped["protein"]
    all_carbs = grouped["carb"]
    all_veggies = grouped["veggie"]

    weekly_plans: List[DailyMealPlan] = []
    grand_cal = grand_pro = grand_carb = grand_fat = grand_cost = 0.0

    # LẶP QUA 7 NGÀY
    for day_index in range(1, 8):
        daily_meals_output: List[SingleMealOutput] = []
        daily_cal = daily_pro = daily_carb = daily_fat = daily_cost = 0.0
        
        # Xáo trộn thực phẩm mỗi ngày để không bị ăn trùng lặp (tránh ngán)
        protein_sources = random.sample(all_proteins, min(3, len(all_proteins))) if all_proteins else []
        carb_sources = random.sample(all_carbs, min(3, len(all_carbs))) if all_carbs else []
        veggie_sources = random.sample(all_veggies, min(3, len(all_veggies))) if all_veggies else []

        for idx, (meal_name, ratio) in enumerate(FIXED_3_MEAL_RATIOS):
            meal_target_pro = request.target_protein_g * ratio
            meal_target_carb = request.target_carbs_g * ratio
            meal_target_cal = request.target_calories * ratio  # BỔ SUNG KIỂM SOÁT CALO
            meal_target_fat = request.target_fat_g * ratio     # BỔ SUNG KIỂM SOÁT FAT
            meal_budget = request.max_budget_vnd * ratio

            p_food = protein_sources[idx % len(protein_sources)] if protein_sources else None
            c_food = carb_sources[idx % len(carb_sources)] if carb_sources else None
            v_food = veggie_sources[idx % len(veggie_sources)] if veggie_sources else None
            
            p_grams = c_grams = v_grams = 0.0

            if p_food:
                p_grams = min(max((meal_target_pro / max(p_food["protein_g"], 1)) * 100, 50.0), 300.0)
            if c_food:
                rem_carb = max(meal_target_carb - (p_food["carbs_g"] * p_grams / 100 if p_food else 0), 10.0)
                c_grams = min(max((rem_carb / max(c_food["carbs_g"], 1)) * 100, 50.0), 350.0)
            
            # Tính toán lượng rau/chất béo dựa trên ngân sách và calo còn dư
            if v_food:
                v_grams = 100.0 
            v_cost = (v_food["cost_per_100g"] * v_grams / 100) if v_food else 0.0

            # Xử lý ngân sách bữa ăn
            est_main_cost = (p_food["cost_per_100g"] * p_grams / 100 if p_food else 0) + (c_food["cost_per_100g"] * c_grams / 100 if c_food else 0)
            available_main_budget = max(meal_budget - v_cost, meal_budget * 0.5)

            if est_main_cost > available_main_budget and est_main_cost > 0:
                scale = available_main_budget / est_main_cost
                p_grams *= scale
                c_grams *= scale

            raw_selections = []
            if p_food: raw_selections.append((p_food, p_grams))
            if c_food: raw_selections.append((c_food, c_grams))
            if v_food and v_grams > 0: raw_selections.append((v_food, v_grams))

            selected_items: List[SelectedFoodItem] = []
            meal_cal = meal_cost = 0.0

            for food_obj, grams in raw_selections:
                factor = grams / 100.0
                item_cal = round(food_obj["calories"] * factor, 1)
                item_pro = round(food_obj["protein_g"] * factor, 1)
                item_carb = round(food_obj["carbs_g"] * factor, 1)
                item_fat = round(food_obj["fat_g"] * factor, 1)
                item_cost = round(food_obj["cost_per_100g"] * factor, 0)

                selected_items.append(SelectedFoodItem(
                    food_id=food_obj["id"], name=food_obj["name"], grams=round(grams, 0),
                    calories=item_cal, protein_g=item_pro, carbs_g=item_carb, fat_g=item_fat, cost_vnd=item_cost
                ))

                meal_cal += item_cal
                meal_cost += item_cost
                daily_pro += item_pro
                daily_carb += item_carb
                daily_fat += item_fat

            daily_cal += meal_cal
            daily_cost += meal_cost

            daily_meals_output.append(SingleMealOutput(
                meal_name=meal_name, total_calories=round(meal_cal, 1), total_cost_vnd=round(meal_cost, 0), items=selected_items
            ))

        weekly_plans.append(DailyMealPlan(
            day_of_week=day_index,
            daily_total_calories=round(daily_cal, 1),
            daily_total_cost=round(daily_cost, 0),
            meals=daily_meals_output
        ))
        
        grand_cal += daily_cal
        grand_pro += daily_pro
        grand_carb += daily_carb
        grand_fat += daily_fat
        grand_cost += daily_cost

    return MealPlanResponse(
        total_calories=round(grand_cal / 7, 1), # Tính trung bình mỗi ngày
        total_protein_g=round(grand_pro / 7, 1),
        total_carbs_g=round(grand_carb / 7, 1),
        total_fat_g=round(grand_fat / 7, 1),
        total_cost_vnd=round(grand_cost / 7, 0),
        budget_remaining_vnd=round(request.max_budget_vnd - (grand_cost / 7), 0),
        weekly_plan=weekly_plans
    )