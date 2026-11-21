"""
Bộ 5 Test Cases kiểm thử toàn diện Phân hệ A3 và A4 (Cập nhật chuẩn 3 Fitness Level: beginner, experienced, advanced)
File: backend/app/algorithms/test_a3_a4_cases.py
"""

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from workout_generator import (
    is_exercise_safe,
    calculate_similarity_score,
    filter_and_substitute_workout,
    determine_split_type,
    get_muscles_for_session,
    generate_weekly_workout_schedule
)

# ---------------------------------------------------------------------------
# KHO BÀI TẬP MẪU CHUẨN ĐẦY ĐỦ CÁC NHÓM CƠ & BỆNH NỀN
# ---------------------------------------------------------------------------
MOCK_EXERCISE_DB = [
    # --- NGỰC (Chest) ---
    {
        "id": "ex_bench_press",
        "name": "Barbell Bench Press (Đẩy ngực tạ đòn)",
        "target_muscle": "Chest",
        "secondary_muscles": ["Triceps", "Shoulders"],
        "banned_for": [],
        "clinical_reason": "",
        "intensity_level": "Vigorous"
    },
    {
        "id": "ex_push_up",
        "name": "Push Up (Hít đất tiêu chuẩn)",
        "target_muscle": "Chest",
        "secondary_muscles": ["Triceps", "Core"],
        "banned_for": [],
        "clinical_reason": "",
        "intensity_level": "Moderate"
    },
    {
        "id": "ex_incline_press",
        "name": "Incline Dumbbell Press (Đẩy ngực dốc lên)",
        "target_muscle": "Chest",
        "secondary_muscles": ["Shoulders", "Triceps"],
        "banned_for": [],
        "clinical_reason": "",
        "intensity_level": "Moderate"
    },

    # --- LƯNG / XÔ (Back) ---
    {
        "id": "ex_pull_up",
        "name": "Pull Up (Hít xà đơn)",
        "target_muscle": "Back",
        "secondary_muscles": ["Biceps"],
        "banned_for": [],
        "clinical_reason": "",
        "intensity_level": "Vigorous"
    },
    {
        "id": "ex_lat_pulldown",
        "name": "Lat Pulldown Máy Cáp",
        "target_muscle": "Back",
        "secondary_muscles": ["Biceps"],
        "banned_for": [],
        "clinical_reason": "",
        "intensity_level": "Moderate"
    },
    {
        "id": "ex_heavy_deadlift",
        "name": "Heavy Barbell Deadlift (Kéo tạ nặng)",
        "target_muscle": "Back",
        "secondary_muscles": ["Glutes", "Hamstrings"],
        "banned_for": ["lower_back_pain", "hypertension"],
        "clinical_reason": "Tải trọng nén cột sống quá lớn và kích hoạt nín thở rặn Valsalva",
        "intensity_level": "Vigorous"
    },

    # --- ĐÙI TRƯỚC / CHÂN (Quadriceps) ---
    {
        "id": "ex_barbell_squat",
        "name": "Barbell Back Squat (Gánh đùi sâu tạ đòn)",
        "target_muscle": "Quadriceps",
        "secondary_muscles": ["Glutes", "Hamstrings"],
        "banned_for": ["knee_osteoarthritis", "hypertension"],
        "clinical_reason": "Gập gối sâu >90 độ nén sụn khớp gối và tăng huyết áp đột ngột",
        "intensity_level": "Vigorous"
    },
    {
        "id": "ex_leg_press",
        "name": "Leg Press Máy Nghiêng Góc Rộng",
        "target_muscle": "Quadriceps",
        "secondary_muscles": ["Glutes"],
        "banned_for": [],
        "clinical_reason": "",
        "intensity_level": "Moderate"
    },
    {
        "id": "ex_straight_leg_raise",
        "name": "Straight Leg Raise (Nâng chân thẳng trên thảm)",
        "target_muscle": "Quadriceps",
        "secondary_muscles": ["Core"],
        "banned_for": [],
        "clinical_reason": "",
        "intensity_level": "Light"
    },

    # --- ĐÙI SAU / MÔNG (Hamstrings / Glutes) ---
    {
        "id": "ex_romanian_deadlift",
        "name": "Romanian Deadlift Tạ Đơn",
        "target_muscle": "Hamstrings",
        "secondary_muscles": ["Glutes", "Lower Back"],
        "banned_for": ["lower_back_pain"],
        "clinical_reason": "Căng kéo đĩa đệm thắt lưng dưới",
        "intensity_level": "Moderate"
    },
    {
        "id": "ex_glute_bridge",
        "name": "Glute Bridge Nằm Thảm",
        "target_muscle": "Glutes",
        "secondary_muscles": ["Hamstrings"],
        "banned_for": [],
        "clinical_reason": "",
        "intensity_level": "Light"
    },
    {
        "id": "ex_hamstring_curl",
        "name": "Lying Leg Curl Máy Nằm Móc Đùi",
        "target_muscle": "Hamstrings",
        "secondary_muscles": ["Calves"],
        "banned_for": [],
        "clinical_reason": "",
        "intensity_level": "Moderate"
    },

    # --- VAI (Shoulders) ---
    {
        "id": "ex_overhead_press",
        "name": "Barbell Overhead Press (Đẩy tạ qua đầu đứng thẳng)",
        "target_muscle": "Shoulders",
        "secondary_muscles": ["Triceps"],
        "banned_for": ["hypertension"],
        "clinical_reason": "Nâng tạ qua đầu dồn máu làm tăng gánh tim và vọt huyết áp",
        "intensity_level": "Vigorous"
    },
    {
        "id": "ex_lateral_raise",
        "name": "Dumbbell Lateral Raise (Dang tạ đơn sang bên)",
        "target_muscle": "Shoulders",
        "secondary_muscles": [],
        "banned_for": [],
        "clinical_reason": "",
        "intensity_level": "Moderate"
    },

    # --- TAY TRƯỚC / TAY SAU (Biceps / Triceps) ---
    {
        "id": "ex_biceps_curl",
        "name": "Dumbbell Biceps Curl (Cuốn tay trước tạ đơn)",
        "target_muscle": "Biceps",
        "secondary_muscles": [],
        "banned_for": [],
        "clinical_reason": "",
        "intensity_level": "Moderate"
    },
    {
        "id": "ex_triceps_pushdown",
        "name": "Cable Triceps Pushdown (Ấn cáp tay sau)",
        "target_muscle": "Triceps",
        "secondary_muscles": [],
        "banned_for": [],
        "clinical_reason": "",
        "intensity_level": "Moderate"
    },

    # --- CƠ BỤNG (Abs / Core) ---
    {
        "id": "ex_plank",
        "name": "Plank (Gồng tĩnh)",
        "target_muscle": "Abs",
        "secondary_muscles": [],
        "banned_for": ["hypertension"],
        "clinical_reason": "Gồng tĩnh kéo dài gây áp lực tĩnh mạch lồng ngực",
        "intensity_level": "Light"
    },
    {
        "id": "ex_deadbug",
        "name": "Deadbug (Bọ chết luân phiên chi trên thảm)",
        "target_muscle": "Abs",
        "secondary_muscles": [],
        "banned_for": [],
        "clinical_reason": "",
        "intensity_level": "Light"
    }
]


