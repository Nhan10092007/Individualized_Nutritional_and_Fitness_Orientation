import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../context/useAuth";
import { getApiErrorMessage } from "../../services/api";
import { nutritionService } from "../../services/nutritionService";

const DAY_NAMES = {
  1: "Thứ 2",
  2: "Thứ 3",
  3: "Thứ 4",
  4: "Thứ 5",
  5: "Thứ 6",
  6: "Thứ 7",
  7: "Chủ nhật",
};

const GOAL_LABELS = {
  fat_loss: "Giảm mỡ",
  muscle_gain: "Tăng cơ",
  maintain: "Duy trì vóc dáng",
  general_fitness: "Thể lực tổng quát",
};

function formatVnd(amount) {
  return `${Math.round(Number(amount || 0)).toLocaleString("vi-VN")} đ`;
}

export default function NutritionPage() {
  const { user } = useAuth();

  const [plan, setPlan] = useState(null);
  const [hasPlan, setHasPlan] = useState(false);
  const [selectedDay, setSelectedDay] = useState("ALL");

  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  useEffect(() => {
    let isMounted = true;

    async function fetchPlan() {
      setLoading(true);
      setError("");
      try {
        const data = await nutritionService.getMealPlan();
        if (!isMounted) return;
        setPlan(data || null);
        setHasPlan(Boolean(data?.weekly_plan?.length));
      } catch (err) {
        if (!isMounted) return;
        if (err?.response?.status === 404) {
          setHasPlan(false);
          setPlan(null);
        } else {
          setError(
            getApiErrorMessage(err, "Không thể tải thực đơn dinh dưỡng hiện tại.")
          );
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    fetchPlan();
    return () => {
      isMounted = false;
    };
  }, []);

  async function handleGenerate() {
    setError("");
    setSuccessMsg("");
    setGenerating(true);
    try {
      const data = await nutritionService.generateMealPlan(7);
      setPlan(data || null);
      setHasPlan(Boolean(data?.weekly_plan?.length));
      setSelectedDay("ALL");
      setSuccessMsg("Đã tạo và lưu thực đơn tối ưu 7 ngày thành công!");
    } catch (err) {
      setError(
        getApiErrorMessage(err, "Không thể sinh thực đơn. Vui lòng thử lại.")
      );
    } finally {
      setGenerating(false);
    }
  }

  const targets = user?.plan_targets || {};
  const macros = targets?.macro_split || {};
  const constraints = user?.constraints || {};

  const targetCalories = Number(targets.target_calorie_kcal || 2000);
  const targetProtein = Number(macros.protein_g || 100);
  const targetCarbs = Number(macros.carb_g || 200);
  const targetFat = Number(macros.fat_g || 50);
  const dailyBudget = Number(constraints.daily_budget_vnd || 100000);

  const weeklyPlan = Array.isArray(plan?.weekly_plan) ? plan.weekly_plan : [];
  const visibleDays =
    selectedDay === "ALL"
      ? weeklyPlan
      : weeklyPlan.filter((d) => String(d.day_of_week) === String(selectedDay));

  const budgetRemaining = Number(plan?.budget_remaining_vnd || 0);

  return (
    <div className="dash-stack">
      {/* Header / Hero */}
      <section className="dash-hero">
        <div>
          <div className="dash-hero-badges">
            <span className="badge badge-success">
              Mục tiêu: {GOAL_LABELS[targets.fitness_goal] || "Chưa thiết lập"}
            </span>
            <span className="badge">
              Calo mục tiêu: {targetCalories.toLocaleString("vi-VN")} kcal/ngày
            </span>
            <span className="badge">Ngân sách: {formatVnd(dailyBudget)}/ngày</span>
          </div>
          <h1 className="dash-hero-title">Thực đơn dinh dưỡng cá nhân hóa</h1>
          <p className="dash-hero-desc">
            Tự động phân bổ thực đơn 7 ngày (Sáng · Trưa · Tối) cân bằng Protein,
            Tinh bột, Chất béo và Calo trong phạm vi ngân sách hằng ngày của bạn.
          </p>
        </div>

        <div className="dash-hero-actions">
          <Link to="/profile" className="btn btn-secondary">
            Điều chỉnh thông số
          </Link>
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleGenerate}
            disabled={generating || loading}
          >
            {generating
              ? "Đang sinh thực đơn..."
              : hasPlan
              ? "Sinh lại thực đơn mới"
              : "Tạo thực đơn 7 ngày"}
          </button>
        </div>
      </section>

      {error && <div className="alert alert-error">{error}</div>}
      {successMsg && <div className="alert alert-success">{successMsg}</div>}

      {loading ? (
        <div className="card">
          <p className="page-description">Đang tải thực đơn của bạn...</p>
        </div>
      ) : !hasPlan || weeklyPlan.length === 0 ? (
        <div className="card workout-empty">
          <h2 className="workout-empty-title">Bạn chưa có thực đơn nào</h2>
          <p className="workout-empty-desc">
            Nhấn nút <strong>Tạo thực đơn 7 ngày</strong> để hệ thống tính toán
            khẩu phần phù hợp với Calo, Macro và ngân sách trong hồ sơ của bạn.
          </p>
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleGenerate}
            disabled={generating}
          >
            {generating ? "Đang sinh thực đơn..." : "Tạo thực đơn 7 ngày"}
          </button>
        </div>
      ) : (
        <>
          {/* Summary KPI Grid */}
          <section className="dash-kpi-grid">
            <div className="dash-kpi-card">
              <div className="dash-kpi-top">
                <span className="dash-kpi-label">Calo TB / ngày</span>
              </div>
              <div className="dash-kpi-value">
                {Number(plan.total_calories || 0).toLocaleString("vi-VN")} kcal
              </div>
              <div className="dash-kpi-sub">
                <span>
                  Mục tiêu: {targetCalories.toLocaleString("vi-VN")} kcal/ngày
                </span>
              </div>
            </div>

            <div className="dash-kpi-card">
              <div className="dash-kpi-top">
                <span className="dash-kpi-label">Macro TB / ngày (P · C · F)</span>
              </div>
              <div className="dash-kpi-value">
                {Math.round(plan.total_protein_g || 0)}g ·{" "}
                {Math.round(plan.total_carbs_g || 0)}g ·{" "}
                {Math.round(plan.total_fat_g || 0)}g
              </div>
              <div className="dash-kpi-sub">
                <span>
                  Mục tiêu: {targetProtein}g Đạm · {targetCarbs}g Tinh bột ·{" "}
                  {targetFat}g Béo
                </span>
              </div>
            </div>

            <div className="dash-kpi-card">
              <div className="dash-kpi-top">
                <span className="dash-kpi-label">Chi phí TB / ngày</span>
              </div>
              <div className="dash-kpi-value">
                {formatVnd(plan.total_cost_vnd)}
              </div>
              <div className="dash-kpi-sub">
                <span>Giới hạn ngân sách: {formatVnd(dailyBudget)}/ngày</span>
              </div>
            </div>

            <div className="dash-kpi-card">
              <div className="dash-kpi-top">
                <span className="dash-kpi-label">Ngân sách còn dư</span>
              </div>
              <div className="dash-kpi-value">
                {budgetRemaining >= 0
                  ? formatVnd(budgetRemaining)
                  : `Vượt ${formatVnd(Math.abs(budgetRemaining))}`}
              </div>
              <div className="dash-kpi-sub">
                <span>Thực đơn {weeklyPlan.length} ngày · 3 bữa/ngày</span>
              </div>
            </div>
          </section>

          {/* Day Filter Tabs */}
          <div className="workout-tabs">
            <button
              type="button"
              className={
                selectedDay === "ALL" ? "workout-tab active" : "workout-tab"
              }
              onClick={() => setSelectedDay("ALL")}
            >
              Cả tuần ({weeklyPlan.length} ngày)
            </button>
            {weeklyPlan.map((dayPlan) => {
              const dayKey = String(dayPlan.day_of_week);
              return (
                <button
                  key={dayKey}
                  type="button"
                  className={
                    String(selectedDay) === dayKey
                      ? "workout-tab active"
                      : "workout-tab"
                  }
                  onClick={() => setSelectedDay(dayKey)}
                >
                  {DAY_NAMES[dayPlan.day_of_week] || `Ngày ${dayPlan.day_of_week}`}{" "}
                  · {Math.round(dayPlan.daily_total_calories || 0)} kcal
                </button>
              );
            })}
          </div>

          {/* Daily Meal Cards */}
          {visibleDays.map((dayPlan) => (
            <section key={dayPlan.day_of_week} className="card">
              <div className="workout-session-header">
                <div>
                  <h2 className="workout-session-title">
                    {DAY_NAMES[dayPlan.day_of_week] ||
                      `Ngày ${dayPlan.day_of_week}`}
                  </h2>
                  <p className="page-description" style={{ margin: 0 }}>
                    {(dayPlan.meals || []).length} bữa ăn chính (Sáng · Trưa · Tối)
                  </p>
                </div>

                <div className="workout-session-meta">
                  <span className="badge badge-success">
                    {Number(dayPlan.daily_total_calories || 0).toLocaleString(
                      "vi-VN"
                    )}{" "}
                    kcal
                  </span>
                  <span className="badge">
                    Tổng chi phí: {formatVnd(dayPlan.daily_total_cost)}
                  </span>
                </div>
              </div>

              <div className="nutrition-meal-list">
                {(dayPlan.meals || []).map((meal, mIdx) => (
                  <div
                    key={`${dayPlan.day_of_week}-${meal.meal_name}-${mIdx}`}
                    className="nutrition-meal-block"
                  >
                    <div className="nutrition-meal-header">
                      <h3 className="nutrition-meal-title">{meal.meal_name}</h3>
                      <div className="nutrition-meal-meta">
                        <span className="badge badge-success">
                          {Number(meal.total_calories || 0).toLocaleString(
                            "vi-VN"
                          )}{" "}
                          kcal
                        </span>
                        <span className="badge">
                          {formatVnd(meal.total_cost_vnd)}
                        </span>
                      </div>
                    </div>

                    <div className="workout-table-wrap">
                      <table className="workout-table">
                        <thead>
                          <tr>
                            <th style={{ width: "52px" }}>STT</th>
                            <th>Tên thực phẩm</th>
                            <th>Khối lượng</th>
                            <th>Calo</th>
                            <th>Đạm (P)</th>
                            <th>Tinh bột (C)</th>
                            <th>Chất béo (F)</th>
                            <th>Chi phí</th>
                          </tr>
                        </thead>
                        <tbody>
                          {(meal.items || []).map((item, iIdx) => (
                            <tr key={`${item.food_id}-${iIdx}`}>
                              <td>{iIdx + 1}</td>
                              <td className="workout-ex-name">{item.name}</td>
                              <td>
                                <strong>{Math.round(item.grams || 0)}</strong> g
                              </td>
                              <td>{item.calories} kcal</td>
                              <td>{item.protein_g} g</td>
                              <td>{item.carbs_g} g</td>
                              <td>{item.fat_g} g</td>
                              <td>{formatVnd(item.cost_vnd)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          ))}
        </>
      )}
    </div>
  );
}
