import { useAuth } from "../../context/useAuth";

const GOAL_LABELS = {
  fat_loss: "Giảm mỡ",
  muscle_gain: "Tăng cơ",
  maintain: "Duy trì vóc dáng",
};

const LEVEL_LABELS = {
  beginner: "Mới bắt đầu",
  experienced: "Có kinh nghiệm",
  advanced: "Nâng cao",
};

const GENDER_LABELS = {
  male: "Nam",
  female: "Nữ",
};

const DAY_LABELS = {
  Mon: "Thứ 2",
  Tue: "Thứ 3",
  Wed: "Thứ 4",
  Thu: "Thứ 5",
  Fri: "Thứ 6",
  Sat: "Thứ 7",
  Sun: "Chủ nhật",
};

const CONDITION_LABELS = {
  knee_osteoarthritis: "Thoái hóa / Đau khớp gối",
  hypertension: "Huyết áp cao",
};

function getBmiCategory(bmi) {
  if (bmi == null) return "Chưa có";
  if (bmi < 18.5) return "Thiếu cân";
  if (bmi < 25) return "Bình thường";
  if (bmi < 30) return "Thừa cân";
  return "Béo phì";
}

function formatBudgetTier(tier) {
  if (tier === "tier_50k_to_100k") return "50.000 - 100.000 VNĐ / ngày";
  if (tier === "tier_over_100k") return "Trên 100.000 VNĐ / ngày";
  return tier || "Chưa thiết lập";
}

export default function ProfilePage() {
  const { user } = useAuth();

  const bio = user?.biometrics || {};
  const targets = user?.plan_targets || {};
  const macros = targets?.macro_split || {};
  const constraints = user?.constraints || {};

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Hồ sơ cá nhân</h1>
          <p className="page-description">
            Thông tin tài khoản, chỉ số cơ thể và kế hoạch dinh dưỡng, tập luyện cá nhân của bạn.
          </p>
        </div>
      </div>

      <div className="card">
        <h2 className="card-title">Thông tin tài khoản</h2>
        <div className="info-list">
          <div>
            <div className="info-item-label">Họ và tên</div>
            <div className="info-item-value">{user?.full_name || "Chưa có"}</div>
          </div>
          <div>
            <div className="info-item-label">Email</div>
            <div className="info-item-value">{user?.email || "Chưa có"}</div>
          </div>
          <div>
            <div className="info-item-label">Trạng thái khảo sát</div>
            <div style={{ marginTop: "4px" }}>
              {user?.is_onboarded ? (
                <span className="badge badge-success">Đã hoàn thành Onboarding</span>
              ) : (
                <span className="badge badge-warning">Chưa hoàn thành</span>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="card-title">Chỉ số sinh trắc cơ thể</h2>
        <div className="metrics-grid" style={{ marginBottom: "20px" }}>
          <div className="metric-box">
            <div className="metric-label">BMI</div>
            <div className="metric-value">{bio.bmi ?? "-"}</div>
            <div className="metric-sub">{getBmiCategory(bio.bmi)}</div>
          </div>
          <div className="metric-box">
            <div className="metric-label">Cân nặng hiện tại</div>
            <div className="metric-value">
              {bio.weight_kg != null ? `${bio.weight_kg} kg` : "-"}
            </div>
          </div>
          <div className="metric-box">
            <div className="metric-label">Cân nặng lý tưởng (IBW)</div>
            <div className="metric-value">
              {bio.ibw_kg != null ? `${bio.ibw_kg} kg` : "-"}
            </div>
          </div>
          <div className="metric-box">
            <div className="metric-label">Chiều cao</div>
            <div className="metric-value">
              {bio.height_cm != null ? `${bio.height_cm} cm` : "-"}
            </div>
          </div>
        </div>

        <div className="info-list">
          <div>
            <div className="info-item-label">Giới tính sinh học</div>
            <div className="info-item-value">
              {GENDER_LABELS[bio.gender] || "Chưa có"}
            </div>
          </div>
          <div>
            <div className="info-item-label">Tuổi</div>
            <div className="info-item-value">
              {bio.age != null ? `${bio.age} tuổi` : "Chưa có"}
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="card-title">Mục tiêu năng lượng & Dinh dưỡng</h2>
        <div className="metrics-grid" style={{ marginBottom: "20px" }}>
          <div className="metric-box">
            <div className="metric-label">BMR</div>
            <div className="metric-value">
              {targets.bmr_kcal != null ? `${targets.bmr_kcal} kcal` : "-"}
            </div>
          </div>
          <div className="metric-box">
            <div className="metric-label">TDEE</div>
            <div className="metric-value">
              {targets.tdee_kcal != null ? `${targets.tdee_kcal} kcal` : "-"}
            </div>
          </div>
          <div className="metric-box">
            <div className="metric-label">Calo mục tiêu / ngày</div>
            <div className="metric-value">
              {targets.target_calorie_kcal != null
                ? `${targets.target_calorie_kcal} kcal`
                : "-"}
            </div>
          </div>
        </div>

        <div className="metrics-grid" style={{ marginBottom: "20px" }}>
          <div className="metric-box">
            <div className="metric-label">Protein mục tiêu</div>
            <div className="metric-value">
              {macros.protein_g != null ? `${macros.protein_g} g` : "-"}
            </div>
          </div>
          <div className="metric-box">
            <div className="metric-label">Carbohydrate mục tiêu</div>
            <div className="metric-value">
              {macros.carb_g != null ? `${macros.carb_g} g` : "-"}
            </div>
          </div>
          <div className="metric-box">
            <div className="metric-label">Fat mục tiêu</div>
            <div className="metric-value">
              {macros.fat_g != null ? `${macros.fat_g} g` : "-"}
            </div>
          </div>
        </div>

        <div className="info-list">
          <div>
            <div className="info-item-label">Mục tiêu tập luyện</div>
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
          <div>
            <div className="info-item-label">Thời lượng mỗi buổi</div>
            <div className="info-item-value">
              {targets.session_duration_mins != null
                ? `${targets.session_duration_mins} phút`
                : "Chưa có"}
            </div>
          </div>
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
        </div>
      </div>

      <div className="card">
        <h2 className="card-title">Ràng buộc an toàn & Ngân sách</h2>
        <div className="info-list">
          <div>
            <div className="info-item-label">Ngân sách ăn uống / ngày</div>
            <div className="info-item-value">
              {constraints.daily_budget_vnd != null
                ? `${Number(constraints.daily_budget_vnd).toLocaleString("vi-VN")} VNĐ (${formatBudgetTier(constraints.budget_tier)})`
                : formatBudgetTier(constraints.budget_tier)}
            </div>
          </div>

          <div>
            <div className="info-item-label">Bệnh lý nền đã khai báo</div>
            <div className="tag-list" style={{ marginTop: "6px" }}>
              {constraints.medical_conditions?.length > 0 ? (
                constraints.medical_conditions.map((cond) => (
                  <span key={cond} className="badge badge-warning">
                    {CONDITION_LABELS[cond] || cond}
                  </span>
                ))
              ) : (
                <span className="badge badge-success">Không có bệnh lý nền</span>
              )}
            </div>
          </div>

          <div>
            <div className="info-item-label">Nhãn bài tập bị loại trừ</div>
            <div className="tag-list" style={{ marginTop: "6px" }}>
              {constraints.banned_exercise_tags?.length > 0 ? (
                constraints.banned_exercise_tags.map((tag) => (
                  <span key={tag} className="badge badge-danger">
                    {tag}
                  </span>
                ))
              ) : (
                <span className="badge badge-success">Không có giới hạn</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
