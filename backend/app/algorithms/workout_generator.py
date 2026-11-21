"""
Module: workout_generator.py
Alias: A3, A4
"""

from typing import List, Dict, Any, Set

#A3

def is_exercise_safe(exercise: Dict[str, Any], medical_conditions: List[str]) -> bool:
    """
    Return True if the exercise is completely not contain any medical conditions of user.
    """
    if not medical_conditions:
        return True

    banned_for = exercise.get("banned_for", [])  

    for cond in medical_conditions:
        if cond in banned_for:
            return False
    return True

def calculate_similarity_score(candidate: Dict[str, Any], banned_ex: Dict[str, Any]) -> float:
    """
    Maximum Point: 100
    - Target muscle group overlap: +70 points
    - Secondary muscle group overlap: +30 points
    """
    score = 0.0
    cand_target = candidate.get("target_muscle", "")
    banned_target = banned_ex.get("target_muscle", "")
    banned_secondary = banned_ex.get("secondary_muscles", [])

    if cand_target and cand_target.lower() == banned_target.lower():
        score += 70.0
    if cand_target.lower() in [muscle.lower() for muscle in banned_secondary]:
        score += 30.0
    return score

def filter_and_substitute_workout(
    routine: List[Dict[str, Any]],
    full_db: List[Dict[str, Any]],
    medical_conditions: List[str]
) -> Dict[str, Any]:
    """
    INPUT:
    - routine: Initial planned workout list
    - full_db: The entire workout library in the system
    - medical_conditions: List of the user's underlying medical conditions
    OUTPUT:
    - final_routine: Workout schedule that has been 100% safely cleaned
    - audit_log: Report explaining why a workout was banned and which workout replaced it
    """
    medical_conditions = medical_conditions or[]
    safe_list = []
    banned_list = []
    audit_log = []

    #1: Filter directly banned exercises
    for ex in routine:
        if is_exercise_safe(ex, medical_conditions):
            safe_list.append(ex)
        else:
            banned_list.append(ex)
    final_routine = list(safe_list)

    #2: Rating score then find substitute
    for banned_ex in banned_list:
        best_candidate = None
        max_score = -1.0
        for candidate in full_db:
            if candidate.get("id") == banned_ex.get("id"):
                continue
            if any(item.get("id") == candidate.get("id") for item in final_routine):
                continue
            if not is_exercise_safe(candidate, medical_conditions):
                continue
            score = calculate_similarity_score(candidate, banned_ex)
            if score > max_score:
                max_score = score
                best_candidate = candidate
        if best_candidate and max_score > 0:
            final_routine.append(best_candidate)
            audit_log.append({
                "banned_exercise_name": banned_ex.get("name"),
                "clinical_reason": banned_ex.get("clinical_reason", "Chống chỉ định y khoa với bệnh nền"),
                "substitute_exercise_name": best_candidate.get("name"),
                "similarity_score": max_score
            })
        else:
            audit_log.append({
                "banned_exercise_name": banned_ex.get("name"),
                "clinical_reason": banned_ex.get("clinical_reason", "Chống chỉ định y khoa với bệnh nền"),
                "substitute_exercise_name": None,
                "similarity_score": 0.0
            })
    return {
        "final_routine": final_routine,
        "audit_log": audit_log
    }
#A4
def determine_split_type(available_days_count: int) -> str:
    """
    Quy tắc phân bổ lịch tập chuẩn hóa theo chu kỳ phục hồi sinh lý:
    - 3 ngày/tuần: "Full Body" (Toàn thân, cách ngày)
    - 4 ngày/tuần: "Upper/Lower" (Thân trên / Thân dưới xen kẽ)
    - 6 ngày/tuần: "Push/Pull/Legs" (Đẩy - Kéo - Chân lặp 2 chu kỳ)
    """
    if available_days_count == 3:
        return "Full Body"
    elif available_days_count == 4:
        return "Upper/Lower"
    elif available_days_count == 6:
        return "Push/Pull/Legs"
    else:
        raise ValueError(
            f"Số ngày tập không hợp lệ ({available_days_count} ngày). "
            f"Hệ thống chỉ hỗ trợ chuẩn hóa 3 ngày (Full Body), 4 ngày (Upper/Lower) hoặc 6 ngày (Push/Pull/Legs)."
        )