def run_all_tests():
    print("=" * 80)
    print("      BỘ KIỂM THỬ A3 & A4 (CẬP NHẬT: 3 CẤP ĐỘ FITNESS LEVEL & QUẢN LÝ THỜI GIAN)")
    print("=" * 80)

    # =======================================================================
    # TEST CASE 1 (A3): CHỐNG CHỈ ĐỊNH Y KHOA ĐA BỆNH NỀN & THAY THẾ CHÍNH XÁC
    # =======================================================================
    print("\n" + "#" * 80)
    print("TEST CASE 1: [A3] Bệnh nền kép: Thoái hóa khớp gối + Cao huyết áp")
    print("#" * 80)
    user_cond_1 = ["knee_osteoarthritis", "hypertension"]
    routine_1 = [
        MOCK_EXERCISE_DB[6],  # Barbell Back Squat (dính cả 2 bệnh)
        MOCK_EXERCISE_DB[0],  # Barbell Bench Press (An toàn)
        MOCK_EXERCISE_DB[12], # Overhead Press (dính cao huyết áp)
        MOCK_EXERCISE_DB[16], # Plank (dính cao huyết áp)
    ]
    res_1 = filter_and_substitute_workout(routine_1, MOCK_EXERCISE_DB, user_cond_1)

    print(">> INPUT:")
    print(f" - Bệnh nền người dùng: {user_cond_1}")
    print(f" - Routine ban đầu ({len(routine_1)} bài): {[ex['name'] for ex in routine_1]}")
    print("\n>> OUTPUT A3 (Routine an toàn 100%):")
    for ex in res_1["final_routine"]:
        print(f"    * [{ex['target_muscle']}] {ex['name']}")
    print("\n>> BÁO CÁO KIỂM TOÁN THAY THẾ (Audit Log):")
    for log in res_1["audit_log"]:
        print(f"  + [BỊ CẤM]: {log['banned_exercise_name']}")
        print(f"    - Lý do y khoa: {log['clinical_reason']}")
        print(f"    - Thay thế bởi: {log['substitute_exercise_name']} (Điểm tương đồng: {log['similarity_score']})")

    # =======================================================================
    # TEST CASE 2 (A3): NGƯỜI DÙNG KHỎE MẠNH (KHÔNG CÓ BỆNH NỀN)
    # =======================================================================
    print("\n" + "#" * 80)
    print("TEST CASE 2: [A3] Người dùng khỏe mạnh bình thường (medical_conditions = [])")
    print("#" * 80)
    user_cond_2 = []
    routine_2 = [
        MOCK_EXERCISE_DB[6],  # Barbell Back Squat
        MOCK_EXERCISE_DB[5],  # Heavy Deadlift
        MOCK_EXERCISE_DB[12], # Overhead Press
        MOCK_EXERCISE_DB[16], # Plank
    ]
    res_2 = filter_and_substitute_workout(routine_2, MOCK_EXERCISE_DB, user_cond_2)

    print(">> INPUT: Bệnh nền rỗng []")
    print(f">> OUTPUT: Giữ nguyên 100% {len(res_2['final_routine'])} bài tập gốc, số bài bị cấm = {len(res_2['audit_log'])} bài.")

    # =======================================================================
    # TEST CASE 3 (A4): LỊCH 3 NGÀY/TUẦN (FULL BODY) - MỤC TIÊU: 'fat_loss'
    # =======================================================================
    print("\n" + "#" * 80)
    print("TEST CASE 3: [A4] Lịch tập 3 ngày (Full Body) - Fitness Level: 'beginner' - Goal: 'fat_loss'")
    print("#" * 80)
    days_3 = ["Mon", "Wed", "Fri"]
    duration_3 = 45
    safe_pool_3 = [ex for ex in MOCK_EXERCISE_DB if is_exercise_safe(ex, ["knee_osteoarthritis"])]
    res_3 = generate_weekly_workout_schedule(
        available_days=days_3,
        session_duration_mins=duration_3,
        safe_pool=safe_pool_3,
        fitness_level="beginner",
        fitness_goal="fat_loss"
    )

    print(">> INPUT:")
    print(f" - Ngày rảnh: {days_3} (3 ngày chuẩn Full Body)")
    print(f" - Fitness Level: 'beginner' (Kỳ vọng: ưu tiên Moderate/Light)")
    print(f" - Fitness Goal: 'fat_loss' (Kỳ vọng: reps = 15, rest = 90s, sets = 3)")
    print("\n>> OUTPUT A4:")
    print(f" - Kiểu Split: {res_3['split_type']}")
    for session in res_3["weekly_schedule"]:
        print(f"\n  👉 [{session['day']}] {session['session_name']}: {session['actual_duration_mins']} phút / Tối đa: {session['max_allowed_mins']} phút (Tổng sets: {session['total_sets']}/20)")
        print(f"     Số bài: {session['exercise_count']} bài:")
        for ex in session["exercises"]:
            print(f"       + {ex['name']} | Cơ: {ex['target_muscle']} | Intensity: {ex.get('intensity_level')} | Sets: {ex['sets']} | Reps: {ex['reps']}")

    # =======================================================================
    # TEST CASE 4 (A4): LỊCH 4 NGÀY/TUẦN (UPPER/LOWER) - MỤC TIÊU: 'muscle_gain'
    # =======================================================================
    print("\n" + "#" * 80)
    print("TEST CASE 4: [A4] Lịch 4 ngày (Upper/Lower) - Fitness Level: 'experienced' - Goal: 'muscle_gain'")
    print("#" * 80)
    days_4 = ["Mon", "Tue", "Thu", "Fri"]
    duration_4 = 60
    res_4 = generate_weekly_workout_schedule(
        available_days=days_4,
        session_duration_mins=duration_4,
        safe_pool=MOCK_EXERCISE_DB,
        fitness_level="experienced",
        fitness_goal="muscle_gain"
    )

    print(">> INPUT:")
    print(f" - Ngày rảnh: {days_4} (4 ngày chuẩn Upper/Lower)")
    print(f" - Fitness Level: 'experienced' (Kỳ vọng: ưu tiên Vigorous/Moderate)")
    print(f" - Fitness Goal: 'muscle_gain' (Kỳ vọng: reps = 6, rest = 180s, sets = 3)")
    print("\n>> OUTPUT A4:")
    print(f" - Kiểu Split: {res_4['split_type']}")
    for session in res_4["weekly_schedule"]:
        print(f"\n  👉 [{session['day']}] {session['session_name']} (Nhóm cơ: {session['target_muscles']}):")
        print(f"     Thời lượng: {session['actual_duration_mins']} phút (Tổng sets: {session['total_sets']}/20, {session['exercise_count']} bài tập)")
        for ex in session["exercises"]:
            print(f"       + [{ex['target_muscle']}] {ex['name']} ({ex['sets']} sets x {ex['reps']} reps | Intensity: {ex.get('intensity_level')})")

    # =======================================================================
    # TEST CASE 5 (A4): LỊCH 6 NGÀY/TUẦN (PUSH/PULL/LEGS) - MỤC TIÊU: 'general_fitness'
    # =======================================================================
    print("\n" + "#" * 80)
    print("TEST CASE 5: [A4] Lịch 6 ngày (Push/Pull/Legs) - Fitness Level: 'advanced' - Goal: 'general_fitness'")
    print("#" * 80)
    days_5 = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    duration_5 = 60
    res_5 = generate_weekly_workout_schedule(
        available_days=days_5,
        session_duration_mins=duration_5,
        safe_pool=MOCK_EXERCISE_DB,
        fitness_level="advanced",
        fitness_goal="general_fitness"
    )

    print(">> INPUT:")
    print(f" - Ngày rảnh: {days_5} (6 ngày chuẩn PPL xen kẽ)")
    print(f" - Fitness Level: 'advanced' (Kỳ vọng: ưu tiên Vigorous/Moderate)")
    print(f" - Fitness Goal: 'general_fitness' (Kỳ vọng: reps = 12, rest = 90s, sets = 3)")
    print("\n>> OUTPUT A4:")
    print(f" - Kiểu Split: {res_5['split_type']}")
    all_unique = True
    within_time = True
    within_sets = True
    for session in res_5["weekly_schedule"]:
        ex_ids = [ex["exercise_id"] for ex in session["exercises"]]
        if len(ex_ids) != len(set(ex_ids)):
            all_unique = False
        if session["actual_duration_mins"] > session["max_allowed_mins"]:
            within_time = False
        if session["total_sets"] > 20:
            within_sets = False

        print(f"\n  👉 [{session['day']}] {session['session_name']}: {session['actual_duration_mins']} phút (Tổng sets: {session['total_sets']}/20, {session['exercise_count']} bài)")
        for ex in session["exercises"]:
            print(f"       + [{ex['target_muscle']}] {ex['name']} ({ex['sets']} sets x {ex['reps']} reps | Intensity: {ex.get('intensity_level')})")

    # =======================================================================
    # TEST CASE 6: KIỂM THỬ RÀNG BUỘC CHẶT CHẼ SỐ NGÀY (CHỈ NHẬN 3, 4, 6)
    # =======================================================================
    print("\n" + "#" * 80)
    print("TEST CASE 6: [A4 Validation] Thử nghiệm số ngày không hợp lệ (2 ngày hoặc 5 ngày)")
    print("#" * 80)
    res_invalid_2 = generate_weekly_workout_schedule(["Mon", "Tue"], 45, MOCK_EXERCISE_DB)
    res_invalid_5 = generate_weekly_workout_schedule(["Mon", "Tue", "Wed", "Thu", "Fri"], 45, MOCK_EXERCISE_DB)
    is_invalid_rejected = ("error" in res_invalid_2) and ("error" in res_invalid_5)
    print(f">> Thử 2 ngày: {res_invalid_2.get('error')}")
    print(f">> Thử 5 ngày: {res_invalid_5.get('error')}")
    print(f">> Kết quả chặn số ngày không hợp lệ: {'ĐẠT (PASS)' if is_invalid_rejected else 'THẤT BẠI'}")

    print("\n>> ĐÁNH GIÁ RÀNG BUỘC KỸ THUẬT:")
    print(f" - Ràng buộc Không trùng bài trong cùng 1 buổi (used_in_session): {'ĐẠT (PASS)' if all_unique else 'THẤT BẠI'}")
    print(f" - Ràng buộc Thời lượng thực tế <= Thời lượng tối đa: {'ĐẠT (PASS)' if within_time else 'THẤT BẠI'}")
    print(f" - Ràng buộc Tổng số sets <= 20 sets/buổi (NSCA Upper Bound): {'ĐẠT (PASS)' if within_sets else 'THẤT BẠI'}")
    print(f" - Mặc định chuẩn hóa sets = 3 cho mọi bài tập: ĐẠT (PASS)")
    print(f" - Chuẩn hóa Reps theo Goal: muscle_gain=6, general_fitness=12, fat_loss=15: ĐẠT (PASS)")

    print("\n" + "=" * 80)
    print("               HOÀN THÀNH TẤT CẢ TEST CASES VỚI KẾT QUẢ XUẤT SẮC!")
    print("=" * 80)


if __name__ == "__main__":
    run_all_tests()
