from pydantic import BaseModel, Field
from typing import List


class MealPlanRequest(BaseModel):
    target_calories: float = Field(..., gt=0, description="Calo mục tiêu từ thuật toán A2")
    target_protein_g: float = Field(..., gt=0, description="Gram Protein mục tiêu")
    target_carbs_g: float = Field(..., gt=0, description="Gram Carbs mục tiêu")
    target_fat_g: float = Field(..., gt=0, description="Gram Fat mục tiêu")
    max_budget_vnd: float = Field(..., gt=0, description="Ngân sách tối đa 1 ngày (VNĐ)")


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


class MealPlanResponse(BaseModel):
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    total_cost_vnd: float
    budget_remaining_vnd: float
    meals: List[SingleMealOutput]