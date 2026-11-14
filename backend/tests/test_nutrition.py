import json
from unittest.mock import MagicMock
from types import SimpleNamespace
import pytest
from pydantic import ValidationError
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.schemas.nutrition import MealPlanRequest
from app.algorithms.nutrition_calculator import (
    categorize_foods_by_macro,
    generate_optimal_meal_plan,
)
from app.models.user import User
from app.models.food import Food
from app.models.meal import MealPlan, MealPlanItem
from app.routers import nutrition as nutrition_router

# CHÚ Ý: Import trực tiếp dependency để override chuẩn xác nhất (Tránh lỗi 500)
from app.dependencies import get_current_user
from app.database import get_db

# =====================================================================
# DỮ LIỆU GIẢ LẬP (MOCK DATA)
# =====================================================================

MOCK_FOOD_DB = [
    {"id": 1, "name_vi": "Ức gà phi lê", "calories_100g": 165, "protein_100g": 31.0, "carbs_100g": 0.0, "fat_100g": 3.6, "estimated_price_vnd": 12000, "sodium_mg": 74},
    {"id": 2, "name_vi": "Thịt bò thăn", "calories_100g": 250, "protein_100g": 26.0, "carbs_100g": 0.0, "fat_100g": 15.0, "estimated_price_vnd": 35000, "sodium_mg": 55},
    {"id": 3, "name_vi": "Ruốc thịt lợn (Nhiều muối)", "calories_100g": 369, "protein_100g": 46.6, "carbs_100g": 0.0, "fat_100g": 20.3, "estimated_price_vnd": 40000, "sodium_mg": 1472},
    {"id": 4, "name_vi": "Cơm trắng", "calories_100g": 130, "protein_100g": 2.7, "carbs_100g": 28.0, "fat_100g": 0.3, "estimated_price_vnd": 3000, "sodium_mg": 1},
    {"id": 5, "name_vi": "Khoai lang luộc", "calories_100g": 86, "protein_100g": 1.6, "carbs_100g": 20.1, "fat_100g": 0.1, "estimated_price_vnd": 4500, "sodium_mg": 36},
    {"id": 6, "name_vi": "Bông cải xanh", "calories_100g": 34, "protein_100g": 2.8, "carbs_100g": 7.0, "fat_100g": 0.4, "estimated_price_vnd": 6000, "sodium_mg": 33},
    {"id": 7, "name_vi": "Dưa chuột muối (Nhiều muối)", "calories_100g": 17, "protein_100g": 0.8, "carbs_100g": 3.06, "fat_100g": 0.14, "estimated_price_vnd": 10000, "sodium_mg": 1208},
]

class MockFood:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

MOCK_ORM_FOODS = [MockFood(**food_dict) for food_dict in MOCK_FOOD_DB]


# =====================================================================
# CẤU HÌNH TEST APP VÀ OVERRIDE
# =====================================================================

def setup_test_app(monkeypatch, current_user_mock, db_session_mock):
    def override_get_current_user():
        return current_user_mock
    
    def override_get_db():
        yield db_session_mock

    test_app = FastAPI()
    test_app.include_router(nutrition_router.router)
    
    # Ghi đè trực tiếp hàm gốc để đảm bảo không bị lọt qua middleware gây lỗi 500
    test_app.dependency_overrides[get_current_user] = override_get_current_user
    test_app.dependency_overrides[get_db] = override_get_db
    
    # Thêm raise_server_exceptions=False để test client trả về mã 500 thay vì crash app
    return TestClient(test_app, raise_server_exceptions=False)


# =====================================================================
# BỘ TEST CASES
# =====================================================================

def test_1_schema_input_output():
    raw_input = {
        "target_calories": 2000.0,
        "target_protein_g": 140.0,
        "target_carbs_g": 220.0,
        "target_fat_g": 60.0,
        "max_budget_vnd": 100000.0,
    }
    schema_obj = MealPlanRequest(**raw_input)
    assert schema_obj.target_calories == 2000.0
    with pytest.raises(ValidationError):
        MealPlanRequest(**{**raw_input, "max_budget_vnd": -50000})


def test_api_generate_normal_no_constraint(monkeypatch): #tại sao cái này vẫn ko haotj động nooooo
    """
    Kiểm thử API POST /generate: User bình thường, không bệnh nền.
    """
    mock_user = User(
        id=1,
        target_calorie_kcal=1800,
        protein_g=120,
        carb_g=200,
        fat_g=50,
        daily_budget_vnd=100000,
        medical_conditions=[]
    )

    mock_db = MagicMock()
    mock_db.query.return_value.all.return_value = MOCK_ORM_FOODS
    
    # Sửa lỗi 500 do thiếu ID lúc lưu DB (Flush)
    def mock_flush(*args, **kwargs):
        for call_args in mock_db.add.call_args_list:
            added_obj = call_args[0][0]
            if hasattr(added_obj, 'id') and getattr(added_obj, 'id') is None:
                added_obj.id = 999 

    mock_db.flush.side_effect = mock_flush

    client = setup_test_app(monkeypatch, mock_user, mock_db)
    response = client.post("/api/nutrition/generate", json={"days": 1})

    print("\n--- [API POST /generate] KẾT QUẢ SINH THỰC ĐƠN BÌNH THƯỜNG ---")
    if response.status_code == 500:
        print(f"LỖI SERVER 500: {response.text}")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["meals"]) == 3


def test_api_get_plan_existing_data(monkeypatch):
    """
    Kiểm thử API GET /plan:
    Sửa lỗi ValidationError bằng cách dùng SimpleNamespace cho name_vi
    """
    mock_user = User(id=1, daily_budget_vnd=100000)

    mock_plan_item = MagicMock()
    mock_plan_item.meal_type = "Bữa Sáng"
    mock_plan_item.food_id = 1
    mock_plan_item.grams = 150
    mock_plan_item.calories = 247.5
    mock_plan_item.protein_g = 46.5
    mock_plan_item.carbs_g = 0
    mock_plan_item.fat_g = 5.4
    mock_plan_item.cost_vnd = 18000

    mock_meal_plan = MagicMock()
    mock_meal_plan.user_id = 1
    mock_meal_plan.total_calories = 1500
    mock_meal_plan.total_protein = 100
    mock_meal_plan.total_carbs = 150
    mock_meal_plan.total_fat = 40
    mock_meal_plan.total_cost_vnd = 80000
    mock_meal_plan.items = [mock_plan_item]

    # FIX LỖI VALIDATION ERROR TẠI ĐÂY
    mock_food_obj = SimpleNamespace(name_vi="Ức gà phi lê")

    mock_db = MagicMock()
    # Mock truy vấn 1: Lấy Plan
    mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = mock_meal_plan
    # Mock truy vấn 2: Lấy Food name
    mock_db.query.return_value.filter.return_value.first.return_value = mock_food_obj

    client = setup_test_app(monkeypatch, mock_user, mock_db)
    response = client.get("/api/nutrition/plan")

    print("\n--- [API GET /plan] LẤY THỰC ĐƠN ĐÃ CÓ TRONG DB ---")
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_calories"] == 1500
    assert data["meals"][0]["items"][0]["name"] == "Ức gà phi lê"


def test_api_get_plan_empty(monkeypatch):
    """
    Kiểm thử API GET /plan: Trả về 404 khi chưa sinh thực đơn.
    """
    mock_user = User(id=2)
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

    client = setup_test_app(monkeypatch, mock_user, mock_db)
    response = client.get("/api/nutrition/plan")

    assert response.status_code == 404