from unittest.mock import MagicMock
from types import SimpleNamespace
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.schemas.nutrition import MealPlanRequest
from app.models.user import User
from app.routers import nutrition as nutrition_router
from app.algorithms.nutrition_calculator import generate_optimal_meal_plan
from app.dependencies import get_current_user
from app.database import get_db

MOCK_FOOD_DB = [
    {"id": 1, "name_vi": "Ức gà phi lê", "calories_100g": 165, "protein_100g": 31.0, "carbs_100g": 0.0, "fat_100g": 3.6, "estimated_price_vnd": 12000},
    {"id": 2, "name_vi": "Thịt bò thăn", "calories_100g": 250, "protein_100g": 26.0, "carbs_100g": 0.0, "fat_100g": 15.0, "estimated_price_vnd": 35000},
    {"id": 3, "name_vi": "Trứng gà luộc", "calories_100g": 155, "protein_100g": 13.0, "carbs_100g": 1.1, "fat_100g": 11.0, "estimated_price_vnd": 6000},
    {"id": 4, "name_vi": "Cơm trắng", "calories_100g": 130, "protein_100g": 2.7, "carbs_100g": 28.0, "fat_100g": 0.3, "estimated_price_vnd": 3000},
    {"id": 5, "name_vi": "Khoai lang luộc", "calories_100g": 86, "protein_100g": 1.6, "carbs_100g": 20.1, "fat_100g": 0.1, "estimated_price_vnd": 4500},
    {"id": 6, "name_vi": "Dầu ô-liu nguyên chất", "calories_100g": 884, "protein_100g": 0.0, "carbs_100g": 0.0, "fat_100g": 100.0, "estimated_price_vnd": 6000},
    {"id": 7, "name_vi": "Bông cải xanh", "calories_100g": 34, "protein_100g": 2.8, "carbs_100g": 7.0, "fat_100g": 0.4, "estimated_price_vnd": 6000},
]


class MockFood:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


MOCK_ORM_FOODS = [MockFood(**f) for f in MOCK_FOOD_DB]


def setup_test_app(current_user_mock, db_session_mock):
    test_app = FastAPI()
    test_app.include_router(nutrition_router.router)
    test_app.dependency_overrides[get_current_user] = lambda: current_user_mock
    test_app.dependency_overrides[get_db] = lambda: db_session_mock
    return TestClient(test_app, raise_server_exceptions=True)


def test_api_generate_weekly_plan():
    mock_user = User(
        id=1,
        target_calorie_kcal=1800,
        protein_g=120,
        carb_g=200,
        fat_g=50,
        daily_budget_vnd=100000,
        medical_conditions=[],
    )
    mock_db = MagicMock()
    mock_db.query.return_value.all.return_value = MOCK_ORM_FOODS

    def mock_flush(*args, **kwargs):
        for call_args in mock_db.add.call_args_list:
            added_obj = call_args[0][0]
            if hasattr(added_obj, "id") and getattr(added_obj, "id") is None:
                added_obj.id = 999

    mock_db.flush.side_effect = mock_flush

    client = setup_test_app(mock_user, mock_db)
    response = client.post("/api/nutrition/generate", json={"days": 7})

    assert response.status_code == 200
    data = response.json()

    assert "weekly_plan" in data
    assert len(data["weekly_plan"]) == 7
    assert len(data["weekly_plan"][0]["meals"]) == 3
    assert data["total_cost_vnd"] <= 100000
    assert data["budget_remaining_vnd"] >= 0


def test_api_generate_custom_days_and_budget_cap():
    algo_foods = [
        {
            "id": f["id"],
            "name": f["name_vi"],
            "calories": float(f["calories_100g"]),
            "protein_g": float(f["protein_100g"]),
            "carbs_g": float(f["carbs_100g"]),
            "fat_g": float(f["fat_100g"]),
            "cost_per_100g": float(f["estimated_price_vnd"]),
        }
        for f in MOCK_FOOD_DB
    ]
    req = MealPlanRequest(
        target_calories=2000,
        target_protein_g=130,
        target_carbs_g=220,
        target_fat_g=55,
        max_budget_vnd=50000,
    )
    res = generate_optimal_meal_plan(req, algo_foods, days=3)

    assert len(res.weekly_plan) == 3
    for day in res.weekly_plan:
        assert day.daily_total_cost <= 50000
    assert res.budget_remaining_vnd >= 0

    # Verify calorie & fat targeting when budget comfortably covers expensive mock beef
    comfort_req = MealPlanRequest(
        target_calories=2000,
        target_protein_g=130,
        target_carbs_g=220,
        target_fat_g=55,
        max_budget_vnd=200000,
    )
    comfort_res = generate_optimal_meal_plan(comfort_req, algo_foods, days=7)
    assert 1850 <= comfort_res.total_calories <= 2150
    assert comfort_res.total_fat_g >= 45


def test_api_get_plan_existing_data():
    mock_user = User(id=1, daily_budget_vnd=100000)

    mock_plan_item = MagicMock()
    mock_plan_item.day_of_week = 1
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

    mock_food_obj = SimpleNamespace(id=1, name_vi="Ức gà phi lê")

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = mock_meal_plan
    mock_db.query.return_value.filter.return_value.all.return_value = [mock_food_obj]

    client = setup_test_app(mock_user, mock_db)
    response = client.get("/api/nutrition/plan")

    assert response.status_code == 200
    data = response.json()

    assert len(data["weekly_plan"]) == 1
    assert data["weekly_plan"][0]["day_of_week"] == 1
    assert data["weekly_plan"][0]["meals"][0]["items"][0]["name"] == "Ức gà phi lê"
