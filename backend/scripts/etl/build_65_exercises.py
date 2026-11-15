"""
Tạo bộ dữ liệu 65 bài tập thực thụ chuẩn hóa từ backend/data/raw/exercises.json
khớp hoàn toàn với schema ORM `Exercise`:
id, category, name_vi, name_en, met_value, intensity_level, description,
equipment, instructions, common_mistakes, image, video_url,
target_muscle, secondary_muscle, banned_for, clinical_reasons, source

100% LÀ CÁC BÀI TẬP THỰC THỤ (Strength, Hypertrophy, Calisthenics, Core),
HOÀN TOÀN LOẠI BỎ CÁC BÀI GIÃN CƠ / KHỞI ĐỘNG (STRETCHING / MOBILITY).

Phủ đều toàn bộ 11 nhóm cơ chính và 3 cấp độ vận động (Light, Moderate, Vigorous):
- 1. Chest - Cơ ngực: 7 bài
- 2. Back - Cơ lưng/xô: 7 bài
- 3. Shoulders - Cơ vai: 6 bài
- 4. Rear Delts - Cơ vai sau: 3 bài
- 5. Biceps - Tay trước: 5 bài
- 6. Triceps - Tay sau: 5 bài
- 7. Quadriceps - Đùi trước: 6 bài
- 8. Hamstrings - Đùi sau: 6 bài
- 9. Glutes - Cơ mông: 6 bài
- 10. Calves - Bắp chân: 6 bài
- 11. Abs - Cơ bụng & Core: 8 bài
Tổng cộng: ĐÚNG 65 BÀI TẬP THỰC THỤ.
"""

import json
from pathlib import Path
from typing import Any

from app.config import BACKEND_DIR

RAW_EXERCISES_PATH = BACKEND_DIR / "data" / "raw" / "exercises.json"
PROCESSED_65_PATH = BACKEND_DIR / "data" / "processed" / "exercises_65.json"
CDN_BASE = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises"

