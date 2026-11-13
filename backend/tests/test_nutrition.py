import json
from types import SimpleNamespace
from unittest.mock import MagicMock
import pytest
from pydantic import ValidationError
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.schemas.nutrition import MealPlanRequest, MealPlanResponse
from app.algorithms.nutrition_calculator import (
    categorize_foods_by_macro,
    generate_optimal_meal_plan,
)
from app.services.nutrition_service import create_meal_plan_service
from app.routers import nutrition as nutrition_router

# Dữ liệu thực phẩm giả lập (chỉ gồm dinh dưỡng và giá trên 100g, KHÔNG có dị ứng/chay mặn)
MOCK_FOOD_DB = [
    {"id": 1, "name": "Ức gà phi lê", "calories": 165, "protein_g": 31.0, "carbs_g": 0.0, "fat_g": 3.6, "cost_per_100g": 12000},
    {"id": 2, "name": "Thịt bò thăn", "calories": 250, "protein_g": 26.0, "carbs_g": 0.0, "fat_g": 15.0, "cost_per_100g": 35000},
    {"id": 3, "name": "Trứng gà", "calories": 155, "protein_g": 13.0, "carbs_g": 1.1, "fat_g": 11.0, "cost_per_100g": 8000},
    {"id": 4, "name": "Cơm trắng", "calories": 130, "protein_g": 2.7, "carbs_g": 28.0, "fat_g": 0.3, "cost_per_100g": 3000},
    {"id": 5, "name": "Khoai lang luộc", "calories": 86, "protein_g": 1.6, "carbs_g": 20.1, "fat_g": 0.1, "cost_per_100g": 4500},
    {"id": 6, "name": "Bông cải xanh", "calories": 34, "protein_g": 2.8, "carbs_g": 7.0, "fat_g": 0.4, "cost_per_100g": 6000},
]


# =====================================================================
# TEST FILE 1: app/schemas/nutrition.py
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

    print("\n--- [1. SCHEMA] INPUT (Raw Dict) ---")
    print(raw_input)
    print("--- [1. SCHEMA] OUTPUT (Validated Pydantic Model) ---")
    print(schema_obj.model_dump())

    assert schema_obj.target_calories == 2000.0
    assert schema_obj.max_budget_vnd == 100000.0

    with pytest.raises(ValidationError):
        MealPlanRequest(**{**raw_input, "max_budget_vnd": -50000})


# =====================================================================
# TEST FILE 2: app/algorithms/nutrition_calculator.py
# =====================================================================
def test_2a_algorithm_categorize_subtask():
    grouped = categorize_foods_by_macro(MOCK_FOOD_DB)

    print("\n--- [2A. ALGORITHM - CATEGORIZE] INPUT ---")
    print(f"Tổng số món trong DB: {len(MOCK_FOOD_DB)}")
    print("--- [2A. ALGORITHM - CATEGORIZE] OUTPUT ---")
    print("Nhóm Đạm (ưu tiên giá rẻ/g đạm):", [f["name"] for f in grouped["protein"]])
    print("Nhóm Tinh bột (ưu tiên giá rẻ/g carb):", [f["name"] for f in grouped["carb"]])
    print("Nhóm Rau/Béo:", [f["name"] for f in grouped["veggie"]])

    assert len(grouped["protein"]) == 2
    assert grouped["protein"][0]["name"] == "Ức gà phi lê"  # Rẻ hơn thịt bò tính trên mỗi gram protein
    assert len(grouped["carb"]) == 2


def test_2b_algorithm_generate_3_meals_subtask():
    req = MealPlanRequest(
        target_calories=2000.0,
        target_protein_g=140.0,
        target_carbs_g=220.0,
        target_fat_g=60.0,
        max_budget_vnd=100000.0,
    )
    res: MealPlanResponse = generate_optimal_meal_plan(req, MOCK_FOOD_DB)

    print("\n--- [2B. ALGORITHM - A5 OPTIMIZER] INPUT ---")
    print(req.model_dump())
    print("--- [2B. ALGORITHM - A5 OPTIMIZER] OUTPUT ---")
    print(json.dumps(res.model_dump(), indent=2, ensure_ascii=False))

    assert len(res.meals) == 3
    assert [m.meal_name for m in res.meals] == ["Bữa Sáng", "Bữa Trưa", "Bữa Tối"]
    assert res.total_cost_vnd <= req.max_budget_vnd
    assert res.budget_remaining_vnd >= 0


# =====================================================================
# TEST FILE 3: app/services/nutrition_service.py
# =====================================================================
def test_3_service_layer_with_mock_db():
    mock_db_session = MagicMock()
    # Dùng SimpleNamespace giả lập đối tượng trả về từ SQLAlchemy mà không bị phụ thuộc tên cột của class Food
    mock_orm_foods = [
        SimpleNamespace(id=1, name="Ức gà phi lê", calories_per_100g=165, protein_per_100g=31.0, carbs_per_100g=0.0, fat_per_100g=3.6, price_per_100g=12000),
        SimpleNamespace(id=4, name="Cơm trắng", calories_per_100g=130, protein_per_100g=2.7, carbs_per_100g=28.0, fat_per_100g=0.3, price_per_100g=3000),
        SimpleNamespace(id=6, name="Bông cải xanh", calories_per_100g=34, protein_per_100g=2.8, carbs_per_100g=7.0, fat_per_100g=0.4, price_per_100g=6000),
    ]
    mock_db_session.query.return_value.all.return_value = mock_orm_foods

    req = MealPlanRequest(
        target_calories=1800.0,
        target_protein_g=120.0,
        target_carbs_g=200.0,
        target_fat_g=50.0,
        max_budget_vnd=90000.0,
    )

    service_output = create_meal_plan_service(db=mock_db_session, request=req)

    print("\n--- [3. SERVICE] INPUT (Mock DB Records + MealPlanRequest) ---")
    print(f"Số bản ghi đọc từ DB: {len(mock_orm_foods)} | Ngân sách: {req.max_budget_vnd} VNĐ")
    print("--- [3. SERVICE] OUTPUT (MealPlanResponse) ---")
    print(f"Tổng Calo: {service_output.total_calories} kcal | Tổng Chi Phí: {service_output.total_cost_vnd} VNĐ")

    assert len(service_output.meals) == 3
    assert service_output.total_cost_vnd <= 90000.0


# =====================================================================
# TEST FILE 4: app/routers/nutrition.py
# =====================================================================
def test_4_router_api_endpoint(monkeypatch):
    def mock_service(db, request):
        return generate_optimal_meal_plan(request, MOCK_FOOD_DB)

    monkeypatch.setattr(nutrition_router, "create_meal_plan_service", mock_service)

    test_app = FastAPI()
    test_app.include_router(nutrition_router.router)
    client = TestClient(test_app)

    http_payload = {
        "target_calories": 2000.0,
        "target_protein_g": 140.0,
        "target_carbs_g": 220.0,
        "target_fat_g": 60.0,
        "max_budget_vnd": 100000.0,
    }

    response = client.post("/api/nutrition/generate-meal-plan", json=http_payload)

    print("\n--- [4. ROUTER API] HTTP INPUT ---")
    print(http_payload)
    print("--- [4. ROUTER API] HTTP STATUS & JSON OUTPUT ---")
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

    assert response.status_code == 200
    data = response.json()
    assert len(data["meals"]) == 3
    assert data["total_cost_vnd"] <= 100000.0