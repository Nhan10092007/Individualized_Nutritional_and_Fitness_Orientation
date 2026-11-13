import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../../components/common/Navbar";
import Sidebar from "../../components/common/Sidebar";
import { useAuth } from "../../context/useAuth";
import { getApiErrorMessage } from "../../services/api";
import { userService } from "../../services/userService";

const DAYS_OPTIONS = [
  { value: "Mon", label: "Thứ 2" },
  { value: "Tue", label: "Thứ 3" },
  { value: "Wed", label: "Thứ 4" },
  { value: "Thu", label: "Thứ 5" },
  { value: "Fri", label: "Thứ 6" },
  { value: "Sat", label: "Thứ 7" },
  { value: "Sun", label: "Chủ nhật" },
];

const DAY_LABELS = Object.fromEntries(DAYS_OPTIONS.map((d) => [d.value, d.label]));

const GOAL_OPTIONS = [
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

const GOAL_LABELS = Object.fromEntries(GOAL_OPTIONS.map((g) => [g.value, g.title]));

const LEVEL_OPTIONS = [
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

const LEVEL_LABELS = Object.fromEntries(LEVEL_OPTIONS.map((l) => [l.value, l.title]));

const MEDICAL_OPTIONS = [
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

const CONDITION_LABELS = Object.fromEntries(MEDICAL_OPTIONS.map((m) => [m.value, m.title]));

const STEP_LABELS = [
  "1. Sinh trắc",
  "2. Mục tiêu",
  "3. Lịch & Sức khỏe",
  "4. Ngân sách",
];

function formatBudgetTier(tier) {
  if (tier === "tier_50k_to_100k") return "Tiết kiệm (50.000 - 100.000 VNĐ/ngày)";
  if (tier === "tier_over_100k") return "Thoải mái (Trên 100.000 VNĐ/ngày)";
  return tier || "Chưa xác định";
}

function buildInitialFormData(user) {
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

export default function OnboardingPage() {
  const { user, refreshProfile } = useAuth();
  const navigate = useNavigate();

  const [step, setStep] = useState(1);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState(() => buildInitialFormData(user));

  const [error, setError] = useState("");
  const [updateSuccess, setUpdateSuccess] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [firstTimeResult, setFirstTimeResult] = useState(null);

  function updateField(name, value) {
    setFormData((prev) => ({ ...prev, [name]: value }));
    setError("");
  }

  function toggleDay(dayValue) {
    setError("");
    setFormData((prev) => {
      const exists = prev.available_days.includes(dayValue);
      if (exists) {
        return {
          ...prev,
          available_days: prev.available_days.filter((d) => d !== dayValue),
        };
      }
      if (prev.available_days.length >= 6) {
        setError("Bạn chỉ có thể chọn tối đa 6 ngày tập mỗi tuần để đảm bảo thời gian phục hồi.");
        return prev;
      }
      return {
        ...prev,
        available_days: [...prev.available_days, dayValue],
      };
    });
  }

  function toggleMedicalCondition(condValue) {
    setFormData((prev) => {
      const exists = prev.medical_conditions.includes(condValue);
      return {
        ...prev,
        medical_conditions: exists
          ? prev.medical_conditions.filter((c) => c !== condValue)
          : [...prev.medical_conditions, condValue],
      };
    });
  }

  function validateStep(currentStep) {
    if (currentStep === 1) {
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

    if (currentStep === 3) {
      const daysCount = formData.available_days.length;
      const duration = Number(formData.session_duration_mins);
      if (daysCount < 2 || daysCount > 6) {
        return "Vui lòng chọn từ 2 đến 6 ngày tập mỗi tuần.";
      }
      if (Number.isNaN(duration) || duration < 30 || duration > 120) {
        return "Thời lượng mỗi buổi tập phải từ 30 đến 120 phút.";
      }
    }

    if (currentStep === 4) {
      const budget = Number(formData.daily_budget_vnd);
      if (Number.isNaN(budget) || budget < 50000) {
        return "Ngân sách ăn uống tối thiểu là 50.000 VNĐ/ngày.";
      }
    }

    return "";
  }

  function handleNext() {
    const validationErr = validateStep(step);
    if (validationErr) {
      setError(validationErr);
      return;
    }
    setError("");
    setStep((prev) => Math.min(prev + 1, 4));
  }

  function handlePrev() {
    setError("");
    setStep((prev) => Math.max(prev - 1, 1));
  }

  function startEditing() {
    setFormData(buildInitialFormData(user));
    setError("");
    setUpdateSuccess(null);
    setIsEditing(true);
  }

  function cancelEditing() {
    setFormData(buildInitialFormData(user));
    setError("");
    setIsEditing(false);
  }

  async function saveSurveyData(isFirstOnboarding) {
    const validationErr = validateStep(1) || validateStep(3) || validateStep(4);
    if (validationErr) {
      setError(validationErr);
      return;
    }

    setError("");
    setSubmitting(true);
    try {
      const payload = {
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

      const data = await userService.submitOnboarding(payload);
      await refreshProfile();

      if (isFirstOnboarding) {
        setFirstTimeResult(data);
      } else {
        setUpdateSuccess(data);
        setIsEditing(false);
      }
    } catch (err) {
      setError(getApiErrorMessage(err, "Không thể lưu khảo sát. Vui lòng kiểm tra lại dữ liệu."));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleWizardSubmit(e) {
    e.preventDefault();
    if (step < 4) {
      handleNext();
      return;
    }
    await saveSurveyData(true);
  }

  async function handleEditSubmit(e) {
    e.preventDefault();
    await saveSurveyData(false);
  }

  function renderBiometricsFields() {
    return (
      <div className="form-stack">
        <div className="form-group">
          <label className="form-label">Giới tính sinh học</label>
          <div className="option-grid">
            <button
              type="button"
              className={
                formData.gender === "male"
                  ? "option-button selected"
                  : "option-button"
              }
              onClick={() => updateField("gender", "male")}
            >
              <span className="option-title">Nam</span>
              <span className="option-desc">Áp dụng công thức tính chỉ số cho nam</span>
            </button>
            <button
              type="button"
              className={
                formData.gender === "female"
                  ? "option-button selected"
                  : "option-button"
              }
              onClick={() => updateField("gender", "female")}
            >
              <span className="option-title">Nữ</span>
              <span className="option-desc">Áp dụng công thức tính chỉ số cho nữ</span>
            </button>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label" htmlFor="onb-age">
              Tuổi (10 - 70)
            </label>
            <input
              id="onb-age"
              type="number"
              className="form-input"
              min={10}
              max={70}
              value={formData.age}
              onChange={(e) => updateField("age", e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="onb-height">
              Chiều cao (cm, từ 125 - 200)
            </label>
            <input
              id="onb-height"
              type="number"
              step="0.5"
              className="form-input"
              min={125}
              max={200}
              value={formData.height_cm}
              onChange={(e) => updateField("height_cm", e.target.value)}
              required
            />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="onb-weight">
            Cân nặng hiện tại (kg, từ 35 - 150)
          </label>
          <input
            id="onb-weight"
            type="number"
            step="0.5"
            className="form-input"
            min={35}
            max={150}
            value={formData.weight_kg}
            onChange={(e) => updateField("weight_kg", e.target.value)}
            required
          />
        </div>
      </div>
    );
  }

  function renderGoalFields() {
    return (
      <div className="form-stack">
        <div className="form-group">
          <label className="form-label">Mục tiêu chính của bạn</label>
          <div className="option-grid">
            {GOAL_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                type="button"
                className={
                  formData.fitness_goal === opt.value
                    ? "option-button selected"
                    : "option-button"
                }
                onClick={() => updateField("fitness_goal", opt.value)}
              >
                <span className="option-title">{opt.title}</span>
                <span className="option-desc">{opt.desc}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Trình độ tập luyện hiện tại</label>
          <div className="option-grid">
            {LEVEL_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                type="button"
                className={
                  formData.fitness_level === opt.value
                    ? "option-button selected"
                    : "option-button"
                }
                onClick={() => updateField("fitness_level", opt.value)}
              >
                <span className="option-title">{opt.title}</span>
                <span className="option-desc">{opt.desc}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  function renderScheduleAndHealthFields() {
    return (
      <div className="form-stack">
        <div className="form-group">
          <label className="form-label">
            Chọn các ngày có thể tập trong tuần (Đã chọn:{" "}
            {formData.available_days.length}/6 ngày, tối thiểu 2 ngày)
          </label>
          <div className="days-grid">
            {DAYS_OPTIONS.map((day) => {
              const selected = formData.available_days.includes(day.value);
              return (
                <button
                  key={day.value}
                  type="button"
                  className={selected ? "day-pill selected" : "day-pill"}
                  onClick={() => toggleDay(day.value)}
                >
                  {day.label}
                </button>
              );
            })}
          </div>
          {formData.available_days.length < 2 && (
            <span className="field-error">
              Cần chọn ít nhất 2 ngày luyện tập mỗi tuần để tiếp tục (hiện tại:{" "}
              {formData.available_days.length} ngày).
            </span>
          )}
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="onb-duration">
            Thời lượng mỗi buổi tập (30 - 120 phút)
          </label>
          <input
            id="onb-duration"
            type="number"
            className="form-input"
            min={30}
            max={120}
            step={5}
            value={formData.session_duration_mins}
            onChange={(e) =>
              updateField("session_duration_mins", e.target.value)
            }
            required
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            Bệnh lý nền cần tránh bài tập rủi ro (Tùy chọn)
          </label>
          <div className="checkbox-list">
            {MEDICAL_OPTIONS.map((cond) => {
              const checked = formData.medical_conditions.includes(cond.value);
              return (
                <label key={cond.value} className="checkbox-item">
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={() => toggleMedicalCondition(cond.value)}
                  />
                  <div>
                    <div className="option-title">{cond.title}</div>
                    <div className="option-desc">{cond.desc}</div>
                  </div>
                </label>
              );
            })}
          </div>
        </div>
      </div>
    );
  }

  function renderBudgetFields() {
    return (
      <div className="form-stack">
        <div className="form-group">
          <label className="form-label" htmlFor="onb-budget">
            Ngân sách ăn uống mỗi ngày (VNĐ, tối thiểu 50.000 VNĐ)
          </label>
          <input
            id="onb-budget"
            type="number"
            className="form-input"
            min={50000}
            step={5000}
            value={formData.daily_budget_vnd}
            onChange={(e) => updateField("daily_budget_vnd", e.target.value)}
            required
          />
          <span className="form-hint">
            Hệ thống sẽ phân nhóm từ 50.000 - 100.000 VNĐ hoặc trên 100.000 VNĐ để tối ưu thực đơn.
          </span>
        </div>

        <div className="option-grid">
          {[50000, 80000, 120000, 150000].map((preset) => (
            <button
              key={preset}
              type="button"
              className={
                Number(formData.daily_budget_vnd) === preset
                  ? "option-button selected"
                  : "option-button"
              }
              onClick={() => updateField("daily_budget_vnd", preset)}
            >
              <span className="option-title">
                {preset.toLocaleString("vi-VN")} VNĐ
              </span>
              <span className="option-desc">
                {preset <= 100000 ? "Nhóm tiết kiệm" : "Nhóm thoải mái"}
              </span>
            </button>
          ))}
        </div>
      </div>
    );
  }

  // 1. Màn hình kết quả sau khi người dùng mới hoàn thành khảo sát lần đầu
  if (firstTimeResult) {
    return (
      <div className="app-shell">
        <Navbar />
        <main className="main-content" style={{ margin: "0 auto", width: "100%" }}>
          <div className="onboarding-container">
            <div className="page-header">
              <div>
                <h1 className="page-title">Kết quả phân tích chỉ số cơ thể</h1>
                <p className="page-description">{firstTimeResult.message}</p>
              </div>
              <span className="badge badge-success">Hoàn thành khảo sát</span>
            </div>

            {firstTimeResult.validation_warnings?.length > 0 && (
              <div className="alert alert-warning">
                <strong>Lưu ý điều chỉnh an toàn y khoa:</strong>
                <ul style={{ margin: "8px 0 0", paddingLeft: "18px" }}>
                  {firstTimeResult.validation_warnings.map((w, idx) => (
                    <li key={idx}>{w}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="card">
              <h2 className="card-title">Chỉ số sinh trắc & Năng lượng hằng ngày</h2>
              <div className="metrics-grid">
                <div className="metric-box">
                  <div className="metric-label">BMI</div>
                  <div className="metric-value">{firstTimeResult.bmi}</div>
                </div>
                <div className="metric-box">
                  <div className="metric-label">Cân nặng lý tưởng (IBW)</div>
                  <div className="metric-value">{firstTimeResult.ibw_kg} kg</div>
                </div>
                <div className="metric-box">
                  <div className="metric-label">BMR</div>
                  <div className="metric-value">{firstTimeResult.bmr_kcal} kcal</div>
                </div>
                <div className="metric-box">
                  <div className="metric-label">TDEE</div>
                  <div className="metric-value">{firstTimeResult.tdee_kcal} kcal</div>
                </div>
                <div className="metric-box">
                  <div className="metric-label">Calo mục tiêu / ngày</div>
                  <div className="metric-value">
                    {firstTimeResult.target_calorie_kcal} kcal
                  </div>
                  {firstTimeResult.is_safety_floor_triggered && (
                    <div className="metric-sub">Đã kích hoạt sàn an toàn y tế</div>
                  )}
                </div>
              </div>
            </div>

            <div className="card">
              <h2 className="card-title">Phân bổ dinh dưỡng đa lượng (Macro)</h2>
              <div className="metrics-grid">
                <div className="metric-box">
                  <div className="metric-label">Protein (Đạm)</div>
                  <div className="metric-value">
                    {firstTimeResult.macro_split?.protein_g} g
                  </div>
                </div>
                <div className="metric-box">
                  <div className="metric-label">Carbohydrate (Tinh bột)</div>
                  <div className="metric-value">
                    {firstTimeResult.macro_split?.carb_g} g
                  </div>
                </div>
                <div className="metric-box">
                  <div className="metric-label">Fat (Chất béo)</div>
                  <div className="metric-value">
                    {firstTimeResult.macro_split?.fat_g} g
                  </div>
                </div>
              </div>
            </div>

            <div className="card">
              <h2 className="card-title">Ràng buộc lịch tập & Dinh dưỡng</h2>
              <div className="info-list">
                <div>
                  <div className="info-item-label">Phân khúc ngân sách dinh dưỡng</div>
                  <div className="info-item-value">
                    {formatBudgetTier(firstTimeResult.budget_tier)}
                  </div>
                </div>
                <div>
                  <div className="info-item-label">Nhãn bài tập bị loại bỏ</div>
                  <div className="tag-list" style={{ marginTop: "6px" }}>
                    {firstTimeResult.banned_exercise_tags?.length > 0 ? (
                      firstTimeResult.banned_exercise_tags.map((tag) => (
                        <span key={tag} className="badge badge-danger">
                          {tag}
                        </span>
                      ))
                    ) : (
                      <span className="badge badge-success">
                        Không có giới hạn bài tập
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>

            <div className="btn-row">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => navigate("/profile")}
              >
                Xem hồ sơ cá nhân
              </button>
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => navigate("/dashboard")}
              >
                Vào trang Tổng quan
              </button>
            </div>
          </div>
        </main>
      </div>
    );
  }

  // 2. Người dùng ĐÃ khảo sát -> Mặc định hiển thị thông tin đã lưu, chỉ sửa khi bấm nút
  if (user?.is_onboarded) {
    const bio = user.biometrics || {};
    const targets = user.plan_targets || {};
    const constraints = user.constraints || {};

    return (
      <div className="app-shell">
        <Navbar />
        <div className="app-body">
          <Sidebar />
          <main className="main-content">
            <div className="page-header">
              <div>
                <h1 className="page-title">Thông tin khảo sát thể chất</h1>
                <p className="page-description">
                  {isEditing
                    ? "Chỉnh sửa thông số bạn muốn thay đổi và lưu để hệ thống tính toán lại kế hoạch."
                    : "Thông tin hiện tại của bạn đã được lưu. Nhấn Chỉnh sửa thông tin khi bạn muốn thay đổi."}
                </p>
              </div>
              {!isEditing && (
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={startEditing}
                >
                  Chỉnh sửa thông tin
                </button>
              )}
            </div>

            {error && <div className="alert alert-error">{error}</div>}

            {updateSuccess && !isEditing && (
              <>
                <div className="alert alert-success">
                  Cập nhật thông tin thành công. Mục tiêu mới:{" "}
                  <strong>{updateSuccess.target_calorie_kcal} kcal/ngày</strong> (BMI:{" "}
                  {updateSuccess.bmi}, TDEE: {updateSuccess.tdee_kcal} kcal).
                </div>
                {updateSuccess.validation_warnings?.length > 0 && (
                  <div className="alert alert-warning">
                    <strong>Lưu ý điều chỉnh an toàn y khoa:</strong>
                    <ul style={{ margin: "8px 0 0", paddingLeft: "18px" }}>
                      {updateSuccess.validation_warnings.map((w, idx) => (
                        <li key={idx}>{w}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </>
            )}

            {isEditing ? (
              <form onSubmit={handleEditSubmit}>
                <div className="card">
                  <h2 className="card-title">1. Chỉ số sinh trắc cơ bản</h2>
                  {renderBiometricsFields()}
                </div>

                <div className="card">
                  <h2 className="card-title">2. Mục tiêu & Trình độ tập luyện</h2>
                  {renderGoalFields()}
                </div>

                <div className="card">
                  <h2 className="card-title">
                    3. Lịch tập khả dụng & Tình trạng sức khỏe
                  </h2>
                  {renderScheduleAndHealthFields()}
                </div>

                <div className="card">
                  <h2 className="card-title">4. Ngân sách dinh dưỡng hằng ngày</h2>
                  {renderBudgetFields()}
                </div>

                <div className="btn-row">
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={cancelEditing}
                    disabled={submitting}
                  >
                    Hủy bỏ
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={
                      submitting ||
                      formData.available_days.length < 2 ||
                      formData.available_days.length > 6
                    }
                  >
                    {submitting ? "Đang lưu..." : "Lưu thay đổi"}
                  </button>
                </div>
              </form>
            ) : (
              <div>
                <div className="card">
                  <h2 className="card-title">1. Chỉ số sinh trắc cơ bản</h2>
                  <div className="info-list">
                    <div>
                      <div className="info-item-label">Giới tính sinh học</div>
                      <div className="info-item-value">
                        {bio.gender === "male"
                          ? "Nam"
                          : bio.gender === "female"
                          ? "Nữ"
                          : "Chưa có"}
                      </div>
                    </div>
                    <div>
                      <div className="info-item-label">Tuổi</div>
                      <div className="info-item-value">
                        {bio.age != null ? `${bio.age} tuổi` : "Chưa có"}
                      </div>
                    </div>
                    <div>
                      <div className="info-item-label">Chiều cao</div>
                      <div className="info-item-value">
                        {bio.height_cm != null ? `${bio.height_cm} cm` : "Chưa có"}
                      </div>
                    </div>
                    <div>
                      <div className="info-item-label">Cân nặng</div>
                      <div className="info-item-value">
                        {bio.weight_kg != null ? `${bio.weight_kg} kg` : "Chưa có"}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="card">
                  <h2 className="card-title">2. Mục tiêu & Trình độ tập luyện</h2>
                  <div className="info-list">
                    <div>
                      <div className="info-item-label">Mục tiêu chính</div>
                      <div className="info-item-value">
                        {GOAL_LABELS[targets.fitness_goal] || "Chưa có"}
                      </div>
                    </div>
                    <div>
                      <div className="info-item-label">Trình độ tập luyện</div>
                      <div className="info-item-value">
                        {LEVEL_LABELS[targets.fitness_level] || "Chưa có"}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="card">
                  <h2 className="card-title">
                    3. Lịch tập khả dụng & Tình trạng sức khỏe
                  </h2>
                  <div className="info-list">
                    <div>
                      <div className="info-item-label">Ngày tập trong tuần</div>
                      <div className="tag-list" style={{ marginTop: "6px" }}>
                        {targets.available_days?.length > 0 ? (
                          targets.available_days.map((day) => (
                            <span key={day} className="badge">
                              {DAY_LABELS[day] || day}
                            </span>
                          ))
                        ) : (
                          <span className="info-item-value">Chưa chọn</span>
                        )}
                      </div>
                    </div>
                    <div>
                      <div className="info-item-label">Thời lượng mỗi buổi</div>
                      <div className="info-item-value">
                        {targets.session_duration_mins != null
                          ? `${targets.session_duration_mins} phút`
                          : "Chưa có"}
                      </div>
                    </div>
                    <div>
                      <div className="info-item-label">Bệnh lý nền</div>
                      <div className="tag-list" style={{ marginTop: "6px" }}>
                        {constraints.medical_conditions?.length > 0 ? (
                          constraints.medical_conditions.map((cond) => (
                            <span key={cond} className="badge badge-warning">
                              {CONDITION_LABELS[cond] || cond}
                            </span>
                          ))
                        ) : (
                          <span className="badge badge-success">
                            Không có bệnh lý nền
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="card">
                  <h2 className="card-title">4. Ngân sách dinh dưỡng hằng ngày</h2>
                  <div className="info-list">
                    <div>
                      <div className="info-item-label">Ngân sách mỗi ngày</div>
                      <div className="info-item-value">
                        {constraints.daily_budget_vnd != null
                          ? `${Number(constraints.daily_budget_vnd).toLocaleString("vi-VN")} VNĐ`
                          : formatBudgetTier(constraints.budget_tier)}
                      </div>
                    </div>
                    <div>
                      <div className="info-item-label">Phân khúc thực đơn</div>
                      <div className="info-item-value">
                        {formatBudgetTier(constraints.budget_tier)}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </main>
        </div>
      </div>
    );
  }

  // 3. Người dùng MỚI chưa khảo sát -> Form Wizard 4 bước lần đầu
  return (
    <div className="app-shell">
      <Navbar />
      <main className="main-content" style={{ margin: "0 auto", width: "100%" }}>
        <div className="onboarding-container">
          <div className="page-header">
            <div>
              <h1 className="page-title">Khảo sát thể chất & Ràng buộc</h1>
              <p className="page-description">
                Cung cấp thông tin cá nhân để hệ thống tính toán BMR, TDEE, Macro và lọc bài tập an toàn.
              </p>
            </div>
          </div>

          <div className="stepper">
            {STEP_LABELS.map((label, idx) => {
              const stepNumber = idx + 1;
              let cls = "step-item";
              if (stepNumber === step) cls += " active";
              else if (stepNumber < step) cls += " done";
              return (
                <div key={label} className={cls}>
                  {label}
                </div>
              );
            })}
          </div>

          {error && <div className="alert alert-error">{error}</div>}

          <form className="card" onSubmit={handleWizardSubmit}>
            {step === 1 && (
              <>
                <h2 className="card-title">Bước 1: Chỉ số sinh trắc cơ bản</h2>
                {renderBiometricsFields()}
              </>
            )}

            {step === 2 && (
              <>
                <h2 className="card-title">Bước 2: Mục tiêu & Trình độ tập luyện</h2>
                {renderGoalFields()}
              </>
            )}

            {step === 3 && (
              <>
                <h2 className="card-title">
                  Bước 3: Lịch tập khả dụng & Tình trạng sức khỏe
                </h2>
                {renderScheduleAndHealthFields()}
              </>
            )}

            {step === 4 && (
              <>
                <h2 className="card-title">Bước 4: Ngân sách dinh dưỡng hằng ngày</h2>
                {renderBudgetFields()}
              </>
            )}

            <div className="btn-row">
              {step > 1 ? (
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handlePrev}
                  disabled={submitting}
                >
                  Quay lại
                </button>
              ) : (
                <div />
              )}

              {step < 4 ? (
                <button
                  key="btn-next"
                  type="button"
                  className="btn btn-primary"
                  onClick={handleNext}
                  disabled={
                    step === 3 &&
                    (formData.available_days.length < 2 ||
                      formData.available_days.length > 6)
                  }
                >
                  Tiếp theo
                </button>
              ) : (
                <button
                  key="btn-submit"
                  type="submit"
                  className="btn btn-primary"
                  disabled={submitting}
                >
                  {submitting ? "Đang tính toán..." : "Hoàn thành khảo sát"}
                </button>
              )}
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}
