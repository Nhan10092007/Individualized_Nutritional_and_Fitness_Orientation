import {
  Activity,
  ArrowRight,
  CalendarDays,
  Coffee,
  Dumbbell,
  Flame,
  User,
  Wallet,
} from "lucide-react";
import { Link } from "react-router-dom";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
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

const WEEK_DAYS = [
  { key: "Mon", short: "T2", full: "Thứ 2" },
  { key: "Tue", short: "T3", full: "Thứ 3" },
  { key: "Wed", short: "T4", full: "Thứ 4" },
  { key: "Thu", short: "T5", full: "Thứ 5" },
  { key: "Fri", short: "T6", full: "Thứ 6" },
  { key: "Sat", short: "T7", full: "Thứ 7" },
  { key: "Sun", short: "CN", full: "Chủ nhật" },
];

const JS_DAY_TO_KEY = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

function getBmiInfo(bmi) {
  if (bmi == null) return { label: "Chưa có", badgeClass: "badge" };
  if (bmi < 18.5) return { label: "Thiếu cân", badgeClass: "badge badge-warning" };
  if (bmi < 25) return { label: "Bình thường", badgeClass: "badge badge-success" };
  if (bmi < 30) return { label: "Thừa cân", badgeClass: "badge badge-warning" };
  return { label: "Béo phì", badgeClass: "badge badge-danger" };
}

function formatBudgetTier(tier) {
  if (tier === "tier_50k_to_100k") return "Tiết kiệm (50k – 100k/ngày)";
  if (tier === "tier_over_100k") return "Thoải mái (Trên 100k/ngày)";
  return tier || "Chưa thiết lập";
}

function formatTodayVi(date) {
  const dayNames = [
    "Chủ nhật",
    "Thứ 2",
    "Thứ 3",
    "Thứ 4",
    "Thứ 5",
    "Thứ 6",
    "Thứ 7",
  ];
  const dayName = dayNames[date.getDay()];
  const dd = String(date.getDate()).padStart(2, "0");
  const mm = String(date.getMonth() + 1).padStart(2, "0");
  const yyyy = date.getFullYear();
  return `${dayName}, ${dd}/${mm}/${yyyy}`;
}

