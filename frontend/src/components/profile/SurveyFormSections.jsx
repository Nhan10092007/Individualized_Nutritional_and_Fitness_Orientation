import {
  DAYS_OPTIONS,
  GOAL_OPTIONS,
  LEVEL_OPTIONS,
  MEDICAL_OPTIONS,
} from "../../utils/surveyConfig";

export function SectionHeader({ icon: Icon, iconTone, title, rightContent = null }) {
  return (
    <div className="section-card-head">
      <div className="section-card-title-wrap">
        <span className={`dash-icon-badge ${iconTone}`}>
          <Icon size={18} />
        </span>
        <h2 className="card-title">{title}</h2>
      </div>
      {rightContent}
    </div>
  );
}

export function BiometricsFields({ formData, onUpdateField }) {
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
            onClick={() => onUpdateField("gender", "male")}
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
            onClick={() => onUpdateField("gender", "female")}
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
            onChange={(e) => onUpdateField("age", e.target.value)}
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
            onChange={(e) => onUpdateField("height_cm", e.target.value)}
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
          onChange={(e) => onUpdateField("weight_kg", e.target.value)}
          required
        />
      </div>
    </div>
  );
}

export function GoalFields({ formData, onUpdateField }) {
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
              onClick={() => onUpdateField("fitness_goal", opt.value)}
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
              onClick={() => onUpdateField("fitness_level", opt.value)}
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

export function ScheduleHealthFields({
  formData,
  onUpdateField,
  onToggleDay,
  onToggleCondition,
}) {
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
                onClick={() => onToggleDay(day.value)}
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
          onChange={(e) => onUpdateField("session_duration_mins", e.target.value)}
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
                  onChange={() => onToggleCondition(cond.value)}
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

export function BudgetFields({ formData, onUpdateField }) {
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
          onChange={(e) => onUpdateField("daily_budget_vnd", e.target.value)}
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
            onClick={() => onUpdateField("daily_budget_vnd", preset)}
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