EXERCISE_DEFINITIONS: list[dict[str, Any]] = [
    # ================= 1. CHEST - NGỰC (7 bài thực thụ) =================
    {
        "key": "barbell bench press - medium grip",
        "name_vi": "Đẩy ngực ngang tạ đòn (Bench Press)",
        "target_muscle": "Chest",
        "secondary_muscle": ["Triceps", "Shoulders"],
        "met_value": 6.0,
        "intensity_level": "Vigorous",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Ưỡn lưng quá mức làm mất ổn định cột sống",
            "Không hạ tạ chạm nhẹ ngực giữa mà nhấp nhả trên cao",
            "Bè cùi chỏ vuông góc 90 độ gây đau khớp vai",
        ],
    },
    {
        "key": "pushups",
        "name_vi": "Hít đất tiêu chuẩn (Push-up)",
        "target_muscle": "Chest",
        "secondary_muscle": ["Triceps", "Shoulders", "Abs"],
        "met_value": 4.5,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Võng lưng hoặc chổng mông lên quá cao",
            "Cùi chỏ bè sang hai bên thay vì tạo góc 45 độ với thân người",
            "Không gồng chặt cơ bụng trong suốt quá trình chuyển động",
        ],
    },
    {
        "key": "incline dumbbell press",
        "name_vi": "Đẩy ngực trên ghế dốc tạ đơn (Incline Dumbbell Press)",
        "target_muscle": "Chest",
        "secondary_muscle": ["Shoulders", "Triceps"],
        "met_value": 5.5,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Chỉnh ghế quá dốc (>45 độ) khiến áp lực dồn hết vào cơ vai",
            "Chạm tạ mạnh vào nhau ở đỉnh gây mất áp lực liên tục lên cơ ngực",
        ],
    },
    {
        "key": "dumbbell flyes",
        "name_vi": "Banh ngực tạ đơn (Dumbbell Flyes)",
        "target_muscle": "Chest",
        "secondary_muscle": ["Shoulders"],
        "met_value": 4.5,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Khóa thẳng khớp khuỷu tay làm quá tải khớp khuỷu",
            "Hạ tạ quá sâu vượt qua biên độ an toàn của khớp vai",
        ],
    },
    {
        "key": "dips - chest version",
        "name_vi": "Chống xà kép ngực (Chest Dips)",
        "target_muscle": "Chest",
        "secondary_muscle": ["Triceps", "Shoulders"],
        "met_value": 6.0,
        "intensity_level": "Vigorous",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Không nghiêng thân người về phía trước khiến cơ tay sau chịu lực chính",
            "Xuống quá sâu gây chèn ép bao khớp vai",
        ],
    },
    {
        "key": "barbell incline bench press - medium grip",
        "name_vi": "Đẩy ngực trên đòn tạ (Incline Barbell Bench Press)",
        "target_muscle": "Chest",
        "secondary_muscle": ["Shoulders", "Triceps"],
        "met_value": 6.0,
        "intensity_level": "Vigorous",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Hạ đòn tạ quá sát cổ thay vì chạm ngực trên",
            "Nhấc mông khỏi ghế đẩy tạo đà gian lận",
        ],
    },
    {
        "key": "cable crossover",
        "name_vi": "Ép ngực dây cáp chéo (Cable Crossover)",
        "target_muscle": "Chest",
        "secondary_muscle": ["Shoulders"],
        "met_value": 4.5,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Gập khuỷu tay quá nhiều biến thành bài đẩy cáp",
            "Nhún nhảy đung đưa thân người lấy đà",
        ],
    },

    # ================= 2. BACK - LƯNG / XÔ (7 bài thực thụ) =================
    {
        "key": "pullups",
        "name_vi": "Hít xà đơn (Pull-up)",
        "target_muscle": "Back",
        "secondary_muscle": ["Biceps", "Shoulders"],
        "met_value": 6.0,
        "intensity_level": "Vigorous",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Đung đưa lăng người (kipping) khi chưa đủ lực kéo tĩnh",
            "Không kéo cằm vượt quá thanh xà",
            "Thả rơi người tự do ở cuối động tác gây sốc khớp vai",
        ],
    },
    {
        "key": "barbell deadlift",
        "name_vi": "Kéo tạ đòn Deadlift (Barbell Deadlift)",
        "target_muscle": "Back",
        "secondary_muscle": ["Hamstrings", "Glutes", "Quadriceps"],
        "met_value": 6.0,
        "intensity_level": "Vigorous",
        "banned_for": ["lower_back_pain", "herniated_disc", "hypertension"],
        "clinical_reasons": "Tạo tải trọng nén và lực cắt cực lớn lên các đĩa đệm cột sống thắt lưng L4-L5 và S1.",
        "common_mistakes": [
            "Cong tròn lưng dưới khi bắt đầu nhấc tạ",
            "Để thanh đòn rời xa cẳng chân làm tăng cánh tay đòn tác động lên lưng dưới",
            "Ngả người ra sau quá mức ở đỉnh chuyển động",
        ],
    },
    {
        "key": "bent over barbell row",
        "name_vi": "Chèo tạ đòn gập người (Bent Over Barbell Row)",
        "target_muscle": "Back",
        "secondary_muscle": ["Biceps", "Shoulders"],
        "met_value": 6.0,
        "intensity_level": "Vigorous",
        "banned_for": ["lower_back_pain", "herniated_disc"],
        "clinical_reasons": "Tư thế gập người duy trì tải trọng tĩnh lâu dài lên cột sống thắt lưng.",
        "common_mistakes": [
            "Gù lưng khi nâng tạ",
            "Đứng quá thẳng người khiến bài tập chuyển sang ăn vào cơ cầu vai",
            "Dùng quán tính cơ thể giật tạ lên",
        ],
    },
    {
        "key": "wide-grip lat pulldown",
        "name_vi": "Kéo xô máy rộng tay (Wide-Grip Lat Pulldown)",
        "target_muscle": "Back",
        "secondary_muscle": ["Biceps", "Shoulders"],
        "met_value": 5.0,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Ngả người ra sau quá sâu (>45 độ) biến thành bài kéo lưng giữa",
            "Kéo thanh đòn ra sau gáy gây chấn thương khớp vai",
            "Dùng cẳng tay giật tạ thay vì dùng cơ xô ép xuống",
        ],
    },
    {
        "key": "seated cable rows",
        "name_vi": "Kéo cáp ngồi chèo xô (Seated Cable Row)",
        "target_muscle": "Back",
        "secondary_muscle": ["Biceps", "Shoulders"],
        "met_value": 4.5,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Đung đưa cột sống ra trước về sau để lấy đà",
            "Rụt vai lên tai thay vì hạ vai ép chặt bả vai",
        ],
    },
    {
        "key": "one-arm dumbbell row",
        "name_vi": "Chèo tạ đơn một tay (One-Arm Dumbbell Row)",
        "target_muscle": "Back",
        "secondary_muscle": ["Biceps", "Shoulders"],
        "met_value": 5.0,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Xoay vặn thân người quá mức ở đỉnh chuyển động",
            "Gù cột sống lưng dưới khi chống tay lên ghế",
        ],
    },
    {
        "key": "t-bar row with handle",
        "name_vi": "Chèo xô tạ đòn chữ T (T-Bar Row)",
        "target_muscle": "Back",
        "secondary_muscle": ["Biceps", "Shoulders"],
        "met_value": 6.0,
        "intensity_level": "Vigorous",
        "banned_for": ["lower_back_pain", "herniated_disc"],
        "clinical_reasons": "Tư thế gập người chịu tải lớn tạo áp lực nén cao lên các đốt sống thắt lưng L4-L5.",
        "common_mistakes": [
            "Võng lưng hoặc gù lưng tròn làm mất ổn định cột sống",
            "Dùng đà gối giật người lên để nâng tạ",
        ],
    },

    # ================= 3. SHOULDERS - VAI (6 bài thực thụ) =================
    {
        "key": "standing military press",
        "name_vi": "Đẩy vai qua đầu tạ đòn (Overhead Press)",
        "target_muscle": "Shoulders",
        "secondary_muscle": ["Triceps"],
        "met_value": 6.0,
        "intensity_level": "Vigorous",
        "banned_for": ["shoulder_impingement", "hypertension"],
        "clinical_reasons": "Góc đẩy đứng qua đầu với tải trọng lớn chèn ép khoang dưới mỏm cùng vai và tăng áp lực tâm thu.",
        "common_mistakes": [
            "Ưỡn lưng dưới quá đà để đẩy tạ lên",
            "Đẩy thanh đòn đi theo đường vòng cung xa cơ thể",
        ],
    },
    {
        "key": "side lateral raise",
        "name_vi": "Banh tạ đơn sang hai bên (Lateral Raise)",
        "target_muscle": "Shoulders",
        "secondary_muscle": [],
        "met_value": 4.0,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Nhún người đung đưa để lấy đà nâng tạ",
            "Nâng tạ cao hơn vai khiến cơ cầu vai (traps) ăn hết lực",
            "Khóa thẳng khuỷu tay thay vì gập nhẹ",
        ],
    },
    {
        "key": "front dumbbell raise",
        "name_vi": "Nâng tạ đơn phía trước (Front Dumbbell Raise)",
        "target_muscle": "Shoulders",
        "secondary_muscle": ["Chest"],
        "met_value": 4.0,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Ngả người ra sau khi nâng tạ",
            "Để tạ rơi tự do khi hạ xuống",
        ],
    },
    {
        "key": "seated dumbbell press",
        "name_vi": "Đẩy vai ngồi ghế tựa tạ đơn (Seated DB Shoulder Press)",
        "target_muscle": "Shoulders",
        "secondary_muscle": ["Triceps"],
        "met_value": 5.0,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Chạm tạ mạnh vào nhau ở đỉnh chuyển động",
            "Hạ tạ không đủ sâu (chưa tới ngang tầm tai)",
        ],
    },
    {
        "key": "arnold dumbbell press",
        "name_vi": "Đẩy vai xoay tạ đơn Arnold (Arnold Dumbbell Press)",
        "target_muscle": "Shoulders",
        "secondary_muscle": ["Triceps"],
        "met_value": 5.0,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Xoay cổ tay quá sớm khi tạ chưa qua mặt",
            "Ưỡn cong lưng dưới khi đẩy tạ lên đỉnh",
        ],
    },
    {
        "key": "upright barbell row",
        "name_vi": "Kéo tạ đòn thẳng đứng tập cầu vai (Upright Barbell Row)",
        "target_muscle": "Shoulders",
        "secondary_muscle": ["Biceps", "Back"],
        "met_value": 5.0,
        "intensity_level": "Moderate",
        "banned_for": ["shoulder_impingement"],
        "clinical_reasons": "Chuyển động xoay trong khớp vai kết hợp nâng tay cao có nguy cơ chèn ép khoang dưới mỏm cùng vai.",
        "common_mistakes": [
            "Cầm tay quá hẹp làm bó khớp cổ tay và khuỷu tay",
            "Kéo tạ quá cao vượt qua tầm xương đòn",
        ],
    },

    # ================= 4. REAR DELTS - VAI SAU (3 bài thực thụ) =================
    {
        "key": "reverse flyes",
        "name_vi": "Banh tạ đơn gập người vai sau (Rear Delt Flyes)",
        "target_muscle": "Rear Delts",
        "secondary_muscle": ["Back"],
        "met_value": 4.0,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Dùng đà thân người để vung tạ",
            "Gập khuỷu tay quá nhiều biến thành bài chèo lưng",
        ],
    },
    {
        "key": "face pull",
        "name_vi": "Kéo cáp dây thừng vào mặt (Face Pull)",
        "target_muscle": "Rear Delts",
        "secondary_muscle": ["Shoulders", "Back"],
        "met_value": 4.5,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Kéo dây thừng về ngực thay vì kéo về ngang tầm mắt/trán",
            "Không xoay cẳng tay ra ngoài ở cuối chuyển động",
            "Dùng mức tạ quá nặng làm mất tư thế chuẩn",
        ],
    },
    {
        "key": "seated bent-over rear delt raise",
        "name_vi": "Ngồi gập người banh tạ đơn vai sau (Seated Rear Delt Raise)",
        "target_muscle": "Rear Delts",
        "secondary_muscle": ["Back"],
        "met_value": 4.0,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Dùng cơ lưng trên co kéo thay vì dùng vai sau",
            "Nâng tạ bằng cách giật thân người khỏi đùi",
        ],
    },

    # ================= 5. BICEPS - TAY TRƯỚC (5 bài thực thụ) =================
    {
        "key": "barbell curl",
        "name_vi": "Cuốn tạ đòn tay trước (Barbell Curl)",
        "target_muscle": "Biceps",
        "secondary_muscle": [],
        "met_value": 4.5,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Đung đưa khuỷu tay ra sau và ra trước để lấy đà",
            "Ưỡn người ra sau khi nâng tạ nặng gây áp lực lên lưng dưới",
        ],
    },
    {
        "key": "hammer curls",
        "name_vi": "Cuốn tạ đơn búa (Hammer Curl)",
        "target_muscle": "Biceps",
        "secondary_muscle": [],
        "met_value": 4.0,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Xoay cổ tay trong lúc nâng thay vì giữ lòng bàn tay đối diện nhau",
            "Cùi chỏ không giữ cố định bên hông",
        ],
    },
    {
        "key": "incline dumbbell curl",
        "name_vi": "Cuốn tạ đơn trên ghế dốc (Incline Dumbbell Curl)",
        "target_muscle": "Biceps",
        "secondary_muscle": [],
        "met_value": 4.0,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Đưa khuỷu tay về phía trước làm mất độ căng của đầu dài bắp tay",
            "Nhấc lưng khỏi đệm ghế tựa",
        ],
    },
    {
        "key": "concentration curls",
        "name_vi": "Cuốn tạ đơn tập trung một tay (Concentration Curl)",
        "target_muscle": "Biceps",
        "secondary_muscle": [],
        "met_value": 3.5,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Tì khuỷu tay lên đỉnh đùi thay vì áp mặt sau cánh tay vào đùi trong",
            "Dùng vai nhấc tạ",
        ],
    },
    {
        "key": "preacher curl",
        "name_vi": "Cuốn bắp tay ghế dốc Preacher (Preacher Curl)",
        "target_muscle": "Biceps",
        "secondary_muscle": [],
        "met_value": 4.5,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Khóa khớp khuỷu tay quá gắt ở đáy chuyển động gây căng đứt gân cơ",
            "Nhấc nách khỏi đệm dốc để tạo lực kéo",
        ],
    },

    # ================= 6. TRICEPS - TAY SAU (5 bài thực thụ) =================
    {
        "key": "triceps pushdown",
        "name_vi": "Kéo cáp tay sau (Triceps Pushdown)",
        "target_muscle": "Triceps",
        "secondary_muscle": [],
        "met_value": 4.0,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Bè cùi chỏ ra hai bên thay vì kẹp chặt sát sườn",
            "Dùng trọng lượng cơ thể đè lên thanh đòn",
        ],
    },
    {
        "key": "dips - triceps version",
        "name_vi": "Chống xà kép tay sau (Triceps Dips)",
        "target_muscle": "Triceps",
        "secondary_muscle": ["Chest", "Shoulders"],
        "met_value": 6.0,
        "intensity_level": "Vigorous",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Nghiêng người về phía trước quá nhiều biến thành bài tập ngực",
            "Xuống quá sâu gây đau khớp vai",
        ],
    },
    {
        "key": "close-grip barbell bench press",
        "name_vi": "Đẩy ngực tay hẹp tạ đòn (Close-Grip Bench Press)",
        "target_muscle": "Triceps",
        "secondary_muscle": ["Chest", "Shoulders"],
        "met_value": 6.0,
        "intensity_level": "Vigorous",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Cầm tay quá sát nhau (<15cm) gây chèn ép cổ tay",
            "Bè khuỷu tay vuông góc với thân người",
        ],
    },
    {
        "key": "lying triceps press",
        "name_vi": "Nằm duỗi tạ đòn tay sau (Skull Crusher)",
        "target_muscle": "Triceps",
        "secondary_muscle": [],
        "met_value": 4.5,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Di chuyển toàn bộ cánh tay thay vì chỉ xoay quanh khớp khuỷu",
            "Bè cùi chỏ ra ngoài khi hạ tạ",
        ],
    },
    {
        "key": "bench dips",
        "name_vi": "Chống đẩy tay sau với ghế (Bench Dips)",
        "target_muscle": "Triceps",
        "secondary_muscle": ["Shoulders", "Chest"],
        "met_value": 4.0,
        "intensity_level": "Moderate",
        "banned_for": ["shoulder_impingement"],
        "clinical_reasons": "Góc duỗi khớp vai ra sau quá mức chịu tải trọng cơ thể có thể gây căng bao khớp vai trước.",
        "common_mistakes": [
            "Đưa mông cách quá xa mép ghế làm quá tải khớp vai",
            "Hạ người quá sâu vượt quá góc 90 độ của khuỷu tay",
        ],
    },

    # ================= 7. QUADRICEPS - ĐÙI TRƯỚC (6 bài thực thụ) =================
    {
        "key": "barbell full squat",
        "name_vi": "Gánh tạ đòn Squat (Barbell Full Squat)",
        "target_muscle": "Quadriceps",
        "secondary_muscle": ["Glutes", "Hamstrings", "Calves"],
        "met_value": 6.0,
        "intensity_level": "Vigorous",
        "banned_for": ["knee_osteoarthritis", "meniscus_tear", "herniated_disc"],
        "clinical_reasons": "Tạo tải trọng nén cực đại lên sụn chêm, gân bánh chè và các đốt sống thắt lưng.",
        "common_mistakes": [
            "Sụp đầu gối vào trong (Knee Valgus) khi đạp tạ lên",
            "Nhấc gót chân khỏi sàn khi xuống sâu",
            "Cong tròn lưng dưới ở đáy chuyển động (Butt Wink)",
        ],
    },
    {
        "key": "front barbell squat",
        "name_vi": "Gánh tạ đòn trước (Front Squat)",
        "target_muscle": "Quadriceps",
        "secondary_muscle": ["Glutes", "Abs"],
        "met_value": 6.0,
        "intensity_level": "Vigorous",
        "banned_for": ["knee_osteoarthritis", "wrist_pain"],
        "clinical_reasons": "Dồn trọng tâm hoàn toàn vào mặt trước đầu gối và yêu cầu gập cổ tay chịu lực lớn.",
        "common_mistakes": [
            "Hạ cùi chỏ xuống khiến thanh đòn bị tuột khỏi vai",
            "Nghiêng người về phía trước thay vì giữ lưng thẳng",
        ],
    },
    {
        "key": "leg press",
        "name_vi": "Đạp đùi trên máy (Leg Press)",
        "target_muscle": "Quadriceps",
        "secondary_muscle": ["Glutes", "Hamstrings"],
        "met_value": 5.5,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Khóa thẳng khớp gối ở đỉnh chuyển động gây áp lực cực lớn lên khớp gối",
            "Nhấc mông và xương cụt khỏi đệm lưng khi hạ bàn đạp xuống sâu",
        ],
    },
    {
        "key": "dumbbell lunges",
        "name_vi": "Bước chùng chân tạ đơn (Dumbbell Lunges)",
        "target_muscle": "Quadriceps",
        "secondary_muscle": ["Glutes", "Hamstrings"],
        "met_value": 5.0,
        "intensity_level": "Moderate",
        "banned_for": ["knee_osteoarthritis"],
        "clinical_reasons": "Tạo lực lệch tâm và tải trọng một bên gối lớn khi bước chân về trước.",
        "common_mistakes": [
            "Đầu gối chân trước lao quá xa vượt ngón chân",
            "Thân người đổ quá nhiều về trước làm mất thăng bằng",
        ],
    },
    {
        "key": "rear leg raises",
        "name_vi": "Đá chân sau tư thế quỳ bò (Rear Leg Raises)",
        "target_muscle": "Quadriceps",
        "secondary_muscle": ["Glutes", "Hamstrings"],
        "met_value": 2.8,
        "intensity_level": "Light",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Võng lưng dưới khi đá chân lên cao",
            "Dùng đà lăng chân thay vì gồng siết kiểm soát chuyển động",
        ],
    },
    {
        "key": "leg extensions",
        "name_vi": "Đá đùi trước trên máy chuyên dụng (Leg Extensions)",
        "target_muscle": "Quadriceps",
        "secondary_muscle": [],
        "met_value": 4.5,
        "intensity_level": "Moderate",
        "banned_for": ["knee_osteoarthritis"],
        "clinical_reasons": "Tạo lực cắt (shear force) mở rộng khớp gối trực tiếp lên gân bánh chè và sụn khớp.",
        "common_mistakes": [
            "Đá giật tạ lên nhanh và để rơi tự do",
            "Chỉnh con lăn đệm sai vị trí (quá cao trên cẳng chân hoặc quá thấp dưới bàn chân)",
        ],
    },

    # ================= 8. HAMSTRINGS - ĐÙI SAU (6 bài thực thụ) =================
    {
        "key": "romanian deadlift",
        "name_vi": "Deadlift kiểu Romania (Romanian Deadlift - RDL)",
        "target_muscle": "Hamstrings",
        "secondary_muscle": ["Glutes", "Back"],
        "met_value": 6.0,
        "intensity_level": "Vigorous",
        "banned_for": ["lower_back_pain", "herniated_disc"],
        "clinical_reasons": "Căng tối đa cơ đùi sau đồng thời đòi hỏi nhóm cơ dựng sống giữ tải tĩnh lớn.",
        "common_mistakes": [
            "Gập đầu gối quá nhiều biến thành bài Squat",
            "Gù lưng khi đẩy hông ra sau",
            "Để tạ rơi ra xa cẳng chân",
        ],
    },
    {
        "key": "lying leg curls",
        "name_vi": "Nằm móc đùi sau trên máy (Lying Leg Curl)",
        "target_muscle": "Hamstrings",
        "secondary_muscle": [],
        "met_value": 4.5,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Nhấc hông khỏi đệm ghế khi cuộn tạ lên",
            "Hạ tạ quá nhanh làm mất thời gian chịu áp lực của cơ bắp",
        ],
    },
    {
        "key": "seated leg curl",
        "name_vi": "Ngồi móc đùi sau trên máy (Seated Leg Curl)",
        "target_muscle": "Hamstrings",
        "secondary_muscle": [],
        "met_value": 4.5,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Không khóa đệm đùi sát vào chân khiến người bị nhấc lên khi co cơ",
            "Gồng cứng cổ và vai thay vì tập trung vào đùi sau",
        ],
    },
    {
        "key": "good morning",
        "name_vi": "Gập người gánh tạ đòn (Good Morning)",
        "target_muscle": "Hamstrings",
        "secondary_muscle": ["Glutes", "Back"],
        "met_value": 5.0,
        "intensity_level": "Moderate",
        "banned_for": ["lower_back_pain", "herniated_disc"],
        "clinical_reasons": "Cánh tay đòn dài đặt thanh tạ trên vai tạo mô-men uốn cực lớn tại đốt sống thắt lưng.",
        "common_mistakes": [
            "Gù lưng khi gập thân người xuống",
            "Xuống quá sâu vượt quá biên độ căng của cơ đùi sau",
        ],
    },
    {
        "key": "clean deadlift",
        "name_vi": "Deadlift cử tạ (Clean Deadlift)",
        "target_muscle": "Hamstrings",
        "secondary_muscle": ["Glutes", "Quadriceps", "Back"],
        "met_value": 6.0,
        "intensity_level": "Vigorous",
        "banned_for": ["lower_back_pain", "herniated_disc"],
        "clinical_reasons": "Đòi hỏi lực bộc phát và áp lực tải trọng nén cao lên cột sống.",
        "common_mistakes": [
            "Nhấc mông quá nhanh trước khi ngực kịp nâng lên",
            "Kéo tạ bằng tay thay vì dùng lực đạp sàn của chân",
        ],
    },
    {
        "key": "sumo deadlift",
        "name_vi": "Kéo tạ đòn thế Sumo (Sumo Deadlift)",
        "target_muscle": "Hamstrings",
        "secondary_muscle": ["Glutes", "Quadriceps", "Back"],
        "met_value": 6.0,
        "intensity_level": "Vigorous",
        "banned_for": ["groin_strain", "herniated_disc"],
        "clinical_reasons": "Thế đứng rộng tạo áp lực kéo căng lớn lên các nhóm cơ khép đùi và khớp háng.",
        "common_mistakes": [
            "Để đầu gối sụp vào trong khi đạp tạ lên",
            "Không mở rộng khớp háng dẫn đến cong lưng dưới",
        ],
    },

    # ================= 9. GLUTES - MÔNG (6 bài thực thụ) =================
    {
        "key": "barbell hip thrust",
        "name_vi": "Đẩy hông tạ đòn (Barbell Hip Thrust)",
        "target_muscle": "Glutes",
        "secondary_muscle": ["Hamstrings"],
        "met_value": 6.0,
        "intensity_level": "Vigorous",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Ưỡn lưng dưới ở đỉnh thay vì cuộn xương chậu siết mông (Posterior Pelvic Tilt)",
            "Đặt chân quá xa làm ăn vào đùi sau, hoặc quá gần làm mỏi đùi trước",
        ],
    },
    {
        "key": "barbell glute bridge",
        "name_vi": "Cầu mông tạ đòn trên sàn (Barbell Glute Bridge)",
        "target_muscle": "Glutes",
        "secondary_muscle": ["Hamstrings"],
        "met_value": 5.0,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Nhấc gót chân lên khỏi mặt sàn",
            "Không giữ siết cơ mông 1 giây ở đỉnh động tác",
        ],
    },
    {
        "key": "glute kickback",
        "name_vi": "Đá mông sau dây cáp (Cable Glute Kickback)",
        "target_muscle": "Glutes",
        "secondary_muscle": ["Hamstrings"],
        "met_value": 4.0,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Võng lưng dưới khi đá chân ra sau",
            "Dùng quán tính đung đưa người thay vì dùng cơ mông",
        ],
    },
    {
        "key": "butt lift (bridge)",
        "name_vi": "Cầu mông tay không (Bodyweight Glute Bridge)",
        "target_muscle": "Glutes",
        "secondary_muscle": ["Hamstrings"],
        "met_value": 2.8,
        "intensity_level": "Light",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Dùng cơ lưng dưới đẩy hông lên thay vì gồng mông",
            "Gót chân đặt quá xa mông",
        ],
    },
    {
        "key": "single leg glute bridge",
        "name_vi": "Cầu mông một chân (Single Leg Glute Bridge)",
        "target_muscle": "Glutes",
        "secondary_muscle": ["Hamstrings"],
        "met_value": 2.8,
        "intensity_level": "Light",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Xương chậu bị lệch sang một bên khi nâng",
            "Không siết chặt mông chân trụ",
        ],
    },
    {
        "key": "dumbbell step ups",
        "name_vi": "Bước lên bục cầm tạ đơn (Dumbbell Step Ups)",
        "target_muscle": "Glutes",
        "secondary_muscle": ["Quadriceps", "Hamstrings"],
        "met_value": 5.0,
        "intensity_level": "Moderate",
        "banned_for": ["knee_instability"],
        "clinical_reasons": "Đòi hỏi khả năng thăng bằng đơn chân và kiểm soát độ lệch trục xương bánh chè khi bước lên cao.",
        "common_mistakes": [
            "Dùng chân dưới bật nhảy thay vì dùng lực cơ mông đùi chân trên bục",
            "Để đầu gối chân trước xoay vẹo vào trong",
        ],
    },

    # ================= 10. CALVES - BẮP CHÂN (6 bài thực thụ) =================
    {
        "key": "standing calf raises",
        "name_vi": "Nhón bắp chân đứng (Standing Calf Raise)",
        "target_muscle": "Calves",
        "secondary_muscle": [],
        "met_value": 2.8,
        "intensity_level": "Light",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Nhấp nhả nhanh không kéo căng tối đa ở đáy",
            "Gập gối khi nhón chân làm giảm kích hoạt cơ bụng chân",
        ],
    },
    {
        "key": "seated calf raise",
        "name_vi": "Nhón bắp chân ngồi máy (Seated Calf Raise)",
        "target_muscle": "Calves",
        "secondary_muscle": [],
        "met_value": 3.5,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Nhảy nhót lò xo thay vì chuyển động chậm rãi kiểm soát",
            "Không hạ gót chân xuống sâu hết biên độ",
        ],
    },
    {
        "key": "calf press on the leg press machine",
        "name_vi": "Nhón bắp chân trên máy đạp đùi (Leg Press Calf Press)",
        "target_muscle": "Calves",
        "secondary_muscle": [],
        "met_value": 4.5,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Để mũi chân trượt khỏi bàn đạp gây nguy hiểm",
            "Khóa thẳng khớp gối hoàn toàn khi nhón chân",
        ],
    },
    {
        "key": "smith machine calf raise",
        "name_vi": "Nhón bắp chân trên máy Smith (Smith Machine Calf Raise)",
        "target_muscle": "Calves",
        "secondary_muscle": [],
        "met_value": 4.5,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Không đứng trên bục kê để có biên độ duỗi sâu",
            "Cong lưng khi gánh thanh đòn",
        ],
    },
    {
        "key": "rocking standing calf raise",
        "name_vi": "Nhón bắp chân bập bênh (Rocking Standing Calf Raise)",
        "target_muscle": "Calves",
        "secondary_muscle": [],
        "met_value": 2.6,
        "intensity_level": "Light",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Mất thăng bằng ngả nghiêng thân người",
            "Thực hiện với nhịp độ quá nhanh",
        ],
    },
    {
        "key": "standing dumbbell calf raise",
        "name_vi": "Nhón bắp chân đứng cầm tạ đơn (Standing Dumbbell Calf Raise)",
        "target_muscle": "Calves",
        "secondary_muscle": [],
        "met_value": 3.5,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Nhún nhảy liên tục không dừng ở điểm căng tối đa",
            "Hơi gập gối làm giảm áp lực dồn vào cơ bắp chân",
        ],
    },

    # ================= 11. ABS - BỤNG & CORE (8 bài thực thụ) =================
    {
        "key": "plank",
        "name_vi": "Tư thế Plank gồng bụng (Plank)",
        "target_muscle": "Abs",
        "secondary_muscle": ["Shoulders", "Glutes"],
        "met_value": 3.5,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Võng lưng dưới gây đau cột sống thắt lưng",
            "Chổng mông lên quá cao làm mất lực gồng cơ bụng",
            "Ngửa cổ nhìn về phía trước thay vì nhìn xuống thảm",
        ],
    },
    {
        "key": "crunches",
        "name_vi": "Gập bụng tiêu chuẩn (Crunches)",
        "target_muscle": "Abs",
        "secondary_muscle": [],
        "met_value": 3.8,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Dùng hai tay kéo mạnh gáy về phía trước gây đau cơ cổ",
            "Nâng toàn bộ lưng dưới khỏi sàn biến thành động tác Sit-up",
        ],
    },
    {
        "key": "russian twist",
        "name_vi": "Vặn người kiểu Nga (Russian Twist)",
        "target_muscle": "Abs",
        "secondary_muscle": [],
        "met_value": 4.0,
        "intensity_level": "Moderate",
        "banned_for": ["herniated_disc"],
        "clinical_reasons": "Chuyển động vặn xoắn cột sống thắt lưng có tải trọng làm tăng nguy cơ tổn thương vòng sợi đĩa đệm.",
        "common_mistakes": [
            "Chỉ di chuyển cánh tay qua lại mà không xoay vùng ngực và vai",
            "Gù lưng tròn khi ngả người ra sau",
        ],
    },
    {
        "key": "hanging leg raise",
        "name_vi": "Treo người nâng chân xà đơn (Hanging Leg Raise)",
        "target_muscle": "Abs",
        "secondary_muscle": ["Forearms"],
        "met_value": 6.0,
        "intensity_level": "Vigorous",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Lăng người lấy đà thay vì dùng cơ bụng dưới cuộn xương chậu",
            "Thả rơi chân quá nhanh khi hạ xuống",
        ],
    },
    {
        "key": "ab roller",
        "name_vi": "Lăn bánh xe gập bụng (Ab Wheel Rollout)",
        "target_muscle": "Abs",
        "secondary_muscle": ["Shoulders", "Back"],
        "met_value": 6.0,
        "intensity_level": "Vigorous",
        "banned_for": ["lower_back_pain", "herniated_disc"],
        "clinical_reasons": "Đòi hỏi sức mạnh cơ lõi cực lớn để chống lại lực võng lưng; dễ gây quá tải đốt sống thắt lưng.",
        "common_mistakes": [
            "Võng lưng dưới khi đẩy bánh xe ra xa",
            "Dùng khớp hông kéo về thay vì gồng cuộn cơ bụng",
        ],
    },
    {
        "key": "3/4 sit-up",
        "name_vi": "Gập bụng 3/4 kiểm soát (3/4 Sit-up)",
        "target_muscle": "Abs",
        "secondary_muscle": [],
        "met_value": 2.8,
        "intensity_level": "Light",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Dùng cổ giật người lên",
            "Không hóp chặt rốn gồng bụng khi nâng thân người",
        ],
    },
    {
        "key": "air bike",
        "name_vi": "Đạp xe gập bụng liên sườn (Air Bike / Bicycle Crunch)",
        "target_muscle": "Abs",
        "secondary_muscle": [],
        "met_value": 4.5,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Kéo mạnh cổ về phía trước gây đau cơ gáy",
            "Chỉ vặn cùi chỏ thay vì xoay chuyển toàn bộ vùng vai và ngực",
        ],
    },
    {
        "key": "cable crunch",
        "name_vi": "Gập bụng quỳ dây cáp (Cable Crunch)",
        "target_muscle": "Abs",
        "secondary_muscle": [],
        "met_value": 4.5,
        "intensity_level": "Moderate",
        "banned_for": ["lower_back_pain"],
        "clinical_reasons": "Gập cột sống dưới tải trọng đối kháng liên tục cần kiểm soát tốt để tránh chèn ép đĩa đệm.",
        "common_mistakes": [
            "Gập từ khớp hông ngồi lùi mông ra sau thay vì cuộn tròn cơ bụng",
            "Dùng cánh tay kéo dây thừng xuống thay vì dùng lực co thắt cơ bụng",
        ],
    },
]


