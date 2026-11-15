"""
Tạo bộ dữ liệu 50 bài tập chuẩn hóa từ backend/data/raw/exercises.json
khớp hoàn toàn với schema ORM `Exercise`:
id, category, name_vi, name_en, met_value, intensity_level, description,
equipment, instructions, common_mistakes, image, video_url,
target_muscle, secondary_muscle, banned_for, clinical_reasons, source

Phủ đều toàn bộ 11 nhóm cơ chính trong ứng dụng:
- Chest (5 bài)
- Back (5 bài)
- Shoulders (4 bài)
- Rear Delts (2 bài)
- Biceps (4 bài)
- Triceps (4 bài)
- Quadriceps (5 bài)
- Hamstrings (5 bài)
- Glutes (5 bài)
- Calves (5 bài)
- Abs (6 bài)
Tổng cộng: ĐÚNG 50 BÀI TẬP.
"""

import json
from pathlib import Path
from typing import Any

from app.config import BACKEND_DIR

RAW_EXERCISES_PATH = BACKEND_DIR / "data" / "raw" / "exercises.json"
PROCESSED_50_PATH = BACKEND_DIR / "data" / "processed" / "exercises_50.json"
CDN_BASE = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises"

EXERCISE_DEFINITIONS: list[dict[str, Any]] = [
    # ================= 1. CHEST - NGỰC (5 bài) =================
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

    # ================= 2. BACK - LƯNG / XÔ (5 bài) =================
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
            "Đung đưa người lấy đà thay vì kéo bằng cơ xô",
            "Không kéo cằm vượt quá thanh xà hoặc thả rơi tự do khi xuống",
        ],
    },
    {
        "key": "barbell deadlift",
        "name_vi": "Kéo tạ đòn (Barbell Deadlift)",
        "target_muscle": "Back",
        "secondary_muscle": ["Glutes", "Hamstrings", "Quadriceps"],
        "met_value": 6.5,
        "intensity_level": "Vigorous",
        "banned_for": ["hypertension"],
        "clinical_reasons": "Phản xạ nín thở Valsalva khi nâng tạ nặng từ sàn làm tăng đột ngột huyết áp và áp lực nội sọ",
        "common_mistakes": [
            "Gù cột sống thắt lưng khi nhấc tạ khỏi mặt sàn",
            "Để thanh đòn quá xa cẳng chân làm tăng cánh tay đòn lên lưng dưới",
            "Ngửa cổ nhìn lên trần nhà thay vì giữ cổ thẳng tự nhiên",
        ],
    },
    {
        "key": "bent over barbell row",
        "name_vi": "Gập người chèo tạ đòn (Barbell Row)",
        "target_muscle": "Back",
        "secondary_muscle": ["Biceps", "Shoulders"],
        "met_value": 5.5,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Đứng quá thẳng người thay vì gập hông cố định góc 45 độ",
            "Dùng đà giật người lên thay vì tập trung ép hai xương bả vai",
        ],
    },
    {
        "key": "wide-grip lat pulldown",
        "name_vi": "Kéo xô máy tay rộng (Lat Pulldown)",
        "target_muscle": "Back",
        "secondary_muscle": ["Biceps", "Shoulders"],
        "met_value": 5.0,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Ngả người ra sau quá nhiều biến thành bài chèo lưng",
            "Kéo thanh đòn ra sau gáy gây chấn thương các đốt sống cổ",
        ],
    },
    {
        "key": "seated cable rows",
        "name_vi": "Kéo cáp ngồi chèo xô (Seated Cable Row)",
        "target_muscle": "Back",
        "secondary_muscle": ["Biceps"],
        "met_value": 5.0,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Đung đưa thân mình trước sau theo nhịp kéo cáp",
            "Co vai lên tai thay vì kéo xương bả vai xuống dưới và ra sau",
        ],
    },

    # ================= 3. SHOULDERS - VAI (4 bài) =================
    {
        "key": "standing military press",
        "name_vi": "Đẩy vai qua đầu tạ đòn (Overhead Press)",
        "target_muscle": "Shoulders",
        "secondary_muscle": ["Triceps"],
        "met_value": 6.0,
        "intensity_level": "Vigorous",
        "banned_for": ["hypertension"],
        "clinical_reasons": "Động tác đẩy tạ qua đầu kết hợp nín thở gồng cơ lồng ngực làm tăng áp lực mạch máu hệ thống",
        "common_mistakes": [
            "Ưỡn lưng dưới ra sau để mượn lực đẩy của cơ ngực",
            "Không siết chặt cơ mông và cơ bụng để khóa cứng khung xương chậu",
        ],
    },
    {
        "key": "side lateral raise",
        "name_vi": "Dang tạ đơn sang hai bên (Lateral Raise)",
        "target_muscle": "Shoulders",
        "secondary_muscle": [],
        "met_value": 4.0,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Nâng tạ cao hơn ngang vai gây chèn ép khoang dưới mỏm cùng vai",
            "Nhún chân vung người để lấy đà nâng tạ",
        ],
    },
    {
        "key": "front dumbbell raise",
        "name_vi": "Nâng tạ đơn phía trước (Front Raise)",
        "target_muscle": "Shoulders",
        "secondary_muscle": ["Chest"],
        "met_value": 4.0,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Đung đưa thân người ra sau khi nâng tạ",
            "Nắm tạ quá chặt phân tán kích thích khỏi cơ vai trước",
        ],
    },
    {
        "key": "seated dumbbell press",
        "name_vi": "Ngồi đẩy vai tạ đơn (Seated Dumbbell Press)",
        "target_muscle": "Shoulders",
        "secondary_muscle": ["Triceps"],
        "met_value": 5.0,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Để cùi chỏ bè ngang 90 độ gây kẹt bao khớp vai; nên hướng nhẹ về trước góc 60 độ",
            "Hạ tạ chưa đủ sâu qua tầm cằm",
        ],
    },

    # ================= 4. REAR DELTS - VAI SAU (2 bài) =================
    {
        "key": "reverse flyes",
        "name_vi": "Dang tạ vai sau (Reverse Flyes)",
        "target_muscle": "Rear Delts",
        "secondary_muscle": ["Back", "Shoulders"],
        "met_value": 4.0,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Dùng cơ cầu vai co rúm thay vì tập trung mở rộng cánh tay",
            "Cổ gập ngửa sai trục tự nhiên",
        ],
    },
    {
        "key": "face pull",
        "name_vi": "Kéo cáp mặt tập vai sau (Face Pull)",
        "target_muscle": "Rear Delts",
        "secondary_muscle": ["Back", "Shoulders"],
        "met_value": 4.5,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Hạ cùi chỏ thấp hơn cổ tay làm mất lực tác động vào cơ vai sau",
            "Ưỡn ngực giật người ra sau",
        ],
    },

    # ================= 5. BICEPS - TAY TRƯỚC (4 bài) =================
    {
        "key": "barbell curl",
        "name_vi": "Cuốn tay trước tạ đòn (Barbell Curl)",
        "target_muscle": "Biceps",
        "secondary_muscle": ["Forearms"],
        "met_value": 4.5,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Vung khuỷu tay ra trước khi cuộn tạ",
            "Võng lưng dưới đung đưa lấy đà nâng tạ nặng",
        ],
    },
    {
        "key": "hammer curls",
        "name_vi": "Cuốn tạ đơn tay búa (Hammer Curl)",
        "target_muscle": "Biceps",
        "secondary_muscle": ["Forearms"],
        "met_value": 4.0,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Xoay cổ tay khi nâng làm mất trọng tâm tác động vào cơ cánh tay (brachialis)",
        ],
    },
    {
        "key": "incline dumbbell curl",
        "name_vi": "Ngồi ghế dốc cuốn tạ đơn (Incline Dumbbell Curl)",
        "target_muscle": "Biceps",
        "secondary_muscle": ["Forearms"],
        "met_value": 4.0,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Đưa khuỷu tay về phía trước làm mất biên độ kéo dãn tối đa của cơ nhị đầu",
        ],
    },
    {
        "key": "concentration curls",
        "name_vi": "Cuốn tạ tập trung (Concentration Curl)",
        "target_muscle": "Biceps",
        "secondary_muscle": [],
        "met_value": 3.8,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Không tì cố định khuỷu tay vào mặt trong đùi",
            "Hạ tạ rơi tự do không ghìm kiểm soát",
        ],
    },

    # ================= 6. TRICEPS - TAY SAU (4 bài) =================
    {
        "key": "triceps pushdown",
        "name_vi": "Kéo cáp tay sau (Triceps Pushdown)",
        "target_muscle": "Triceps",
        "secondary_muscle": [],
        "met_value": 4.5,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Bè khuỷu tay sang hai bên thay vì kẹp sát thân mình",
            "Đứng quá xa máy cáp làm đổi góc tác động",
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
            "Nghiêng người về phía trước thay vì giữ lưng thẳng đứng để cô lập tay sau",
        ],
    },
    {
        "key": "close-grip barbell bench press",
        "name_vi": "Đẩy ngực tạ đòn tay hẹp (Close-Grip Bench Press)",
        "target_muscle": "Triceps",
        "secondary_muscle": ["Chest", "Shoulders"],
        "met_value": 5.5,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Cầm tay quá hẹp (<15cm) gây vặn vẹo áp lực lên cổ tay",
        ],
    },
    {
        "key": "lying triceps press",
        "name_vi": "Nằm duỗi tạ sau đầu (Skullcrusher)",
        "target_muscle": "Triceps",
        "secondary_muscle": [],
        "met_value": 4.5,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Di chuyển cánh tay thay vì giữ khuỷu tay cố định vuông góc với sàn",
        ],
    },

    # ================= 7. QUADRICEPS - ĐÙI TRƯỚC (5 bài) =================
    {
        "key": "barbell full squat",
        "name_vi": "Gánh tạ đòn sâu (Back Squat)",
        "target_muscle": "Quadriceps",
        "secondary_muscle": ["Glutes", "Hamstrings", "Calves"],
        "met_value": 6.5,
        "intensity_level": "Vigorous",
        "banned_for": ["knee_osteoarthritis", "hypertension"],
        "clinical_reasons": "Gập gối sâu tạo áp lực nén đỉnh điểm lên sụn chêm và xương bánh chè; gồng bụng nén tạ nặng làm huyết áp tăng vọt",
        "common_mistakes": [
            "Đầu gối chụm vào trong (knee valgus) khi nâng người lên",
            "Nhấc gót chân khỏi sàn",
            "Gù thắt lưng ở điểm sâu nhất của động tác",
        ],
    },
    {
        "key": "front barbell squat",
        "name_vi": "Gánh tạ đòn trước (Front Squat)",
        "target_muscle": "Quadriceps",
        "secondary_muscle": ["Glutes", "Abs"],
        "met_value": 6.5,
        "intensity_level": "Vigorous",
        "banned_for": ["knee_osteoarthritis", "hypertension"],
        "clinical_reasons": "Lực nén lớn lên khớp gối và nín thở gồng bụng dưới tải trọng lớn",
        "common_mistakes": [
            "Hạ cùi chỏ xuống làm thanh tạ trượt khỏi vai",
            "Gập người quá nhiều về phía trước",
        ],
    },
    {
        "key": "leg press",
        "name_vi": "Đạp đùi bằng máy (Leg Press)",
        "target_muscle": "Quadriceps",
        "secondary_muscle": ["Glutes", "Hamstrings"],
        "met_value": 5.5,
        "intensity_level": "Moderate",
        "banned_for": ["knee_osteoarthritis"],
        "clinical_reasons": "Gập gối góc nhọn dưới tải trọng lớn tạo áp lực nén mạnh lên bao khớp gối",
        "common_mistakes": [
            "Khóa chết khớp gối ở điểm duỗi tối đa",
            "Nhấc mông và xương cụt khỏi đệm tựa khi hạ bàn đạp xuống sâu",
        ],
    },
    {
        "key": "dumbbell lunges",
        "name_vi": "Chùng chân bước tới tạ đơn (Dumbbell Lunge)",
        "target_muscle": "Quadriceps",
        "secondary_muscle": ["Glutes", "Hamstrings"],
        "met_value": 5.5,
        "intensity_level": "Moderate",
        "banned_for": ["knee_osteoarthritis"],
        "clinical_reasons": "Chịu tải đơn chân với lực cắt ngang lớn tác động trực tiếp lên dây chằng chéo và sụn gối",
        "common_mistakes": [
            "Đầu gối chân trước vượt quá xa đầu ngón chân",
            "Thân mình bị nghiêng lệch vẹo sang một bên",
        ],
    },
    {
        "key": "rear leg raises",
        "name_vi": "Nâng chân duỗi thẳng trên thảm (Rear Leg Raise - An toàn khớp gối)",
        "target_muscle": "Quadriceps",
        "secondary_muscle": ["Glutes"],
        "met_value": 2.8,
        "intensity_level": "Light",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Võng lưng dưới khi nâng chân",
            "Không gồng siết cơ đùi và cơ mông ở đỉnh chuyển động",
        ],
    },

    # ================= 8. HAMSTRINGS - ĐÙI SAU (5 bài) =================
    {
        "key": "romanian deadlift",
        "name_vi": "Deadlift kiểu Rumani (Romanian Deadlift - RDL)",
        "target_muscle": "Hamstrings",
        "secondary_muscle": ["Glutes", "Back"],
        "met_value": 5.5,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Trùng gối quá nhiều biến thành bài squat",
            "Cong lưng dưới khi hạ thanh đòn xuống dưới gối",
        ],
    },
    {
        "key": "lying leg curls",
        "name_vi": "Nằm cuốn đùi sau máy (Lying Leg Curl)",
        "target_muscle": "Hamstrings",
        "secondary_muscle": ["Calves"],
        "met_value": 4.0,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Nhấc hông khỏi đệm khi cuộn chân",
            "Để tạ rơi nhanh không ghìm lực",
        ],
    },
    {
        "key": "seated leg curl",
        "name_vi": "Ngồi cuốn đùi sau máy (Seated Leg Curl)",
        "target_muscle": "Hamstrings",
        "secondary_muscle": ["Calves"],
        "met_value": 4.0,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Không khóa chặt đệm giữ đùi khiến cơ thể bị trượt về trước",
        ],
    },
    {
        "key": "good morning",
        "name_vi": "Gập người chào buổi sáng (Good Morning)",
        "target_muscle": "Hamstrings",
        "secondary_muscle": ["Glutes", "Back"],
        "met_value": 5.0,
        "intensity_level": "Moderate",
        "banned_for": ["hypertension"],
        "clinical_reasons": "Tư thế dốc đầu xuống kết hợp gánh tạ đòn trên vai tạo áp lực tĩnh mạch lớn vùng đầu",
        "common_mistakes": [
            "Cong cột sống thắt lưng khi gập hông",
            "Chọn mức tạ quá nặng gây quá tải cơ dựng sống",
        ],
    },
    {
        "key": "clean deadlift",
        "name_vi": "Kéo tạ Clean Deadlift (Đùi sau & Lưng)",
        "target_muscle": "Hamstrings",
        "secondary_muscle": ["Glutes", "Back", "Quadriceps"],
        "met_value": 6.0,
        "intensity_level": "Vigorous",
        "banned_for": ["hypertension"],
        "clinical_reasons": "Nâng tạ nặng từ sàn kèm phản xạ nín thở làm tăng huyết áp nhanh",
        "common_mistakes": [
            "Nhấc mông trước khi vai di chuyển",
            "Thanh đòn trôi xa cơ thể",
        ],
    },

    # ================= 9. GLUTES - MÔNG (5 bài) =================
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
            "Võng lưng dưới ở đỉnh thay vì cuộn xương chậu siết mông",
            "Đặt bàn chân quá xa hoặc quá gần thân người",
        ],
    },
    {
        "key": "barbell glute bridge",
        "name_vi": "Cầu mông tạ đòn nằm sàn (Barbell Glute Bridge)",
        "target_muscle": "Glutes",
        "secondary_muscle": ["Hamstrings"],
        "met_value": 5.0,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Đẩy bằng mũi chân thay vì đạp gót chân xuống sàn",
        ],
    },
    {
        "key": "glute kickback",
        "name_vi": "Đá chân sau tập mông (Glute Kickback)",
        "target_muscle": "Glutes",
        "secondary_muscle": ["Hamstrings"],
        "met_value": 3.8,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Võng cột sống lưng dưới để đá chân lên cao",
        ],
    },
    {
        "key": "butt lift (bridge)",
        "name_vi": "Cầu mông thể trọng (Bodyweight Glute Bridge)",
        "target_muscle": "Glutes",
        "secondary_muscle": ["Hamstrings", "Abs"],
        "met_value": 2.8,
        "intensity_level": "Light",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Không dừng lại siết chặt cơ mông 1-2 giây ở điểm cao nhất",
        ],
    },
    {
        "key": "single leg glute bridge",
        "name_vi": "Cầu mông đơn chân (Single Leg Glute Bridge)",
        "target_muscle": "Glutes",
        "secondary_muscle": ["Hamstrings"],
        "met_value": 4.0,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Hông bị nghiêng lệch sang bên chân đang nâng",
        ],
    },

    # ================= 10. CALVES - BẮP CHÂN (5 bài) =================
    {
        "key": "standing calf raises",
        "name_vi": "Nhón bắp chân đứng (Standing Calf Raise)",
        "target_muscle": "Calves",
        "secondary_muscle": [],
        "met_value": 4.0,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Nhấp nhả dùng quán tính gân gót thay vì kéo dãn và siết cơ bắp chuối",
            "Trùng gối khi nhón",
        ],
    },
    {
        "key": "seated calf raise",
        "name_vi": "Nhón bắp chân ngồi máy (Seated Calf Raise)",
        "target_muscle": "Calves",
        "secondary_muscle": [],
        "met_value": 2.8,
        "intensity_level": "Light",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Không hạ sâu gót chân để đạt độ căng tối đa của cơ dép (soleus)",
        ],
    },
    {
        "key": "calf press on the leg press machine",
        "name_vi": "Nhón bắp chân trên máy đạp đùi (Calf Press on Leg Press)",
        "target_muscle": "Calves",
        "secondary_muscle": [],
        "met_value": 4.5,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Khóa chết khớp gối gây rủi ro bật ngược khớp; cần giữ gối hơi chùng nhẹ",
        ],
    },
    {
        "key": "smith machine calf raise",
        "name_vi": "Nhón bắp chân với máy Smith (Smith Machine Calf Raise)",
        "target_muscle": "Calves",
        "secondary_muscle": [],
        "met_value": 4.0,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Gập thân về trước để giảm tải",
        ],
    },
    {
        "key": "rocking standing calf raise",
        "name_vi": "Nhón bắp chân bập bênh (Rocking Calf Raise)",
        "target_muscle": "Calves",
        "secondary_muscle": [],
        "met_value": 2.5,
        "intensity_level": "Light",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Mất thăng bằng ngã người",
        ],
    },

    # ================= 11. ABS - BỤNG (6 bài) =================
    {
        "key": "plank",
        "name_vi": "Plank giữ thân người (Plank)",
        "target_muscle": "Abs",
        "secondary_muscle": ["Shoulders", "Glutes"],
        "met_value": 3.8,
        "intensity_level": "Moderate",
        "banned_for": ["hypertension"],
        "clinical_reasons": "Co cơ tĩnh đẳng trường (isometric hold) kéo dài làm gia tăng sức cản mạch máu ngoại vi và huyết áp",
        "common_mistakes": [
            "Võng thắt lưng gây đau cột sống",
            "Đẩy mông lên quá cao",
            "Nín thở khi giữ tư thế",
        ],
    },
    {
        "key": "crunches",
        "name_vi": "Gập bụng cơ bản (Crunch)",
        "target_muscle": "Abs",
        "secondary_muscle": [],
        "met_value": 3.5,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Dùng tay kéo giật đốt sống cổ",
            "Nhấc toàn bộ lưng dưới khỏi sàn thay vì chỉ cuộn xương bả vai",
        ],
    },
    {
        "key": "russian twist",
        "name_vi": "Xoay người kiểu Nga (Russian Twist)",
        "target_muscle": "Abs",
        "secondary_muscle": [],
        "met_value": 4.0,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Chỉ vung tay qua lại thay vì xoay toàn bộ thân trên từ cơ liên sườn",
        ],
    },
    {
        "key": "hanging leg raise",
        "name_vi": "Treo người nâng chân gập bụng (Hanging Leg Raise)",
        "target_muscle": "Abs",
        "secondary_muscle": ["Forearms"],
        "met_value": 5.0,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Đung đưa lấy đà cơ thể",
            "Chỉ nâng đùi bằng cơ gấp hông mà không cuộn khung xương chậu",
        ],
    },
    {
        "key": "ab roller",
        "name_vi": "Lăn bánh xe tập bụng (Ab Roller Rollout)",
        "target_muscle": "Abs",
        "secondary_muscle": ["Shoulders", "Back"],
        "met_value": 5.5,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Võng lưng dưới khi vươn ra xa",
            "Dùng cơ xô kéo bánh xe về thay vì siết gập cơ bụng",
        ],
    },
    {
        "key": "3/4 sit-up",
        "name_vi": "Gập bụng 3/4 (3/4 Sit-up)",
        "target_muscle": "Abs",
        "secondary_muscle": [],
        "met_value": 3.8,
        "intensity_level": "Moderate",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Dùng cổ giật người lên",
            "Không hóp chặt rốn gồng bụng khi nâng thân người",
        ],
    },

    # ================= 12. CÁC BÀI TẬP CƯỜNG ĐỘ NHẸ (LIGHT / MOBILITY / STRETCHING) =================
    {
        "key": "behind head chest stretch",
        "name_vi": "Giãn ngực vòng tay sau đầu (Behind Head Chest Stretch)",
        "target_muscle": "Chest",
        "secondary_muscle": ["Shoulders"],
        "met_value": 2.3,
        "intensity_level": "Light",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Gập cổ về phía trước thay vì giữ thẳng lưng và cổ",
            "Kéo khuỷu tay quá giật cục gây chèn ép khớp vai",
        ],
    },
    {
        "key": "child's pose",
        "name_vi": "Tư thế em bé giãn lưng dưới (Child's Pose)",
        "target_muscle": "Back",
        "secondary_muscle": ["Glutes"],
        "met_value": 2.0,
        "intensity_level": "Light",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Không thả lỏng cơ vai và hông",
            "Nín thở khi giữ tư thế",
        ],
    },
    {
        "key": "cat stretch",
        "name_vi": "Tư thế con mèo giãn cột sống lưng (Cat Stretch)",
        "target_muscle": "Back",
        "secondary_muscle": ["Shoulders"],
        "met_value": 2.3,
        "intensity_level": "Light",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Chuyển động quá nhanh làm mất kiểm soát khớp đốt sống",
            "Không gập cằm về ngực khi uốn cong lưng",
        ],
    },
    {
        "key": "arm circles",
        "name_vi": "Xoay vòng khớp vai khởi động (Arm Circles)",
        "target_muscle": "Shoulders",
        "secondary_muscle": [],
        "met_value": 2.5,
        "intensity_level": "Light",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Xoay với biên độ quá nhanh và giật cục",
            "Nhún vai lên tai thay vì giữ vai hạ lỏng tự nhiên",
        ],
    },
    {
        "key": "shoulder stretch",
        "name_vi": "Giãn cơ vai bắt chéo tay (Shoulder Stretch)",
        "target_muscle": "Shoulders",
        "secondary_muscle": [],
        "met_value": 2.3,
        "intensity_level": "Light",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Nâng vai sát tai làm căng cứng cơ cổ",
            "Xoay vặn toàn thân theo hướng cánh tay",
        ],
    },
    {
        "key": "upper back stretch",
        "name_vi": "Giãn cơ vai sau và lưng trên (Upper Back Stretch)",
        "target_muscle": "Rear Delts",
        "secondary_muscle": ["Back"],
        "met_value": 2.3,
        "intensity_level": "Light",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Gù lưng dưới thay vì tập trung mở rộng bả vai",
            "Dùng lực kéo quá mạnh gây đau khớp khuỷu",
        ],
    },
    {
        "key": "standing biceps stretch",
        "name_vi": "Giãn cơ bắp tay trước đứng (Standing Biceps Stretch)",
        "target_muscle": "Biceps",
        "secondary_muscle": ["Chest"],
        "met_value": 2.2,
        "intensity_level": "Light",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Ưỡn bụng về phía trước để bù trừ biên độ khớp vai",
            "Gập khuỷu tay thay vì duỗi thẳng nhẹ nhàng",
        ],
    },
    {
        "key": "overhead triceps",
        "name_vi": "Giãn cơ bắp tay sau qua đầu (Overhead Triceps Stretch)",
        "target_muscle": "Triceps",
        "secondary_muscle": ["Shoulders"],
        "met_value": 2.2,
        "intensity_level": "Light",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Gập đầu về phía trước khiến cằm chạm ngực",
            "Kéo cùi chỏ quá mạnh sang bên đối diện",
        ],
    },
    {
        "key": "all fours quad stretch",
        "name_vi": "Giãn cơ tứ đầu đùi tư thế quỳ bò (All Fours Quad Stretch)",
        "target_muscle": "Quadriceps",
        "secondary_muscle": ["Glutes"],
        "met_value": 2.3,
        "intensity_level": "Light",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Võng lưng dưới khi kéo gót chân về mông",
            "Đặt đầu gối trên mặt sàn cứng không có thảm đệm",
        ],
    },
    {
        "key": "standing hamstring and calf stretch",
        "name_vi": "Giãn cơ đùi sau và bắp chân đứng (Standing Hamstring & Calf Stretch)",
        "target_muscle": "Hamstrings",
        "secondary_muscle": ["Calves"],
        "met_value": 2.4,
        "intensity_level": "Light",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Cong tròn toàn bộ cột sống thay vì gập từ khớp hông",
            "Khóa cứng khớp gối chân trước quá mức",
        ],
    },
    {
        "key": "ankle on the knee",
        "name_vi": "Giãn cơ mông hình số 4 (Figure 4 Glute Stretch)",
        "target_muscle": "Glutes",
        "secondary_muscle": ["Hamstrings"],
        "met_value": 2.3,
        "intensity_level": "Light",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Nhấc mông và xương cụt khỏi thảm",
            "Gồng cứng cơ cổ và vai khi kéo chân",
        ],
    },
    {
        "key": "ankle circles",
        "name_vi": "Xoay khớp cổ chân thả lỏng (Ankle Circles)",
        "target_muscle": "Calves",
        "secondary_muscle": [],
        "met_value": 2.0,
        "intensity_level": "Light",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Xoay giật cục hoặc dùng cả cẳng chân thay vì chỉ xoay khớp cổ chân",
        ],
    },
    {
        "key": "standing gastrocnemius calf stretch",
        "name_vi": "Giãn bắp chân chống tường (Standing Calf Stretch)",
        "target_muscle": "Calves",
        "secondary_muscle": ["Hamstrings"],
        "met_value": 2.3,
        "intensity_level": "Light",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Nhấc gót chân sau lên khỏi mặt sàn",
            "Bàn chân sau xoay hướng ra ngoài thay vì hướng thẳng về trước",
        ],
    },
    {
        "key": "pelvic tilt into bridge",
        "name_vi": "Nghiêng xương chậu kết hợp nâng hông nhẹ (Pelvic Tilt Bridge)",
        "target_muscle": "Abs",
        "secondary_muscle": ["Glutes"],
        "met_value": 2.4,
        "intensity_level": "Light",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Ưỡn lưng trên quá cao làm mất kiểm soát cơ bụng dưới",
            "Không siết nhẹ cơ sàn chậu và cơ bụng",
        ],
    },
    {
        "key": "knee across the body",
        "name_vi": "Vặn mình gập gối giãn cơ liên sườn và lưng (Knee Across The Body)",
        "target_muscle": "Abs",
        "secondary_muscle": ["Glutes"],
        "met_value": 2.3,
        "intensity_level": "Light",
        "banned_for": [],
        "clinical_reasons": None,
        "common_mistakes": [
            "Để vai cùng bên nhấc bổng khỏi mặt sàn",
            "Dùng tay kéo gối ép mạnh đột ngột xuống sàn",
        ],
    },
]


def build_50_exercises() -> list[dict[str, Any]]:
    """Đọc raw exercises.json và trích xuất đúng 50 bài tập chuẩn hóa phủ đều 11 nhóm cơ."""
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

    PROCESSED_50_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PROCESSED_50_PATH, mode="w", encoding="utf-8") as out:
        json.dump(processed_exercises, out, ensure_ascii=False, indent=2)

    alt_path = BACKEND_DIR / "data" / "processed" / "exercises.json"
    with open(alt_path, mode="w", encoding="utf-8") as out:
        json.dump(processed_exercises, out, ensure_ascii=False, indent=2)

    return processed_exercises


if __name__ == "__main__":
    items = build_50_exercises()
    print(f"[+] Đã trích xuất và chuẩn hóa thành công {len(items)} bài tập vào: {PROCESSED_50_PATH}")
