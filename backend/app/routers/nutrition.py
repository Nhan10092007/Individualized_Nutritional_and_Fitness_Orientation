from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import Dict, List

from app.database import get_db
from app.models.user import User
from app.models.food import Food
from app.models.meal import MealPlan, MealPlanItem
from app.schemas.nutrition import (
    GeneratePlanRequest,
    MealPlanResponse,
    SingleMealOutput,
    SelectedFoodItem,
    DailyMealPlan,
)
from app.algorithms.nutrition_calculator import (
    FIXED_3_MEAL_RATIOS,
    generate_optimal_meal_plan,
    MealPlanRequest,
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/nutrition", tags=["Nutrition"])

MEAL_ORDER = {name: idx for idx, (name, _) in enumerate(FIXED_3_MEAL_RATIOS)}


@router.post("/generate", response_model=MealPlanResponse)
def generate_meal_plan(
    payload: GeneratePlanRequest = Body(default_factory=GeneratePlanRequest),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Sinh thực đơn tối ưu mới theo số ngày yêu cầu (mặc định 7 ngày) và lưu vào DB."""
    req = MealPlanRequest(
        target_calories=float(current_user.target_calorie_kcal or 2000),
        target_protein_g=float(current_user.protein_g or 100),
        target_carbs_g=float(current_user.carb_g or 200),
        target_fat_g=float(current_user.fat_g or 50),
        max_budget_vnd=float(current_user.daily_budget_vnd or 100000),
    )

    raw_foods = db.query(Food).all()
    if not raw_foods:
        raise HTTPException(
            status_code=404,
            detail="Kho thực phẩm rỗng. Vui lòng seed dữ liệu bảng foods trước.",
        )

    food_list = [
        {
            "id": f.id,
            "name": f.name_vi,
            "calories": float(f.calories_100g),
            "protein_g": float(f.protein_100g),
            "carbs_g": float(f.carbs_100g),
            "fat_g": float(f.fat_100g),
            "cost_per_100g": float(f.estimated_price_vnd),
        }
        for f in raw_foods
    ]

    try:
        plan_result = generate_optimal_meal_plan(
            request=req,
            food_db=food_list,
            days=payload.days,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    new_plan = MealPlan(
        user_id=current_user.id,
        generated_date=date.today(),
        total_calories=plan_result.total_calories,
        total_protein=plan_result.total_protein_g,
        total_carbs=plan_result.total_carbs_g,
        total_fat=plan_result.total_fat_g,
        total_cost_vnd=plan_result.total_cost_vnd,
    )
    db.add(new_plan)
    db.flush()

    for daily_plan in plan_result.weekly_plan:
        for meal in daily_plan.meals:
            for item in meal.items:
                db.add(
                    MealPlanItem(
                        plan_id=new_plan.id,
                        food_id=item.food_id,
                        day_of_week=daily_plan.day_of_week,
                        meal_type=meal.meal_name,
                        grams=item.grams,
                        calories=item.calories,
                        protein_g=item.protein_g,
                        carbs_g=item.carbs_g,
                        fat_g=item.fat_g,
                        cost_vnd=item.cost_vnd,
                    )
                )

    db.commit()
    return plan_result


@router.get("/plan", response_model=MealPlanResponse)
def get_current_meal_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lấy thực đơn gần nhất của người dùng."""
    latest_plan = (
        db.query(MealPlan)
        .filter(MealPlan.user_id == current_user.id)
        .order_by(MealPlan.created_at.desc(), MealPlan.id.desc())
        .first()
    )

    if not latest_plan:
        raise HTTPException(status_code=404, detail="Chưa có thực đơn nào.")

    food_ids = {item.food_id for item in latest_plan.items}
    food_map: Dict[int, str] = {}
    if food_ids:
        foods = db.query(Food).filter(Food.id.in_(food_ids)).all()
        food_map = {f.id: f.name_vi for f in foods}

    weekly_dict: Dict[int, Dict[str, List[SelectedFoodItem]]] = {}
    for item in latest_plan.items:
        day_meals = weekly_dict.setdefault(item.day_of_week, {})
        meal_items = day_meals.setdefault(item.meal_type, [])
        meal_items.append(
            SelectedFoodItem(
                food_id=item.food_id,
                name=food_map.get(item.food_id, "Unknown"),
                grams=item.grams,
                calories=item.calories,
                protein_g=item.protein_g,
                carbs_g=item.carbs_g,
                fat_g=item.fat_g,
                cost_vnd=item.cost_vnd,
            )
        )

    weekly_output: List[DailyMealPlan] = []
    for day in sorted(weekly_dict.keys()):
        daily_meals: List[SingleMealOutput] = []
        daily_cal = daily_cost = 0.0

        ordered_meal_types = sorted(
            weekly_dict[day].keys(),
            key=lambda m: MEAL_ORDER.get(m, 99),
        )
        for m_type in ordered_meal_types:
            items_list = weekly_dict[day][m_type]
            m_cal = sum(i.calories for i in items_list)
            m_cost = sum(i.cost_vnd for i in items_list)
            daily_cal += m_cal
            daily_cost += m_cost

            daily_meals.append(
                SingleMealOutput(
                    meal_name=m_type,
                    total_calories=round(m_cal, 1),
                    total_cost_vnd=round(m_cost, 0),
                    items=items_list,
                )
            )

        weekly_output.append(
            DailyMealPlan(
                day_of_week=day,
                daily_total_calories=round(daily_cal, 1),
                daily_total_cost=round(daily_cost, 0),
                meals=daily_meals,
            )
        )

    budget = current_user.daily_budget_vnd or 0

    return MealPlanResponse(
        total_calories=latest_plan.total_calories,
        total_protein_g=latest_plan.total_protein,
        total_carbs_g=latest_plan.total_carbs,
        total_fat_g=latest_plan.total_fat,
        total_cost_vnd=latest_plan.total_cost_vnd,
        budget_remaining_vnd=round(budget - latest_plan.total_cost_vnd, 0),
        weekly_plan=weekly_output,
    )