def get_intensity_penalty(exercise: Dict[str, Any], fitness_level: str = "beginner") -> int:
    """
    Tính điểm phạt cường độ (Intensity Penalty) để ưu tiên bài tập mềm theo cấp độ:
    - beginner: Ưu tiên Moderate và Light (penalty = 0), Vigorous xếp sau (penalty = 1).
    - experienced / advanced: Ưu tiên Vigorous và Moderate (penalty = 0), Light xếp sau (penalty = 1).
    """
    intensity = str(exercise.get("intensity_level", "Moderate")).capitalize()
    level = str(fitness_level).lower()

    if level in ["beginner", "1"]:
        return 1 if intensity == "Vigorous" else 0
    else:
        return 1 if intensity == "Light" else 0

def get_muscles_for_session(split_type : str, session_index: int) -> List[str]:
    """
    Return the list of target muscles for the given session based on the split type and session index.
    """
    if split_type == "Full Body":
        return ["Chest", "Back", "Quadriceps", "Hamstrings", "Shoulders", "Abs"]
    elif split_type == "Upper/Lower":
        if session_index%2==0:
            return ["Chest", "Back", "Shoulders", "Biceps", "Triceps"]
        else:
            return ["Quadriceps", "Hamstrings", "Glutes", "Calves", "Abs"]
    else :
        mod = session_index % 3
        if mod == 0:
            return ["Chest", "Shoulders", "Triceps"]
        elif mod == 1:
            return ["Back", "Biceps", "Rear Delts"]
        else:
            return ["Quadriceps", "Hamstrings", "Glutes", "Calves", "Abs"]

# Bảng tham số động theo mục tiêu rèn luyện (Chuẩn hóa nhịp độ 3s/rep và thời gian nghỉ NSCA)
GOAL_TIMING_CONFIG = {
    "fat_loss": {
        "reps": 15,
        "duration_per_set_sec": 45.0,     # 15 reps * 3.0s/rep
        "rest_sec": 90.0,                 # 90 giây theo NSCA Table 17.11
        "transition_time_sec": 60.0       # 60 giây chuyển bài / set up
    },

    "muscle_gain": {
        "reps": 6,
        "duration_per_set_sec": 18.0,     # 6 reps * 3.0s/rep
        "rest_sec": 180.0,                # 180 giây (3 phút) hồi phục ATP-CP
        "transition_time_sec": 60.0       # 60 giây chuyển bài / set up
    },

    "general_fitness": {
        "reps": 12,
        "duration_per_set_sec": 36.0,     # 12 reps * 3.0s/rep
        "rest_sec": 90.0,                 # 90 giây theo NSCA Table 17.11
        "transition_time_sec": 60.0       # 60 giây chuyển bài / set up
    }
}

def _build_exercise_entry(
    exercise: Dict[str, Any],
    sets: int,
    reps: int,
    rest_between_sets_sec: float,
    transition_time_sec: float,
    ex_total_time_sec: float,
) -> Dict[str, Any]:
    """Build a scheduled exercise entry with set/rest/transition timing fields."""
    return {
        "exercise_id": exercise.get("id"),
        "name": exercise.get("name"),
        "target_muscle": exercise.get("target_muscle"),
        "intensity_level": exercise.get("intensity_level", "Moderate"),
        "sets": sets,
        "reps": reps,
        "rest_seconds": int(rest_between_sets_sec),
        "rest_between_exercises_seconds": int(transition_time_sec),
        "estimated_time_seconds": int(ex_total_time_sec),
    }