def build_65_exercises() -> list[dict[str, Any]]:
    """Đọc raw exercises.json và trích xuất đúng 65 bài tập thực thụ chuẩn hóa phủ đều 11 nhóm cơ."""
    if not RAW_EXERCISES_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {RAW_EXERCISES_PATH}")

    with open(RAW_EXERCISES_PATH, mode="r", encoding="utf-8") as f:
        raw_list = json.load(f)

    raw_by_key = {d.get("name", "").strip().lower(): d for d in raw_list}

    processed_exercises: list[dict[str, Any]] = []

    for idx, defn in enumerate(EXERCISE_DEFINITIONS, start=1):
        key = defn["key"]
        raw = raw_by_key.get(key)
        if not raw:
            raise KeyError(f"Không tìm thấy bài tập '{key}' trong exercises.json")

        category = str(raw.get("category") or "strength").strip().title()
        equipment = (raw.get("equipment") or "other").strip().lower()
        instructions = [str(step).strip() for step in raw.get("instructions", []) if str(step).strip()]

        images = raw.get("images", [])
        image_url = f"{CDN_BASE}/{images[0]}" if images else None

        desc = (
            f"Bài tập {defn['name_vi']} nhắm vào nhóm cơ {defn['target_muscle']}, "
            f"sử dụng thiết bị {equipment} với mức vận động MET {defn['met_value']}."
        )

        record = {
            "id": idx,
            "category": category,
            "name_vi": defn["name_vi"],
            "name_en": raw.get("name", "").strip(),
            "met_value": float(defn["met_value"]),
            "intensity_level": defn["intensity_level"],
            "description": desc,
            "equipment": equipment,
            "instructions": instructions,
            "common_mistakes": defn["common_mistakes"],
            "image": image_url,
            "video_url": None,
            "target_muscle": defn["target_muscle"],
            "secondary_muscle": defn["secondary_muscle"],
            "banned_for": defn["banned_for"],
            "clinical_reasons": defn["clinical_reasons"],
            "source": "free-exercise-db",
        }
        processed_exercises.append(record)

    PROCESSED_65_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PROCESSED_65_PATH, mode="w", encoding="utf-8") as out:
        json.dump(processed_exercises, out, ensure_ascii=False, indent=2)

    alt_path = BACKEND_DIR / "data" / "processed" / "exercises.json"
    with open(alt_path, mode="w", encoding="utf-8") as out:
        json.dump(processed_exercises, out, ensure_ascii=False, indent=2)

    return processed_exercises


if __name__ == "__main__":
    items = build_65_exercises()
    print(f"[+] Đã trích xuất và chuẩn hóa thành công {len(items)} bài tập thực thụ vào: {PROCESSED_65_PATH}")
