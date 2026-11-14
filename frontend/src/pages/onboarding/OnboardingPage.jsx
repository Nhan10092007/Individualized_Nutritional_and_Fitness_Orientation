import {
  ArrowLeft,
  ArrowRight,
  CalendarDays,
  CheckCircle2,
  Target,
  User,
  Wallet,
} from "lucide-react";
import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import Navbar from "../../components/common/Navbar";
import {
  BiometricsFields,
  BudgetFields,
  GoalFields,
  ScheduleHealthFields,
  SectionHeader,
} from "../../components/profile/SurveyFormSections";
import { useAuth } from "../../context/useAuth";
import { getApiErrorMessage } from "../../services/api";
import { userService } from "../../services/userService";
import {
  buildInitialFormData,
  buildSurveyPayload,
  formatBudgetTier,
  validateSurveyStep,
} from "../../utils/surveyConfig";

const STEP_LABELS = [
  "1. Sinh trắc",
  "2. Mục tiêu",
  "3. Lịch & Sức khỏe",
  "4. Ngân sách",
];

export default function OnboardingPage() {
  const { user, refreshProfile } = useAuth();
  const navigate = useNavigate();

  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState(() => buildInitialFormData(user));
  const [error, setError] = useState("");
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
        setError(
          "Bạn chỉ có thể chọn tối đa 6 ngày tập mỗi tuần để đảm bảo thời gian phục hồi."
        );
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

  function handleNext() {
    const validationErr = validateSurveyStep(formData, step);
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

  async function handleWizardSubmit(e) {
    e.preventDefault();
    if (step < 4) {
      handleNext();
      return;
    }

    const validationErr =
      validateSurveyStep(formData, 1) ||
      validateSurveyStep(formData, 3) ||
      validateSurveyStep(formData, 4);
    if (validationErr) {
      setError(validationErr);
      return;
    }

    setError("");
    setSubmitting(true);
    try {
      const data = await userService.submitOnboarding(buildSurveyPayload(formData));
      await refreshProfile();
      setFirstTimeResult(data);
    } catch (err) {
      setError(
        getApiErrorMessage(err, "Không thể lưu khảo sát. Vui lòng kiểm tra lại dữ liệu.")
      );
    } finally {
      setSubmitting(false);
    }
  }

  // Người dùng mới vừa hoàn thành khảo sát lần đầu -> hiện màn hình kết quả
  if (firstTimeResult) {
    return (
      <div className="app-shell">
        <Navbar />
        <main className="main-content" style={{ margin: "0 auto", width: "100%" }}>
          <div className="onboarding-container">
            <div className="dash-hero" style={{ marginBottom: "20px" }}>
              <div>
                <div className="dash-hero-badges">
                  <span className="badge badge-success">
                    <CheckCircle2 size={14} />
                    <span>Hoàn thành khảo sát</span>
                  </span>
                </div>
                <h1 className="dash-hero-title">Kết quả phân tích chỉ số cơ thể</h1>
                <p className="dash-hero-desc">{firstTimeResult.message}</p>
              </div>
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
              <SectionHeader
                icon={User}
                iconTone="dash-icon-blue"
                title="Chỉ số sinh trắc & Năng lượng hằng ngày"
              />
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
                  <div className="metric-value" style={{ color: "var(--primary)" }}>
                    {firstTimeResult.target_calorie_kcal} kcal
                  </div>
                  {firstTimeResult.is_safety_floor_triggered && (
                    <div className="metric-sub">Đã kích hoạt sàn an toàn y tế</div>
                  )}
                </div>
              </div>
            </div>

            <div className="card">
              <SectionHeader
                icon={Target}
                iconTone="dash-icon-emerald"
                title="Phân bổ dinh dưỡng đa lượng (Macro)"
              />
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
              <SectionHeader
                icon={Wallet}
                iconTone="dash-icon-amber"
                title="Ràng buộc lịch tập & Dinh dưỡng"
              />
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
                        <CheckCircle2 size={14} />
                        <span>Không có giới hạn bài tập</span>
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
                <span>Bắt đầu sử dụng</span>
                <ArrowRight size={16} />
              </button>
            </div>
          </div>
        </main>
      </div>
    );
  }

  // Đã khảo sát trước đó -> chuyển về trang Hồ sơ cá nhân hợp nhất
  if (user?.is_onboarded) {
    return <Navigate to="/profile" replace />;
  }

  // Người dùng MỚI chưa khảo sát -> Form Wizard 4 bước lần đầu
  return (
    <div className="app-shell">
      <Navbar />
      <main className="main-content" style={{ margin: "0 auto", width: "100%" }}>
        <div className="onboarding-container">
          <div className="dash-hero" style={{ marginBottom: "20px" }}>
            <div>
              <h1 className="dash-hero-title">Khảo sát thể chất &amp; Ràng buộc</h1>
              <p className="dash-hero-desc">
                Cung cấp thông tin cá nhân để hệ thống tính toán BMR, TDEE, Macro và lọc bài tập an toàn.
              </p>
            </div>
            <span className="badge badge-accent">Bước {step} / 4</span>
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
                <SectionHeader
                  icon={User}
                  iconTone="dash-icon-blue"
                  title="Bước 1: Chỉ số sinh trắc cơ bản"
                />
                <BiometricsFields formData={formData} onUpdateField={updateField} />
              </>
            )}

            {step === 2 && (
              <>
                <SectionHeader
                  icon={Target}
                  iconTone="dash-icon-emerald"
                  title="Bước 2: Mục tiêu & Trình độ tập luyện"
                />
                <GoalFields formData={formData} onUpdateField={updateField} />
              </>
            )}

            {step === 3 && (
              <>
                <SectionHeader
                  icon={CalendarDays}
                  iconTone="dash-icon-violet"
                  title="Bước 3: Lịch tập khả dụng & Tình trạng sức khỏe"
                />
                <ScheduleHealthFields
                  formData={formData}
                  onUpdateField={updateField}
                  onToggleDay={toggleDay}
                  onToggleCondition={toggleMedicalCondition}
                />
              </>
            )}

            {step === 4 && (
              <>
                <SectionHeader
                  icon={Wallet}
                  iconTone="dash-icon-amber"
                  title="Bước 4: Ngân sách dinh dưỡng hằng ngày"
                />
                <BudgetFields formData={formData} onUpdateField={updateField} />
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
                  <ArrowLeft size={16} />
                  <span>Quay lại</span>
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
                  <span>Tiếp theo</span>
                  <ArrowRight size={16} />
                </button>
              ) : (
                <button
                  key="btn-submit"
                  type="submit"
                  className="btn btn-primary"
                  disabled={submitting}
                >
                  <CheckCircle2 size={16} />
                  <span>{submitting ? "Đang tính toán..." : "Hoàn thành khảo sát"}</span>
                </button>
              )}
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}
