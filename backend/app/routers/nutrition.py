from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.nutrition import MealPlanRequest, MealPlanResponse
from app.services.nutrition_service import create_meal_plan_service

router = APIRouter(prefix="/api/nutrition", tags=["Nutrition"])


@router.post("/generate-meal-plan", response_model=MealPlanResponse, status_code=status.HTTP_200_OK)
def generate_meal_plan_endpoint(
    payload: MealPlanRequest,
    db: Session = Depends(get_db),
):
    try:
        return create_meal_plan_service(db=db, request=payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi hệ thống khi tạo thực đơn.",
        )