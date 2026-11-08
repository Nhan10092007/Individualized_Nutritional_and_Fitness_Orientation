"""
Module: energy_calculator.py
Triển khai các công thức chuyển hóa sinh học & năng lượng chuẩn xác:
- Calo IN: Tính toán dưỡng chất theo khối lượng gam từ USDA & Viện Dinh Dưỡng Quốc Gia.
- Calo BURN: Tính toán tiêu hao năng lượng dựa trên chỉ số MET (Compendium of Physical Activities, Ainsworth et al. 2011 & ACSM).
"""

from typing import Dict, Any, Optional


def calculate_calories_burned_per_minute(met: float, body_weight_kg: float) -> float:
    """
    Tính tốc độ tiêu hao Calo mỗi phút (kcal/min) theo chuẩn ACSM:
    
    Cơ sở khoa học:
    1 MET = 3.5 ml O2 / (kg * min) (Mức tiêu thụ oxy nền chuẩn khi nghỉ ngơi)
    1 Lít O2 tiêu thụ tạo ra xấp xỉ 5 kcal năng lượng.
    
    Chứng minh công thức:
    VO2 (L/min) = (MET * 3.5 * Body_Weight_kg) / 1000
    Cal/min     = VO2 (L/min) * 5
                = (MET * 3.5 * Body_Weight_kg / 1000) * 5
                = (MET * 3.5 * Body_Weight_kg) / 200
                
    Args:
        met (float): Giá trị Metabolic Equivalent of Task từ Compendium (ví dụ: 8.0)
        body_weight_kg (float): Cân nặng cơ thể tính bằng kg (ví dụ: 70.0)
        
    Returns:
        float: Số kcal tiêu hao trong 1 phút hoạt động
    """
    if met <= 0 or body_weight_kg <= 0:
        raise ValueError("MET và Cân nặng phải lớn hơn 0")
    
    cal_per_min = (met * 3.5 * body_weight_kg) / 200.0
    return round(cal_per_min, 4)


def calculate_activity_duration_minutes(
    sets: int, 
    duration_per_set_sec: float, 
    rest_between_sets_sec: float = 0.0
) -> float:
    """
    Tính tổng thời gian hoạt động thực tế T (tính bằng phút) của bài tập dạng Sets/Reps.
    
    Công thức:
    T = [(số set * thời gian 1 set) + ((số set - 1) * thời gian nghỉ giữa set)] / 60
    
    Args:
        sets (int): Số set bài tập thực hiện (>= 1)
        duration_per_set_sec (float): Thời gian hoàn thành 1 set (giây)
        rest_between_sets_sec (float): Thời gian nghỉ giữa các set (giây)
        
    Returns:
        float: Tổng thời gian T tính bằng phút
    """
    if sets < 1:
        raise ValueError("Số set phải >= 1")
    if duration_per_set_sec <= 0:
        raise ValueError("Thời gian thực hiện 1 set phải > 0 giây")
    if rest_between_sets_sec < 0:
        raise ValueError("Thời gian nghỉ không được âm")
        
    total_seconds = (sets * duration_per_set_sec) + ((sets - 1) * rest_between_sets_sec)
    total_minutes = total_seconds / 60.0
    return round(total_minutes, 4)


def calculate_total_calories_burned(
    met: float, 
    body_weight_kg: float, 
    sets: int = 1, 
    duration_per_set_sec: Optional[float] = None, 
    rest_between_sets_sec: float = 0.0,
    continuous_duration_min: Optional[float] = None
) -> Dict[str, Any]:
    """
    Tính tổng số Calo tiêu thụ của một bài tập / hoạt động:
    Total Calo = Cal/min * T
    
    Hỗ trợ 2 chế độ:
    1. Tập theo hiệp (Sets/Reps gym, calisthenics, HIIT): tính T từ sets, time_per_set, rest
    2. Tập liên tục (Chạy bộ, bơi lội, đạp xe continuous): truyền continuous_duration_min
    
    Returns:
        dict: Chứa met, weight, total_minutes, cal_per_min, total_calories
    """
    cal_per_min = calculate_calories_burned_per_minute(met, body_weight_kg)
    
    if continuous_duration_min is not None and continuous_duration_min > 0:
        total_minutes = continuous_duration_min
    elif duration_per_set_sec is not None and duration_per_set_sec > 0:
        total_minutes = calculate_activity_duration_minutes(
            sets=sets,
            duration_per_set_sec=duration_per_set_sec,
            rest_between_sets_sec=rest_between_sets_sec
        )
    else:
        raise ValueError("Phải cung cấp thời gian hiệp tập (duration_per_set_sec) hoặc thời gian liên tục (continuous_duration_min)")

    total_calories = cal_per_min * total_minutes
    
    return {
        "met": met,
        "body_weight_kg": body_weight_kg,
        "cal_per_minute": round(cal_per_min, 2),
        "total_minutes": round(total_minutes, 2),
        "total_calories_burned": round(total_calories, 2)
    }


def calculate_food_nutrition_intake(
    actual_weight_g: float,
    calories_100g: float,
    protein_100g: float,
    fat_100g: float,
    carbs_100g: float,
    fiber_100g: float = 0.0
) -> Dict[str, float]:
    """
    Tính toán lượng Calo và các chất dinh dưỡng vi mô/vĩ mô nạp vào dựa trên khối lượng thực tế (g)
    
    Công thức:
    Nutrient_Actual = (actual_weight_g / 100.0) * Nutrient_100g
    """
    if actual_weight_g < 0:
        raise ValueError("Khối lượng thực phẩm không được âm")
        
    ratio = actual_weight_g / 100.0
    return {
        "actual_weight_g": round(actual_weight_g, 2),
        "calories": round(calories_100g * ratio, 2),
        "protein_g": round(protein_100g * ratio, 2),
        "fat_g": round(fat_100g * ratio, 2),
        "carbs_g": round(carbs_100g * ratio, 2),
        "fiber_g": round(fiber_100g * ratio, 2),
    }
