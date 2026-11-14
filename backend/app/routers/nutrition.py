from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.food import Food
from app.models.meal import MealPlan, MealPlanItem
from app.schemas.nutrition import GeneratePlanRequest, MealPlanResponse, SingleMealOutput, SelectedFoodItem, MealPlanRequest
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/nutrition", tags=["Nutrition"])

@router.post("/generate", response_model=MealPlanResponse)
def generate_meal_plan(
    payload: GeneratePlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sinh thực đơn tối ưu mới và lưu vào DB."""
    
    # 1. Đọc thông số từ current_user
    req = MealPlanRequest(
        target_calories=float(current_user.target_calorie_kcal or 2000),
        target_protein_g=float(current_user.protein_g or 100),
        target_carbs_g=float(current_user.carb_g or 200),
        target_fat_g=float(current_user.fat_g or 50),
        max_budget_vnd=float(current_user.daily_budget_vnd or 100000)
    )

    # 2. Xử lý ràng buộc Y khoa (Natri / Sodium)
    medical_conds = current_user.medical_conditions or []
    needs_low_sodium = "hypertension" in medical_conds or "knee_osteoarthritis" in medical_conds

    raw_foods = db.query(Food).all()
    food_list = []
    
    for f in raw_foods:
        # Lấy lượng Natri (giả định bạn đã thêm cột sodium_mg vào model Food)
        sodium = getattr(f, "sodium_mg", 0.0) 
        
        # Nếu có bệnh nền, loại bỏ các thực phẩm có Natri > 400mg/100g
        if needs_low_sodium and sodium > 400:
            continue
            
        food_list.append({
            "id": f.id,
            "name": f.name_vi,
            "calories": float(f.calories_100g),
            "protein_g": float(f.protein_100g),
            "carbs_g": float(f.carbs_100g),
            "fat_g": float(f.fat_100g),
            "cost_per_100g": float(f.estimated_price_vnd)
        })

    if not food_list:
        raise HTTPException(status_code=400, detail="Không đủ thực phẩm an toàn để sinh thực đơn.")

    # 3. Chạy thuật toán A5
    try:
        plan_result = generate_optimal_meal_plan(request=req, food_db=food_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 4. Lưu kết quả vào Database
    new_plan = MealPlan(
        user_id=current_user.id,
        generated_date=date.today(),
        total_calories=plan_result.total_calories,
        total_protein=plan_result.total_protein_g,
        total_carbs=plan_result.total_carbs_g,
        total_fat=plan_result.total_fat_g,
        total_cost_vnd=plan_result.total_cost_vnd
    )
    db.add(new_plan)
    db.flush()

    for meal in plan_result.meals:
        for item in meal.items:
            db_item = MealPlanItem(
                plan_id=new_plan.id,
                food_id=item.food_id,
                meal_type=meal.meal_name,
                grams=item.grams,
                calories=item.calories,
                protein_g=item.protein_g,
                carbs_g=item.carbs_g,
                fat_g=item.fat_g,
                cost_vnd=item.cost_vnd
            )
            db.add(db_item)
            
    db.commit()
    return plan_result


@router.get("/plan", response_model=MealPlanResponse)
def get_current_meal_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy thực đơn hiện tại của user."""
    
    latest_plan = db.query(MealPlan).filter(MealPlan.user_id == current_user.id)\
                    .order_by(MealPlan.created_at.desc()).first()

    if not latest_plan:
        raise HTTPException(status_code=404, detail="Chưa có thực đơn nào.")

    meal_dict = {}
    for item in latest_plan.items:
        if item.meal_type not in meal_dict:
            meal_dict[item.meal_type] = []
        
        food_obj = db.query(Food).filter(Food.id == item.food_id).first()
        food_name = food_obj.name_vi if food_obj else "Unknown"

        meal_dict[item.meal_type].append(SelectedFoodItem(
            food_id=item.food_id,
            name=food_name,
            grams=item.grams,
            calories=item.calories,
            protein_g=item.protein_g,
            carbs_g=item.carbs_g,
            fat_g=item.fat_g,
            cost_vnd=item.cost_vnd
        ))

    meals_output = []
    for m_type, items_list in meal_dict.items():
        m_cal = sum(i.calories for i in items_list)
        m_cost = sum(i.cost_vnd for i in items_list)
        meals_output.append(SingleMealOutput(
            meal_name=m_type,
            total_calories=round(m_cal, 1),
            total_cost_vnd=round(m_cost, 0),
            items=items_list
        ))

    budget = current_user.daily_budget_vnd or 0

    return MealPlanResponse(
        total_calories=latest_plan.total_calories,
        total_protein_g=latest_plan.total_protein,
        total_carbs_g=latest_plan.total_carbs,
        total_fat_g=latest_plan.total_fat,
        total_cost_vnd=latest_plan.total_cost_vnd,
        budget_remaining_vnd=round(budget - latest_plan.total_cost_vnd, 0),
        meals=meals_output
    )