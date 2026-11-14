from pydantic import BaseModel, Field
from typing import List, Optional

# --- 1. API Endpoint (Nhận từ Frontend) ---
class GeneratePlanRequest(BaseModel):
    days: int = Field(default=1, ge=1, le=7, description="Số ngày muốn sinh thực đơn (mặc định 1)")

# --- 2. Thuật toán ---
class MealPlanRequest(BaseModel):
    target_calories: float = Field(..., gt=0, description="Calo mục tiêu")
    target_protein_g: float = Field(..., ge=0, description="Gram Protein mục tiêu")
    target_carbs_g: float = Field(..., ge=0, description="Gram Carbs mục tiêu")
    target_fat_g: float = Field(..., ge=0, description="Gram Fat mục tiêu")
    max_budget_vnd: float = Field(..., gt=0, description="Ngân sách tối đa 1 ngày (VNĐ)")


# --- 3.  Output trả về ---
class SelectedFoodItem(BaseModel):
    food_id: int
    name: str
    grams: float
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    cost_vnd: float

class SingleMealOutput(BaseModel):
    meal_name: str
    total_calories: float
    total_cost_vnd: float
    items: List[SelectedFoodItem]

class DailyMealPlan(BaseModel):
    day_of_week: int
    daily_total_calories: float
    daily_total_cost: float
    meals: List[SingleMealOutput]

class MealPlanResponse(BaseModel):
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    total_cost_vnd: float
    budget_remaining_vnd: float
    weekly_plan: List[DailyMealPlan]