import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import ToastNotice from "../../components/common/ToastNotice";
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

const BUBBLE_ANIMATION_MS = 1650;
const TAB_TRANSITION_MS = 300;

function formatVnd(amount) {
  return `${Math.round(Number(amount || 0)).toLocaleString("vi-VN")} đ`;
}

function getDailyMacros(dayPlan) {
  return (dayPlan?.meals || []).reduce(
    (acc, meal) => {
      for (const item of meal?.items || []) {
        acc.protein += Number(item?.protein_g || 0);
        acc.carbs += Number(item?.carbs_g || 0);
        acc.fat += Number(item?.fat_g || 0);
      }
      return acc;
    },
    { protein: 0, carbs: 0, fat: 0 }
  );
}

export default function NutritionPage() {
  const { user } = useAuth();

  const [plan, setPlan] = useState(null);
  const [hasPlan, setHasPlan] = useState(false);
  const [selectedDay, setSelectedDay] = useState("ALL");
  const [exitingDay, setExitingDay] = useState(null);

  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [isBubbleAnimating, setIsBubbleAnimating] = useState(false);
  const [generationKey, setGenerationKey] = useState(0);
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  const bubbleTimerRef = useRef(null);
  const tabTimerRef = useRef(null);

  useEffect(() => {
    return () => {
      if (bubbleTimerRef.current) clearTimeout(bubbleTimerRef.current);
      if (tabTimerRef.current) clearTimeout(tabTimerRef.current);
    };
  }, []);

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

  function handleSelectDayTab(nextDay) {
    if (String(nextDay) === String(selectedDay)) return;
    if (tabTimerRef.current) clearTimeout(tabTimerRef.current);
    setExitingDay(selectedDay);
    setSelectedDay(nextDay);
    tabTimerRef.current = setTimeout(() => {
      setExitingDay(null);
      tabTimerRef.current = null;
    }, TAB_TRANSITION_MS);
  }

  async function handleGenerate() {
    if (generating || isBubbleAnimating) return;
    setError("");
    setSuccessMsg("");
    setGenerating(true);
    try {
      const data = await nutritionService.generateMealPlan(7);
      setPlan(data || null);
      setHasPlan(Boolean(data?.weekly_plan?.length));
      setExitingDay(null);
      setSelectedDay("ALL");
      setGenerationKey((prev) => prev + 1);
      setIsBubbleAnimating(true);
      if (bubbleTimerRef.current) clearTimeout(bubbleTimerRef.current);
      bubbleTimerRef.current = setTimeout(() => {
        setIsBubbleAnimating(false);
        bubbleTimerRef.current = null;
      }, BUBBLE_ANIMATION_MS);
      setSuccessMsg("Đã cập nhật thành công");
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
  const gender = user?.biometrics?.gender || "male";
  const hardFloor = gender === "female" ? 1200 : 1500;
  const bmrKcal = Number(targets.bmr_kcal || 0);
  const minCaloriesFloor = Number(
    plan?.min_calories_floor || Math.max(bmrKcal, hardFloor)
  );

  const weeklyPlan = Array.isArray(plan?.weekly_plan) ? plan.weekly_plan : [];

  function getDaysForFilter(dayFilter) {
    return dayFilter === "ALL"
      ? weeklyPlan
      : weeklyPlan.filter((d) => String(d.day_of_week) === String(dayFilter));
  }

  const visibleDays = getDaysForFilter(selectedDay);
  const exitingDays = exitingDay !== null ? getDaysForFilter(exitingDay) : [];

  const budgetRemaining = Number(plan?.budget_remaining_vnd || 0);
  const isGenerateDisabled = generating || isBubbleAnimating || loading;

  function renderDayMealCards(daysList, shouldBubbleAnimate = false) {
    return daysList.map((dayPlan, dIdx) => {
      const dailyMacros = getDailyMacros(dayPlan);
      return (
        <section
          key={dayPlan.day_of_week}
          className={
            shouldBubbleAnimate ? "card bubble-drop-item" : "card"
          }
          style={
            shouldBubbleAnimate
              ? { animationDelay: `${Math.min(0.18 + dIdx * 0.06, 0.45)}s` }
              : undefined
          }
        >
          <div className="workout-session-header">
            <div>
              <h2 className="workout-session-title">
                {DAY_NAMES[dayPlan.day_of_week] ||
                  `Ngày ${dayPlan.day_of_week}`}
              </h2>
              <p className="page-description" style={{ margin: 0 }}>
                {(dayPlan.meals || []).length} bữa ăn chính (Sáng riêng · Trưa &amp; Tối cùng món)
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
                P {Math.round(dailyMacros.protein)}g · C{" "}
                {Math.round(dailyMacros.carbs)}g · F{" "}
                {Math.round(dailyMacros.fat)}g
              </span>
              <span className="badge">
                Tổng chi phí: {formatVnd(dayPlan.daily_total_cost)}
              </span>
            </div>
          </div>

          {dayPlan.budget_warning && (
            <div className="alert alert-warning" style={{ marginBottom: "14px" }}>
              {dayPlan.budget_warning}
            </div>
          )}

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
                          <strong>{Math.ceil(item.grams || 0)}</strong> g
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
      );
    });
  }

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
            <span className="badge">
              Sàn calo an toàn: {Math.round(minCaloriesFloor).toLocaleString("vi-VN")} kcal/ngày
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
            disabled={isGenerateDisabled}
          >
            {generating
              ? "Đang sinh thực đơn..."
              : isBubbleAnimating
              ? "Đang hiển thị thực đơn..."
              : hasPlan
              ? "Sinh lại thực đơn mới"
              : "Tạo thực đơn 7 ngày"}
          </button>
        </div>
      </section>

      {error && <div className="alert alert-error">{error}</div>}
      {plan?.budget_warning && (
        <div className="alert alert-warning">{plan.budget_warning}</div>
      )}
      <ToastNotice message={successMsg} onClose={() => setSuccessMsg("")} />

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
            disabled={isGenerateDisabled}
          >
            {generating
              ? "Đang sinh thực đơn..."
              : isBubbleAnimating
              ? "Đang hiển thị thực đơn..."
              : "Tạo thực đơn 7 ngày"}
          </button>
        </div>
      ) : (
        <div key={`nutrition-gen-${generationKey}`} className="dash-stack">
          {/* Summary KPI Grid */}
          <section
            className={
              generationKey > 0
                ? "dash-kpi-grid bubble-drop-item"
                : "dash-kpi-grid"
            }
          >
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
          <div
            className={
              generationKey > 0
                ? "workout-tabs bubble-drop-item"
                : "workout-tabs"
            }
            style={generationKey > 0 ? { animationDelay: "0.1s" } : undefined}
          >
            <button
              type="button"
              className={
                selectedDay === "ALL" ? "workout-tab active" : "workout-tab"
              }
              onClick={() => handleSelectDayTab("ALL")}
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
                  onClick={() => handleSelectDayTab(dayKey)}
                >
                  {DAY_NAMES[dayPlan.day_of_week] || `Ngày ${dayPlan.day_of_week}`}{" "}
                  · {Math.round(dayPlan.daily_total_calories || 0)} kcal
                </button>
              );
            })}
          </div>

          {/* Daily Meal Cards with 0.3s tab transition & bubble generation transition */}
          <div className="tab-transition-stage">
            {exitingDay !== null && (
              <div
                key={`nutri-exit-${exitingDay}`}
                className="tab-page-pane tab-page-exit dash-stack"
                aria-hidden="true"
              >
                {renderDayMealCards(exitingDays, false)}
              </div>
            )}
            <div
              key={`nutri-active-${selectedDay}`}
              className={
                exitingDay !== null
                  ? "tab-page-pane tab-page-enter dash-stack"
                  : "tab-page-pane dash-stack"
              }
            >
              {renderDayMealCards(
                visibleDays,
                generationKey > 0 && exitingDay === null
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
