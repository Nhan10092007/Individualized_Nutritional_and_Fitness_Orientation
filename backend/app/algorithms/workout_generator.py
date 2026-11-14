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
    Rules for scientifically dividing your workout schedule:
    - <= 3 days/week: "Full Body" (Full body workout per session, good recovery)
    - 4 days/week: "Upper / Lower" (Alternating upper and lower body workouts)
    - >= 5 days/week: "Push / Pull / Legs" (Push / Pull / Leg exercises)
    """
    if available_days_count <=3:
        return "Full Body"
    elif available_days_count == 4:
        return "Upper/Lower"
    else:
        return "Push/Pull/Legs"

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
    - available_days: Example ['Mon', 'Wed', 'Fri']
    - session_duration_mins: Example 45 or 60 minutes
    - safe_pool: List of safe exercises that have passed the A3 filter
    OUTPUT:
    - Complete weekly workout schedule structure including exercises, number of sets, number of reps, and time rest between sets.
    """
    k = len(available_days)
    if k==0:
        return {"error": "No available days provided."}
    split_type = determine_split_type(k)
    max_time_sec = session_duration_mins*60

    weekly_usage: Dict[str, int] = {ex.get("id"): 0 for ex in safe_pool}
    weekly_schedule = []

    major_muscles = ["chest", "back", "quadriceps", "hamstrings", "glutes"]
    max_exercises_limit = 8 #ràng buộc trần 

    for session_idx, day_name in enumerate(available_days):
        session_muscles = get_muscles_for_session(split_type, session_idx)
        current_session_time_sec = 0.0
        used_in_session: Set[str] = set()
        chosen_exercise = []

        level_str = str(fitness_level).lower()
        if level_str in ["beginner", "1"]:
            sets = 2
        elif level_str in ["experienced", "2"]:
            sets = 3
        elif level_str in ["advanced", "3"]:
            sets = 3
        else:
            sets = 2
        
        reps = 10 if fitness_goal == "fat_loss" else 8 if fitness_goal == "muscle_gain" else 12
        duration_per_set_sec = 45.0
        transition_time_sec = 120.0

        for muscle in session_muscles:
            if len(chosen_exercise) >= max_exercises_limit:
                break

            candidates = [
                ex for ex in safe_pool if ex.get("target_muscle", "").lower() == muscle.lower() and ex.get("id") not in used_in_session
            ]

            if not candidates:
                continue

            candidates.sort(key = lambda x: weekly_usage.get(x.get("id"), 0))
            best_ex = candidates[0]
            if best_ex.get("target_muscle", "").lower() in major_muscles:
                rest_between_sets_sec = 150.0
            else:
                rest_between_sets_sec = 120.0

            
            ex_total_time_sec = (sets * duration_per_set_sec) + ((sets-1) * rest_between_sets_sec) + transition_time_sec

            if current_session_time_sec + ex_total_time_sec <= max_time_sec:
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
                current_session_time_sec += ex_total_time_sec
                used_in_session.add(best_ex.get("id"))
                weekly_usage[best_ex.get("id")] += 1

        # Vòng 2: Lấp đầy thời lượng CHỈ TỪ CÁC NHÓM CƠ CỦA CHÍNH BUỔI TẬP ĐÓ (session_muscles)
        # Nguyên tắc cốt lõi: Buổi nào chỉ tập cơ buổi đó (Push chỉ tập Ngực/Vai/Tay sau, tuyệt đối không bốc Chân hay Lưng)
        added_any = True
        while added_any:
            added_any = False
            for muscle in session_muscles:
                if len(chosen_exercise) >= max_exercises_limit:
                    break

                # Tìm bài tập tiếp theo thuộc CHÍNH nhóm cơ này mà chưa tập trong buổi hôm nay
                candidates = [
                    ex for ex in safe_pool
                    if ex.get("target_muscle", "").lower() == muscle.lower()
                    and ex.get("id") not in used_in_session
                ]

                # Nếu nhóm cơ này trong kho đã hết bài mới thì bỏ qua
                if not candidates:
                    continue

                candidates.sort(key=lambda x: weekly_usage.get(x.get("id"), 0))
                extra_ex = candidates[0]

                if extra_ex.get("target_muscle", "").lower() in major_muscles:
                    rest_between_sets_sec = 150.0
                else:
                    rest_between_sets_sec = 120.0
                
                ex_total_time_sec = (sets * duration_per_set_sec) + ((sets-1) * rest_between_sets_sec) + transition_time_sec

                #chỉ thêm vào nếu tgian ko vượt quá tgian trần
                if current_session_time_sec + ex_total_time_sec <= max_time_sec:
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
                    current_session_time_sec += ex_total_time_sec
                    used_in_session.add(extra_ex.get("id"))
                    weekly_usage[extra_ex.get("id")] += 1
                    added_any = True

        weekly_schedule.append({
            "day": day_name,
            "session_name": f"{split_type} - Session {session_idx+1}",
            "target_muscles": session_muscles,
            "actual_duration_mins": round(current_session_time_sec/60.0, 1),
            "max_allowed_mins": session_duration_mins,
            "exercise_count": len(chosen_exercise),
            "exercises": chosen_exercise
        })

    return {
        "split_type": split_type,
        "total_sessions": k,
        "weekly_schedule": weekly_schedule
    }



