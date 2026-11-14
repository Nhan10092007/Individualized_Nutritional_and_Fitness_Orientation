from sqlalchemy.orm import Session
from app.models.food import Food
from app.schemas.nutrition import MealPlanRequest, MealPlanResponse
from app.algorithms.nutrition_calculator import generate_optimal_meal_plan


def create_meal_plan_service(db: Session, request: MealPlanRequest) -> MealPlanResponse:
    foods_from_db = db.query(Food).all()

    food_list = []
    for f in foods_from_db:
        food_list.append(
            {
                "id": getattr(f, "id", 0),
                "name": getattr(f, "name", getattr(f, "food_name", "Thực phẩm")),
                "calories": float(getattr(f, "calories_per_100g", getattr(f, "calories", 0.0))),
                "protein_g": float(getattr(f, "protein_per_100g", getattr(f, "protein", getattr(f, "protein_g", 0.0)))),
                "carbs_g": float(getattr(f, "carbs_per_100g", getattr(f, "carbs", getattr(f, "carbs_g", 0.0)))),
                "fat_g": float(getattr(f, "fat_per_100g", getattr(f, "fat", getattr(f, "fat_g", 0.0)))),
                "cost_per_100g": float(getattr(f, "price_per_100g", getattr(f, "cost_per_100g", getattr(f, "price", 10000.0)))),
            }
        )

    return generate_optimal_meal_plan(request=request, food_db=food_list)