export default function DashboardPage() {
  const { user } = useAuth();

  const bio = user?.biometrics || {};
  const targets = user?.plan_targets || {};
  const macros = targets?.macro_split || {};
  const constraints = user?.constraints || {};

  const availableDays = Array.isArray(targets.available_days)
    ? targets.available_days
    : [];
  const durationMins = Number(targets.session_duration_mins || 0);
  const weeklyMinutes = availableDays.length * durationMins;

  const now = new Date();
  const todayKey = JS_DAY_TO_KEY[now.getDay()];
  const isTrainingToday = availableDays.includes(todayKey);

  const bmr = Number(targets.bmr_kcal || 0);
  const tdee = Number(targets.tdee_kcal || 0);
  const targetKcal = Number(targets.target_calorie_kcal || 0);
  const calorieDelta = tdee > 0 && targetKcal > 0 ? Math.round(targetKcal - tdee) : 0;

  let calorieDeltaText = "Cân bằng theo TDEE";
  if (calorieDelta < 0) {
    calorieDeltaText = `Thâm hụt ${Math.abs(calorieDelta).toLocaleString("vi-VN")} kcal/ngày`;
  } else if (calorieDelta > 0) {
    calorieDeltaText = `Thặng dư +${calorieDelta.toLocaleString("vi-VN")} kcal/ngày`;
  }

  const proteinG = Number(macros.protein_g || 0);
  const carbG = Number(macros.carb_g || 0);
  const fatG = Number(macros.fat_g || 0);

  const proteinKcal = proteinG * 4;
  const carbKcal = carbG * 4;
  const fatKcal = fatG * 9;
  const totalMacroKcal = proteinKcal + carbKcal + fatKcal;

  const macroChartData = [
    {
      name: "Protein (Đạm)",
      grams: proteinG,
      kcal: proteinKcal,
      pct: totalMacroKcal > 0 ? Math.round((proteinKcal / totalMacroKcal) * 100) : 0,
      color: "#059669",
    },
    {
      name: "Carbohydrate (Tinh bột)",
      grams: carbG,
      kcal: carbKcal,
      pct: totalMacroKcal > 0 ? Math.round((carbKcal / totalMacroKcal) * 100) : 0,
      color: "#2563eb",
    },
    {
      name: "Fat (Chất béo)",
      grams: fatG,
      kcal: fatKcal,
      pct: totalMacroKcal > 0 ? Math.round((fatKcal / totalMacroKcal) * 100) : 0,
      color: "#f59e0b",
    },
  ];

  const hasMacroData = totalMacroKcal > 0;
  const energyData = [
    { name: "BMR", value: bmr, color: "#64748b" },
    { name: "TDEE", value: tdee, color: "#2563eb" },
    { name: "Mục tiêu", value: targetKcal, color: "#059669" },
  ];

  const bmiInfo = getBmiInfo(bio.bmi);

  return (
    <div className="dash-stack">
      {/* Hero Banner */}
      <section className="dash-hero">
        <div>
          <div className="dash-hero-badges">
            <span className="badge">
              <CalendarDays size={13} />
              <span>{formatTodayVi(now)}</span>
            </span>
            {isTrainingToday ? (
              <span className="badge badge-success">
                <Flame size={13} />
                <span>Hôm nay: Ngày tập luyện ({durationMins || 45} phút)</span>
              </span>
            ) : (
              <span className="badge badge-accent">
                <Coffee size={13} />
                <span>Hôm nay: Ngày nghỉ phục hồi</span>
              </span>
            )}
          </div>

          <h1 className="dash-hero-title">
            Xin chào, {user?.full_name || "bạn"}!
          </h1>
          <p className="dash-hero-desc">
            Lộ trình cá nhân hóa trình độ{" "}
            <strong>{LEVEL_LABELS[targets.fitness_level] || "tiêu chuẩn"}</strong> với mục
            tiêu{" "}
            <strong>
              {targetKcal > 0 ? `${targetKcal.toLocaleString("vi-VN")} kcal/ngày` : "cân bằng"}
            </strong>{" "}
            và tần suất <strong>{availableDays.length} buổi/tuần</strong>.
          </p>
        </div>

        <div className="dash-hero-actions">
          <Link to="/profile" className="btn btn-primary">
            <User size={16} />
            <span>Hồ sơ &amp; Khảo sát</span>
          </Link>
        </div>
      </section>

      {/* 4 KPI Cards */}
      <section className="dash-kpi-grid">
        <div className="dash-kpi-card">
          <div className="dash-kpi-top">
            <span className="dash-kpi-label">Calo mục tiêu / ngày</span>
            <span className="dash-icon-badge dash-icon-emerald">
              <Flame size={18} />
            </span>
          </div>
          <div className="dash-kpi-value">
            {targetKcal > 0 ? `${targetKcal.toLocaleString("vi-VN")} kcal` : "-"}
          </div>
          <div className="dash-kpi-sub">
            <span>{calorieDeltaText}</span>
          </div>
        </div>

        <div className="dash-kpi-card">
          <div className="dash-kpi-top">
            <span className="dash-kpi-label">Cân nặng &amp; BMI</span>
            <span className="dash-icon-badge dash-icon-blue">
              <Activity size={18} />
            </span>
          </div>
          <div className="dash-kpi-value">
            {bio.weight_kg != null ? `${bio.weight_kg} kg` : "-"}
          </div>
          <div className="dash-kpi-sub">
            <span className={bmiInfo.badgeClass}>
              BMI {bio.bmi ?? "-"} • {bmiInfo.label}
            </span>
            {bio.ibw_kg != null && <span>Lý tưởng: {bio.ibw_kg} kg</span>}
          </div>
        </div>

        <div className="dash-kpi-card">
          <div className="dash-kpi-top">
            <span className="dash-kpi-label">Lịch tập hàng tuần</span>
            <span className="dash-icon-badge dash-icon-violet">
              <Dumbbell size={18} />
            </span>
          </div>
          <div className="dash-kpi-value">{availableDays.length} buổi / tuần</div>
          <div className="dash-kpi-sub">
            <span>
              {durationMins > 0
                ? `${durationMins} phút/buổi • Tổng ${weeklyMinutes} phút`
                : "Chưa thiết lập thời lượng"}
            </span>
          </div>
        </div>

        <div className="dash-kpi-card">
          <div className="dash-kpi-top">
            <span className="dash-kpi-label">Ngân sách dinh dưỡng</span>
            <span className="dash-icon-badge dash-icon-amber">
              <Wallet size={18} />
            </span>
          </div>
          <div className="dash-kpi-value">
            {constraints.daily_budget_vnd != null
              ? `${Number(constraints.daily_budget_vnd).toLocaleString("vi-VN")} ₫`
              : "-"}
          </div>
          <div className="dash-kpi-sub">
            <span>{formatBudgetTier(constraints.budget_tier)}</span>
          </div>
        </div>
      </section>

      {/* Charts Row */}
      <section className="dash-two-col">
        {/* Macro Breakdown Donut */}
        <div className="dash-card">
          <div className="dash-card-header">
            <div>
              <h2 className="dash-card-title">Phân bổ Macro mục tiêu</h2>
              <p className="dash-card-subtitle">
                Tỷ lệ năng lượng từ Đạm, Tinh bột và Chất béo mỗi ngày
              </p>
            </div>
            <span className="badge badge-success">
              {GOAL_LABELS[targets.fitness_goal] || "Mục tiêu"}
            </span>
          </div>

          {hasMacroData ? (
            <div className="dash-macro-layout">
              <div className="dash-donut-wrap">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={macroChartData}
                      dataKey="kcal"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      innerRadius={58}
                      outerRadius={82}
                      paddingAngle={3}
                      stroke="none"
                    >
                      {macroChartData.map((entry) => (
                        <Cell key={entry.name} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={(value, name) => [`${value} kcal`, name]}
                      contentStyle={{
                        backgroundColor: "#ffffff",
                        border: "1px solid #e2e8f0",
                        borderRadius: "10px",
                        fontSize: "13px",
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
                <div className="dash-donut-center">
                  <span className="dash-donut-kcal">
                    {targetKcal > 0
                      ? targetKcal.toLocaleString("vi-VN")
                      : totalMacroKcal.toLocaleString("vi-VN")}
                  </span>
                  <span className="dash-donut-unit">kcal / ngày</span>
                </div>
              </div>

              <div className="dash-macro-list">
                {macroChartData.map((item) => (
                  <div key={item.name} className="dash-macro-item">
                    <div className="dash-macro-row">
                      <span className="dash-macro-name">
                        <span
                          className="dash-macro-dot"
                          style={{ backgroundColor: item.color }}
                        />
                        {item.name}
                      </span>
                      <span className="dash-macro-stats">
                        {item.grams} g ({item.pct}%)
                      </span>
                    </div>
                    <div className="dash-progress-track">
                      <div
                        className="dash-progress-fill"
                        style={{
                          width: `${item.pct}%`,
                          backgroundColor: item.color,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p className="page-description">Chưa có dữ liệu Macro để hiển thị.</p>
          )}
        </div>

        {/* Energy Balance Bar Chart */}
        <div className="dash-card">
          <div className="dash-card-header">
            <div>
              <h2 className="dash-card-title">Cân bằng năng lượng (kcal)</h2>
              <p className="dash-card-subtitle">
                So sánh BMR, tổng tiêu hao TDEE và lượng calo mục tiêu
              </p>
            </div>
          </div>

          <div style={{ width: "100%", height: 195 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={energyData}
                margin={{ top: 10, right: 12, left: -12, bottom: 0 }}
                barSize={44}
              >
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis
                  dataKey="name"
                  tick={{ fill: "#475569", fontSize: 13, fontWeight: 600 }}
                  axisLine={{ stroke: "#e2e8f0" }}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fill: "#64748b", fontSize: 12 }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip
                  cursor={{ fill: "#f8fafc" }}
                  formatter={(value) => [`${Number(value).toLocaleString("vi-VN")} kcal`, "Năng lượng"]}
                  contentStyle={{
                    backgroundColor: "#ffffff",
                    border: "1px solid #e2e8f0",
                    borderRadius: "10px",
                    fontSize: "13px",
                  }}
                />
                <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                  {energyData.map((entry) => (
                    <Cell key={entry.name} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="dash-energy-notes">
            <div className="dash-energy-pill">
              <div className="dash-energy-pill-label">Chuyển hóa cơ bản</div>
              <div className="dash-energy-pill-val">
                {bmr > 0 ? `${bmr.toLocaleString("vi-VN")} kcal` : "-"}
              </div>
            </div>
            <div className="dash-energy-pill">
              <div className="dash-energy-pill-label">Tiêu hao cả ngày</div>
              <div className="dash-energy-pill-val">
                {tdee > 0 ? `${tdee.toLocaleString("vi-VN")} kcal` : "-"}
              </div>
            </div>
            <div className="dash-energy-pill">
              <div className="dash-energy-pill-label">Mục tiêu nạp</div>
              <div className="dash-energy-pill-val" style={{ color: "var(--primary)" }}>
                {targetKcal > 0 ? `${targetKcal.toLocaleString("vi-VN")} kcal` : "-"}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Bottom Row: Full-width Weekly Schedule */}
      <section className="dash-card">
        <div className="dash-card-header">
          <div>
            <h2 className="dash-card-title">Lịch tập trong tuần</h2>
            <p className="dash-card-subtitle">
              Các ngày bạn đã chọn sẵn sàng cho buổi tập cá nhân hóa
            </p>
          </div>
          <Link
            to="/workout"
            className="btn btn-secondary"
            style={{ padding: "6px 12px", fontSize: "13px" }}
          >
            <span>Chi tiết</span>
            <ArrowRight size={14} />
          </Link>
        </div>

        <div className="dash-week-grid">
          {WEEK_DAYS.map((day) => {
            const isWorkout = availableDays.includes(day.key);
            const isToday = day.key === todayKey;
            let cardClass = "dash-day-card";
            if (isWorkout) cardClass += " workout";
            if (isToday) cardClass += " today";

            return (
              <div key={day.key} className={cardClass} title={day.full}>
                <span className="dash-day-name">{day.full}</span>
                <span className="dash-day-icon">
                  {isWorkout ? <Dumbbell size={15} /> : <Coffee size={15} />}
                </span>
                <span className="dash-day-status">
                  {isWorkout ? `${durationMins || 45} phút` : "Ngày nghỉ"}
                </span>
                {isToday && <span className="dash-today-tag">Hôm nay</span>}
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}