def generate_weekly_workout_schedule(
    available_days: List[str],
    session_duration_mins: int,
    safe_pool: List[Dict[str, Any]],
    fitness_level: str = "beginner",
    fitness_goal: str = "general_fitness"
) -> Dict[str, Any]:
    """
    INPUT:
    - available_days: Chỉ nhận 3 ngày (Full Body), 4 ngày (Upper/Lower) hoặc 6 ngày (PPL)
    - session_duration_mins: Thời gian trần của buổi tập (VD: 45 hoặc 60 phút)
    - safe_pool: Danh sách bài tập an toàn đã qua bộ lọc A3 (kèm intensity_level)
    - fitness_level: 'beginner', 'experienced', 'advanced'
    - fitness_goal: 'muscle_gain', 'fat_loss', 'general_fitness'
    OUTPUT:
    - Lịch tập tuần chuẩn hóa với 2 chốt chặn: Tổng Sets <= 20 VÀ Thời gian <= thời gian user chọn.
    """
    k = len(available_days)
    if k == 0:
        return {"error": "No available days provided."}
    if k not in [3, 4, 6]:
        return {
            "error": f"Số ngày tập không hợp lệ ({k} ngày). Hệ thống chỉ hỗ trợ 3 ngày (Full Body), 4 ngày (Upper/Lower) hoặc 6 ngày (Push/Pull/Legs)."
        }

    DAY_ORDER = {"Mon": 1, "Tue": 2, "Wed": 3, "Thu": 4, "Fri": 5, "Sat": 6, "Sun": 7}
    available_days = sorted(available_days, key=lambda d: DAY_ORDER.get(d, 99))
    split_type = determine_split_type(k)
    max_time_sec = session_duration_mins * 60

    weekly_usage: Dict[str, int] = {ex.get("id"): 0 for ex in safe_pool}
    weekly_schedule = []

    # Hai chốt chặn dừng (Stopping Conditions) theo NSCA & Volume Management:
    max_sets_limit = 20  # Ngưỡng an toàn trên: tối đa 20 sets/buổi (chống Junk Volume)
    sets = 3             # Mặc định 3 sets/bài theo Multiple-set System (NSCA / ACSM)

    goal_key = str(fitness_goal).lower() if fitness_goal else "general_fitness"
    timing = GOAL_TIMING_CONFIG.get(goal_key, GOAL_TIMING_CONFIG["general_fitness"])
    reps = timing["reps"]
    duration_per_set_sec = timing["duration_per_set_sec"]
    transition_time_sec = timing["transition_time_sec"]
    rest_between_sets_sec = timing["rest_sec"]

    ex_total_time_sec = (sets * duration_per_set_sec) + ((sets - 1) * rest_between_sets_sec) + transition_time_sec

    for session_idx, day_name in enumerate(available_days):
        session_muscles = get_muscles_for_session(split_type, session_idx)
        current_session_time_sec = 0.0
        current_session_sets = 0
        used_in_session: Set[str] = set()
        chosen_exercise = []

        # VÒNG 1: Phủ đều tất cả nhóm cơ của buổi tập
        for muscle in session_muscles:
            if current_session_sets + sets > max_sets_limit:
                break

            candidates = [
                ex for ex in safe_pool
                if ex.get("target_muscle", "").lower() == muscle.lower()
                and ex.get("id") not in used_in_session
            ]

            if not candidates:
                continue

            # Ưu tiên 1: Cường độ intensity_level phù hợp với Level
            # Ưu tiên 2: Bài ít xuất hiện trong tuần nhất (weekly_usage)
            candidates.sort(key=lambda x: (
                get_intensity_penalty(x, fitness_level),
                weekly_usage.get(x.get("id"), 0)
            ))
            best_ex = candidates[0]

            if current_session_sets + sets <= max_sets_limit and current_session_time_sec + ex_total_time_sec <= max_time_sec:
                chosen_exercise.append(
                    _build_exercise_entry(
                        best_ex,
                        sets,
                        reps,
                        rest_between_sets_sec,
                        transition_time_sec,
                        ex_total_time_sec,
                    )
                )
                current_session_sets += sets
                current_session_time_sec += ex_total_time_sec
                used_in_session.add(best_ex.get("id"))
                weekly_usage[best_ex.get("id")] += 1

        # VÒNG 2: Lấp đầy Volume & Thời lượng cho chính các nhóm cơ của buổi đó
        added_any = True
        while added_any:
            added_any = False
            for muscle in session_muscles:
                if current_session_sets + sets > max_sets_limit:
                    break

                candidates = [
                    ex for ex in safe_pool
                    if ex.get("target_muscle", "").lower() == muscle.lower()
                    and ex.get("id") not in used_in_session
                ]

                if not candidates:
                    continue

                candidates.sort(key=lambda x: (
                    get_intensity_penalty(x, fitness_level),
                    weekly_usage.get(x.get("id"), 0)
                ))
                extra_ex = candidates[0]

                if current_session_sets + sets <= max_sets_limit and current_session_time_sec + ex_total_time_sec <= max_time_sec:
                    chosen_exercise.append(
                        _build_exercise_entry(
                            extra_ex,
                            sets,
                            reps,
                            rest_between_sets_sec,
                            transition_time_sec,
                            ex_total_time_sec,
                        )
                    )
                    current_session_sets += sets
                    current_session_time_sec += ex_total_time_sec
                    used_in_session.add(extra_ex.get("id"))
                    weekly_usage[extra_ex.get("id")] += 1
                    added_any = True

        weekly_schedule.append({
            "day": day_name,
            "session_name": f"{split_type} - Session {session_idx+1}",
            "target_muscles": session_muscles,
            "actual_duration_mins": round(current_session_time_sec / 60.0, 1),
            "max_allowed_mins": session_duration_mins,
            "total_sets": current_session_sets,
            "exercise_count": len(chosen_exercise),
            "exercises": chosen_exercise
        })

    return {
        "split_type": split_type,
        "total_sessions": k,
        "weekly_schedule": weekly_schedule
    }



