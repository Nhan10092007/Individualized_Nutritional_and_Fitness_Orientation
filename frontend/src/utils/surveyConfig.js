export const DAYS_OPTIONS = [
  { value: "Mon", short: "T2", label: "Thứ 2" },
  { value: "Tue", short: "T3", label: "Thứ 3" },
  { value: "Wed", short: "T4", label: "Thứ 4" },
  { value: "Thu", short: "T5", label: "Thứ 5" },
  { value: "Fri", short: "T6", label: "Thứ 6" },
  { value: "Sat", short: "T7", label: "Thứ 7" },
  { value: "Sun", short: "CN", label: "Chủ nhật" },
];

export const GOAL_OPTIONS = [
  {
    value: "fat_loss",
    title: "Giảm mỡ",
    desc: "Thâm hụt 20% calo so với TDEE, ưu tiên đạm cao",
  },
  {
    value: "muscle_gain",
    title: "Tăng cơ",
    desc: "Thặng dư 15% calo so với TDEE, ưu tiên tinh bột phục hồi",
  },
  {
    value: "maintain",
    title: "Duy trì vóc dáng",
    desc: "Cân bằng calo ở mức TDEE để giữ cân và cải thiện thể lực",
  },
];

export const GOAL_MAP = Object.fromEntries(GOAL_OPTIONS.map((g) => [g.value, g]));

export const LEVEL_OPTIONS = [
  {
    value: "beginner",
    title: "Mới bắt đầu",
    desc: "Chưa từng tập hoặc mới tập dưới 3 tháng",
  },
  {
    value: "experienced",
    title: "Có kinh nghiệm",
    desc: "Đã tập đều đặn từ 3 đến 12 tháng",
  },
  {
    value: "advanced",
    title: "Nâng cao",
    desc: "Tập luyện bài bản trên 1 năm",
  },
];

export const LEVEL_MAP = Object.fromEntries(LEVEL_OPTIONS.map((l) => [l.value, l]));

export const MEDICAL_OPTIONS = [
  {
    value: "knee_osteoarthritis",
    title: "Thoái hóa / Đau khớp gối",
    desc: "Loại bỏ các bài gập gối sâu quá 90 độ hoặc nén áp lực lớn lên khớp gối",
  },
  {
    value: "hypertension",
    title: "Huyết áp cao",
    desc: "Loại bỏ các bài nín thở nén hơi (Valsalva), dốc đầu xuống thấp hoặc tạ quá nặng",
  },
];

export const CONDITION_LABELS = Object.fromEntries(
  MEDICAL_OPTIONS.map((m) => [m.value, m.title])
);

export function formatBudgetTier(tier) {
  if (tier === "tier_50k_to_100k") return "50.000 – 100.000 VNĐ / ngày";
  if (tier === "tier_over_100k") return "Trên 100.000 VNĐ / ngày";
  return tier || "Chưa thiết lập";
}

export function buildInitialFormData(user) {
  const savedBudget = user?.constraints?.daily_budget_vnd;
  const fallbackBudget =
    user?.constraints?.budget_tier === "tier_over_100k" ? 120000 : 80000;

  return {
    gender: user?.biometrics?.gender || "male",
    age: user?.biometrics?.age ?? 20,
    height_cm: user?.biometrics?.height_cm ?? 170,
    weight_kg: user?.biometrics?.weight_kg ?? 65,
    fitness_goal: user?.plan_targets?.fitness_goal || "maintain",
    fitness_level: user?.plan_targets?.fitness_level || "beginner",
    available_days: user?.plan_targets?.available_days?.length
      ? user.plan_targets.available_days
      : ["Mon", "Wed", "Fri"],
    session_duration_mins: user?.plan_targets?.session_duration_mins ?? 45,
    medical_conditions: user?.constraints?.medical_conditions || [],
    daily_budget_vnd: savedBudget ?? fallbackBudget,
  };
}

export function validateSurveyStep(formData, step) {
  if (step === 1) {
    const age = Number(formData.age);
    const height = Number(formData.height_cm);
    const weight = Number(formData.weight_kg);

    if (Number.isNaN(age) || age < 10 || age > 70) {
      return "Tuổi phải nằm trong khoảng từ 10 đến 70.";
    }
    if (Number.isNaN(height) || height < 125 || height > 200) {
      return "Chiều cao phải nằm trong khoảng từ 125 cm đến 200 cm.";
    }
    if (Number.isNaN(weight) || weight < 35 || weight > 150) {
      return "Cân nặng phải nằm trong khoảng từ 35 kg đến 150 kg.";
    }
  }

  if (step === 3) {
    const daysCount = formData.available_days.length;
    const duration = Number(formData.session_duration_mins);
    if (daysCount < 2 || daysCount > 6) {
      return "Vui lòng chọn từ 2 đến 6 ngày tập mỗi tuần.";
    }
    if (Number.isNaN(duration) || duration < 30 || duration > 120) {
      return "Thời lượng mỗi buổi tập phải từ 30 đến 120 phút.";
    }
  }

  if (step === 4) {
    const budget = Number(formData.daily_budget_vnd);
    if (Number.isNaN(budget) || budget < 50000) {
      return "Ngân sách ăn uống tối thiểu là 50.000 VNĐ/ngày.";
    }
  }

  return "";
}

export function buildSurveyPayload(formData) {
  return {
    gender: formData.gender,
    age: Number(formData.age),
    height_cm: Number(formData.height_cm),
    weight_kg: Number(formData.weight_kg),
    fitness_goal: formData.fitness_goal,
    fitness_level: formData.fitness_level,
    available_days: formData.available_days,
    session_duration_mins: Number(formData.session_duration_mins),
    medical_conditions: formData.medical_conditions,
    daily_budget_vnd: Number(formData.daily_budget_vnd),
  };
}
