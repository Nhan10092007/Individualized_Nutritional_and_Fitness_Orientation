import random
from typing import List, Dict, Any
from app.schemas.nutrition import (
    MealPlanRequest,
    MealPlanResponse,
    DailyMealPlan,
    SingleMealOutput,
    SelectedFoodItem,
)

# Cố định tỷ lệ 3 bữa ăn trong ngày: Sáng (30%), Trưa (40%), Tối (30%)
FIXED_3_MEAL_RATIOS = [("Bữa Sáng", 0.30), ("Bữa Trưa", 0.40), ("Bữa Tối", 0.30)]

def categorize_foods_by_macro(food_db: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Phân nhóm thực phẩm chi tiết thành 4 loại để cấu trúc bữa ăn: Đạm, Tinh bột, Rau, Món thêm.
    """
    if not food_db:
        raise ValueError("Danh sách thực phẩm đầu vào đang trống.")

    # 1. Nguồn Đạm (Ưu tiên giàu protein)
    protein_sources = sorted([f for f in food_db if f["protein_g"] >= 15], key=lambda x: x["cost_per_100g"] / max(x["protein_g"], 1))
    
    # 2. Nguồn Tinh bột (Giàu Carb, ít Đạm)
    carb_sources = sorted([f for f in food_db if f["carbs_g"] >= 20 and f["protein_g"] < 15], key=lambda x: x["cost_per_100g"] / max(x["carbs_g"], 1))
    
    # 3. Nguồn Rau (Ít Calo, ít Carb)
    veggie_sources = sorted([f for f in food_db if f["calories"] < 50 and f["carbs_g"] < 10 and f not in protein_sources], key=lambda x: x["cost_per_100g"])
    
    # 4. Món thêm (Chất béo, trái cây, sữa hạt... để lấp đầy Calo)
    extra_sources = [f for f in food_db if f not in protein_sources and f not in carb_sources and f not in veggie_sources]
    
    # Dự phòng nếu Database quá ít món
    if not veggie_sources:
        veggie_sources = extra_sources[:2] if extra_sources else carb_sources
    if not extra_sources:
        extra_sources = protein_sources + carb_sources 

    return {"protein": protein_sources, "carb": carb_sources, "veggie": veggie_sources, "extra": extra_sources}


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
    all_proteins = grouped["protein"]
    all_carbs = grouped["carb"]
    all_veggies = grouped["veggie"]
    all_extras = grouped["extra"]

    weekly_plans: List[DailyMealPlan] = []
    grand_cal = grand_pro = grand_carb = grand_fat = grand_cost = 0.0

    # Lặp qua 7 ngày trong tuần
    for day_index in range(1, 8):
        daily_meals_output: List[SingleMealOutput] = []
        daily_cal = daily_pro = daily_carb = daily_fat = daily_cost = 0.0
        
        # Xáo trộn món ăn đầu ngày để đảm bảo sự đa dạng, không bị lặp lại thứ tự
        protein_pool = random.sample(all_proteins, len(all_proteins)) if all_proteins else []
        carb_pool = random.sample(all_carbs, len(all_carbs)) if all_carbs else []
        veggie_pool = random.sample(all_veggies, len(all_veggies)) if all_veggies else []
        extra_pool = random.sample(all_extras, len(all_extras)) if all_extras else []

        for idx, (meal_name, ratio) in enumerate(FIXED_3_MEAL_RATIOS):
            meal_target_pro = request.target_protein_g * ratio
            meal_target_carb = request.target_carbs_g * ratio
            meal_target_cal = request.target_calories * ratio
            meal_budget = request.max_budget_vnd * ratio

            # Lấy 1 món đại diện cho mỗi nhóm trong bữa ăn hiện tại
            p_food = protein_pool[idx % len(protein_pool)] if protein_pool else None
            c_food = carb_pool[idx % len(carb_pool)] if carb_pool else None
            v_food = veggie_pool[idx % len(veggie_pool)] if veggie_pool else None
            e_food = extra_pool[idx % len(extra_pool)] if extra_pool else None
            
            p_grams = c_grams = v_grams = e_grams = 0.0

            # Bước 1: Khớp Tinh bột và Đạm
            if p_food:
                p_grams = min(max((meal_target_pro / max(p_food["protein_g"], 1)) * 100, 50.0), 300.0)
            
            if c_food:
                rem_carb = max(meal_target_carb - (p_food["carbs_g"] * p_grams / 100 if p_food else 0), 10.0)
                c_grams = min(max((rem_carb / max(c_food["carbs_g"], 1)) * 100, 50.0), 350.0)
            
            # Bước 2: Gắn khẩu phần Rau cố định (150g) giúp bữa ăn tự nhiên
            if v_food:
                v_grams = 150.0

            # Bước 3: Đánh giá Calo hiện tại và thêm Món phụ nếu thiếu
            current_cal = 0.0
            if p_food: current_cal += p_food["calories"] * (p_grams / 100)
            if c_food: current_cal += c_food["calories"] * (c_grams / 100)
            if v_food: current_cal += v_food["calories"] * (v_grams / 100)

            if e_food and current_cal < (meal_target_cal * 0.9):
                missing_cal = meal_target_cal - current_cal
                # Khống chế lượng món thêm tối đa 200g (tránh uống quá nhiều sữa hoặc ăn quá nhiều hạt)
                e_grams = min(max((missing_cal / max(e_food["calories"], 1)) * 100, 20.0), 200.0)

            # Bước 4: Kiểm soát Ngân sách (Co dãn khẩu phần nếu vượt tiền)
            raw_selections = []
            if p_food: raw_selections.append([p_food, p_grams])
            if c_food: raw_selections.append([c_food, c_grams])
            if v_food: raw_selections.append([v_food, v_grams])
            if e_food and e_grams > 0: raw_selections.append([e_food, e_grams])

            total_est_cost = sum(food["cost_per_100g"] * (g / 100) for food, g in raw_selections)
            
            if total_est_cost > meal_budget and total_est_cost > 0:
                scale = meal_budget / total_est_cost
                for item in raw_selections:
                    item[1] *= scale

            # Xuất dữ liệu bữa ăn
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
        total_calories=round(grand_cal / 7, 1),
        total_protein_g=round(grand_pro / 7, 1),
        total_carbs_g=round(grand_carb / 7, 1),
        total_fat_g=round(grand_fat / 7, 1),
        total_cost_vnd=round(grand_cost / 7, 0),
        budget_remaining_vnd=round(request.max_budget_vnd - (grand_cost / 7), 0),
        weekly_plan=weekly_plans 
    )
