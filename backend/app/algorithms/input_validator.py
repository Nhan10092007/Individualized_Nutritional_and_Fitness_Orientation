from typing import Dict, Any, List
from app.schemas.user import (OnboardingRequest, OnboardingResponse, MacroSplit, GenderEnum, FitnessGoalEnum, FitnessLevelEnum)

# Kiểm tra + ràng buộc dữ liệu
class InputValidator:
    @classmethod
    def validate_and_construct(cls, raw: OnboardingRequest) -> Dict[str, Any]:
        warnings: List[str] = []

        # 1. Kiểm tra ngưỡng an toàn sinh học (đồng bộ với OnboardingRequest & Frontend: age 10-70, height 125-200, weight 35-150)
        gender = raw.gender
        age = raw.age
        height_cm = raw.height_cm
        weight_kg = raw.weight_kg

        if age < 10 or age > 70:
            age = 25
            warnings.append(f"Age ({raw.age}) is outside the supported range [10, 70]; defaulting to 25 for safe BMR calculation.")

        if height_cm < 125.0 or height_cm > 200.0:
            height_cm = 165.0 if gender == GenderEnum.MALE else 160.0
            warnings.append(f"Height ({raw.height_cm} cm) is outside the supported range [125, 200] cm; defaulting to {height_cm} cm.")

        if weight_kg < 35.0 or weight_kg > 150.0:
            weight_kg = 60.0 if gender == GenderEnum.MALE else 55.0
            warnings.append(f"Weight ({raw.weight_kg} kg) is outside the supported range [35, 150] kg; defaulting to {weight_kg} kg.")

        daily_budget = raw.daily_budget_vnd
        if daily_budget < 50000.0:
            daily_budget = 50000.0
            warnings.append(f"The budget ({raw.daily_budget_vnd:,.0f} VND) is below the 50,000 VND/day minimum; it has been automatically increased to 50,000 VND.")

        # 2. Tính chỉ số y sinh và sàn calo
        height_m = height_cm / 100
        bmi = round(weight_kg / (height_m * height_m), 1)

        if gender == GenderEnum.MALE:
            ibw_kg = round(50.0 + 0.9 * (height_cm - 152.4), 1)
            bmr_kcal = round(10.0 * weight_kg + 6.25 * height_cm - 5.0 * age + 5.0, 1)
            hard_floor = 1500.0  # Sàn calo an toàn cho nam (NHLBI)
        else:
            ibw_kg = round(45.5 + 0.9 * (height_cm - 152.4), 1)
            bmr_kcal = round(10.0 * weight_kg + 6.25 * height_cm - 5.0 * age - 161.0, 1)
            hard_floor = 1200.0  # Sàn calo an toàn cho nữ (NHLBI)

        days_count = len(raw.available_days)
        if days_count <= 2:
            pal = 1.375 # Vận động nhẹ
        elif days_count <= 4:
            pal = 1.55 # Vận động vừa
        else:
            pal = 1.725 # Vận động nhiều

        tdee_kcal = round(bmr_kcal * pal, 1)

        if raw.fitness_goal == FitnessGoalEnum.FAT_LOSS:
            calc_target = tdee_kcal - 500.0   # Thâm hụt 500 calories
        elif raw.fitness_goal == FitnessGoalEnum.MUSCLE_GAIN:
            calc_target = tdee_kcal + 300.0   # Thặng dư 300 calories
        else:
            calc_target = tdee_kcal  # Duy trì

        is_floor_triggered = False
        if calc_target < bmr_kcal or calc_target < hard_floor:
            target_calorie_kcal = round(max(bmr_kcal, hard_floor), 0)
            is_floor_triggered = True
            warnings.append("The target calorie count reached the medically safe lower limit; the system automatically adjusted it upward to the minimum threshold to safeguard your health.")
        else:
            target_calorie_kcal = round(calc_target, 0)

        if raw.fitness_goal == FitnessGoalEnum.FAT_LOSS:
            p_pct, c_pct, f_pct = 0.35, 0.45, 0.20
        elif raw.fitness_goal == FitnessGoalEnum.MUSCLE_GAIN:
            p_pct, c_pct, f_pct = 0.30, 0.45, 0.25
        else:
            p_pct, c_pct, f_pct = 0.20, 0.50, 0.30

        protein_g = round((target_calorie_kcal * p_pct) / 4.0)
        carb_g = round((target_calorie_kcal * c_pct) / 4.0)
        fat_g = round((target_calorie_kcal * f_pct) / 9.0)

        banned_tags: List[str] = []
        for cond in raw.medical_conditions:
            cond_clean = cond.strip().lower()
            if cond_clean == "knee_osteoarthritis":
                banned_tags.extend(["knee_flexion_over_90", "spine_compression", "open_kinetic_chain_leg_ext"])
            elif cond_clean == "hypertension":
                banned_tags.extend(["valsalva_press", "decline_head_below_heart", "heavy_1rm_npt"])

        banned_tags = sorted(list(set(banned_tags)))  # Loại bỏ nhãn trùng

        
        if daily_budget <= 100000.0:
            budget_tier = "tier_50k_to_100k"
        else:
            budget_tier = "tier_over_100k"

        response_dto = OnboardingResponse(
            message = "Integration and setup of the survey completed successfully!",
            is_valid=True,
            validation_warnings=warnings,
            bmi=bmi,
            ibw_kg=ibw_kg,
            bmr_kcal=bmr_kcal,
            tdee_kcal=tdee_kcal,
            target_calorie_kcal=target_calorie_kcal,
            is_safety_floor_triggered=is_floor_triggered,
            macro_split=MacroSplit(
                protein_g=protein_g,
                carb_g=carb_g,
                fat_g=fat_g
            ),
            budget_tier=budget_tier,
            banned_exercise_tags=banned_tags
        )
    
        # Trả về cả DTO response và bộ dữ liệu đã được làm sạch để lưu Database
        return {
            "response": response_dto,
            "clean_data": {
                "gender": gender.value,
                "age": age,
                "height_cm": height_cm,
                "weight_kg": weight_kg,
                "fitness_goal": raw.fitness_goal.value,
                "fitness_level": raw.fitness_level.value,
                "available_days": raw.available_days,
                "session_duration_mins": raw.session_duration_mins,
                "medical_conditions": raw.medical_conditions,
                "daily_budget_vnd": daily_budget,
                "bmi": bmi,
                "ibw_kg": ibw_kg,
                "bmr_kcal": bmr_kcal,
                "tdee_kcal": tdee_kcal,
                "target_calorie_kcal": target_calorie_kcal,
                "protein_g": protein_g,
                "carb_g": carb_g,
                "fat_g": fat_g,
                "budget_tier": budget_tier,
                "banned_exercise_tags": banned_tags
            }
        }

        