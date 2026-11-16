import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import ToastNotice from "../../components/common/ToastNotice";
import ExerciseDetailModal from "../../components/exercises/ExerciseDetailModal";
import { MUSCLE_LABELS } from "../../constants/exerciseLabels";
import { useAuth } from "../../context/useAuth";
import { getApiErrorMessage } from "../../services/api";
import { exerciseService } from "../../services/exerciseService";
import { workoutService } from "../../services/workoutService";

const WEEK_DAYS = [
  { key: "Mon", label: "Thứ 2" },
  { key: "Tue", label: "Thứ 3" },
  { key: "Wed", label: "Thứ 4" },
  { key: "Thu", label: "Thứ 5" },
  { key: "Fri", label: "Thứ 6" },
  { key: "Sat", label: "Thứ 7" },
  { key: "Sun", label: "Chủ nhật" },
];

const DAY_LABELS = Object.fromEntries(WEEK_DAYS.map((d) => [d.key, d.label]));

const GOAL_LABELS = {
  fat_loss: "Giảm mỡ",
  muscle_gain: "Tăng cơ",
  maintain: "Duy trì vóc dáng",
  general_fitness: "Thể lực tổng quát",
};

const LEVEL_LABELS = {
  beginner: "Mới bắt đầu",
  experienced: "Có kinh nghiệm",
  advanced: "Nâng cao",
};

const SPLIT_DESCRIPTIONS = {
  "Full Body": "Toàn thân mỗi buổi, tối ưu phục hồi cho lịch 2-3 ngày/tuần",
  "Upper/Lower": "Luân phiên Thân trên & Thân dưới cho lịch 4 ngày/tuần",
  "Push/Pull/Legs": "Chia nhóm Đẩy - Kéo - Chân cho lịch 5-6 ngày/tuần",
};

function getInitialSelectedDay(schedule) {
  if (!Array.isArray(schedule) || schedule.length === 0) return "Mon";
  const firstOrdered = WEEK_DAYS.find((d) =>
    schedule.some((s) => s.day === d.key)
  );
  return firstOrdered ? firstOrdered.key : schedule[0].day;
}

function formatSessionName(sessionName, fallbackSplit) {
  const cleaned = String(sessionName || "")
    .replace(/\s*[-–]?\s*Session\s*\d*/gi, "")
    .trim();
  return cleaned || fallbackSplit || "Buổi tập";
}

function formatExerciseName(name) {
  const raw = String(name || "").trim();
  if (!raw) return "";
  const match = raw.match(/\(([^)]+)\)\s*$/);
  if (match && /[a-zA-Z]/.test(match[1])) {
    return match[1].trim();
  }
  if (/^plank\b/i.test(raw)) return "Plank";
  return raw;
}

export default function WorkoutPage() {
  const { user } = useAuth();

  const [plan, setPlan] = useState(null);
  const [hasPlan, setHasPlan] = useState(false);
  const [createdAt, setCreatedAt] = useState(null);
  const [selectedDay, setSelectedDay] = useState("Mon");

  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  const [modalOpen, setModalOpen] = useState(false);
  const [modalExercise, setModalExercise] = useState(null);
  const [modalLoading, setModalLoading] = useState(false);
  const [modalError, setModalError] = useState("");
  const exerciseCacheRef = useRef({});
  const activeExerciseReqRef = useRef(0);

  async function handleOpenExercise(exerciseId) {
    if (!exerciseId) return;
    setModalOpen(true);
    setModalError("");

    const cached = exerciseCacheRef.current[exerciseId];
    if (cached) {
      setModalExercise(cached);
      setModalLoading(false);
      return;
    }

    const reqId = ++activeExerciseReqRef.current;
    setModalExercise(null);
    setModalLoading(true);
    try {
      const detail = await exerciseService.getExerciseById(exerciseId);
      exerciseCacheRef.current[exerciseId] = detail;
      if (activeExerciseReqRef.current === reqId) {
        setModalExercise(detail);
      }
    } catch (err) {
      if (activeExerciseReqRef.current === reqId) {
        setModalError(
          getApiErrorMessage(err, "Không thể tải chi tiết bài tập.")
        );
      }
    } finally {
      if (activeExerciseReqRef.current === reqId) {
        setModalLoading(false);
      }
    }
  }

  function handleCloseModal() {
    activeExerciseReqRef.current += 1;
    setModalOpen(false);
    setModalLoading(false);
    setModalError("");
  }

  useEffect(() => {
    let isMounted = true;

    async function fetchPlan() {
      setLoading(true);
      setError("");
      try {
        const data = await workoutService.getWorkoutPlan();
        if (!isMounted) return;
        const loadedPlan = data?.workout_plan || null;
        setHasPlan(Boolean(data?.has_plan && loadedPlan));
        setPlan(loadedPlan);
        setCreatedAt(data?.created_at || null);
        if (loadedPlan?.weekly_schedule?.length) {
          setSelectedDay(getInitialSelectedDay(loadedPlan.weekly_schedule));
        }
      } catch (err) {
        if (isMounted) {
          setError(
            getApiErrorMessage(err, "Không thể tải lịch tập luyện hiện tại.")
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
      const data = await workoutService.generateWorkoutPlan();
      const generatedPlan = data?.workout_plan || null;
      setPlan(generatedPlan);
      setHasPlan(Boolean(generatedPlan));
      setCreatedAt(new Date().toISOString());
      if (generatedPlan?.weekly_schedule?.length) {
        setSelectedDay(getInitialSelectedDay(generatedPlan.weekly_schedule));
      }
      setSuccessMsg("Đã cập nhật thành công");
    } catch (err) {
      setError(
        getApiErrorMessage(err, "Không thể sinh lịch tập. Vui lòng thử lại.")
      );
    } finally {
      setGenerating(false);
    }
  }

  const targets = user?.plan_targets || {};
  const constraints = user?.constraints || {};
  const medicalConditions = Array.isArray(constraints.medical_conditions)
    ? constraints.medical_conditions
    : [];
  const weeklySchedule = Array.isArray(plan?.weekly_schedule)
    ? plan.weekly_schedule
    : [];

  const sessionByDay = Object.fromEntries(
    weeklySchedule.map((session) => [session.day, session])
  );
  const selectedSession = sessionByDay[selectedDay] || null;

  const avgDuration =
    weeklySchedule.length > 0
      ? (
          weeklySchedule.reduce(
            (sum, s) => sum + Number(s.actual_duration_mins || 0),
            0
          ) / weeklySchedule.length
        ).toFixed(1)
      : "0";

  const totalExercisesWeek = weeklySchedule.reduce(
    (sum, s) => sum + Number(s.exercise_count || s.exercises?.length || 0),
    0
  );

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
              Trình độ: {LEVEL_LABELS[targets.fitness_level] || "Mới bắt đầu"}
            </span>
            <span className="badge">
              {targets.available_days?.length || 0} buổi/tuần ·{" "}
              {targets.session_duration_mins || 45} phút/buổi
            </span>
          </div>
          <h1 className="dash-hero-title">Lịch tập luyện cá nhân hóa</h1>
          <p className="dash-hero-desc">
            Tự động phân chia nhóm cơ theo lịch rảnh của bạn, điều chỉnh số hiệp
            theo trình độ và lọc bỏ các bài tập có nguy cơ với tình trạng sức
            khỏe.
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
              ? "Đang sinh lịch tập..."
              : hasPlan
              ? "Sinh lại lịch tập mới"
              : "Tạo lịch tập ngay"}
          </button>
        </div>
      </section>

      {error && <div className="alert alert-error">{error}</div>}
      <ToastNotice message={successMsg} onClose={() => setSuccessMsg("")} />

      {loading ? (
        <div className="card">
          <p className="page-description">Đang tải lịch tập của bạn...</p>
        </div>
      ) : !hasPlan || weeklySchedule.length === 0 ? (
        <div className="card workout-empty">
          <h2 className="workout-empty-title">Bạn chưa có lịch tập nào</h2>
          <p className="workout-empty-desc">
            Nhấn nút <strong>Tạo lịch tập ngay</strong> để hệ thống phân tích số
            ngày rảnh, trình độ và bệnh lý nền trong hồ sơ nhằm tạo lịch tập
            tuần phù hợp nhất cho bạn.
          </p>
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleGenerate}
            disabled={generating}
          >
            {generating ? "Đang sinh lịch tập..." : "Tạo lịch tập ngay"}
          </button>
        </div>
      ) : (
        <>
          {/* Summary KPI Grid */}
          <section className="dash-kpi-grid">
            <div className="dash-kpi-card">
              <div className="dash-kpi-top">
                <span className="dash-kpi-label">Mô hình chia lịch</span>
              </div>
              <div className="dash-kpi-value">{plan.split_type}</div>
              <div className="dash-kpi-sub">
                <span>
                  {SPLIT_DESCRIPTIONS[plan.split_type] ||
                    "Phân bổ tối ưu theo tuần"}
                </span>
              </div>
            </div>

            <div className="dash-kpi-card">
              <div className="dash-kpi-top">
                <span className="dash-kpi-label">Tổng số buổi / tuần</span>
              </div>
              <div className="dash-kpi-value">
                {plan.total_sessions || weeklySchedule.length} buổi
              </div>
              <div className="dash-kpi-sub">
                <span>Tổng {totalExercisesWeek} lượt bài tập trong tuần</span>
              </div>
            </div>

            <div className="dash-kpi-card">
              <div className="dash-kpi-top">
                <span className="dash-kpi-label">Thời lượng trung bình</span>
              </div>
              <div className="dash-kpi-value">{avgDuration} phút</div>
              <div className="dash-kpi-sub">
                <span>
                  Giới hạn tối đa:{" "}
                  {weeklySchedule[0]?.max_allowed_mins ||
                    targets.session_duration_mins ||
                    45}{" "}
                  phút/buổi
                </span>
              </div>
            </div>

            <div className="dash-kpi-card">
              <div className="dash-kpi-top">
                <span className="dash-kpi-label">Kiểm soát an toàn</span>
              </div>
              <div className="dash-kpi-value">
                {medicalConditions.length > 0
                  ? `${medicalConditions.length} bệnh nền`
                  : "An toàn đầy đủ"}
              </div>
              <div className="dash-kpi-sub">
                <span>
                  {createdAt
                    ? `Cập nhật: ${new Date(createdAt).toLocaleString("vi-VN")}`
                    : "Đã lưu vào hệ thống"}
                </span>
              </div>
            </div>
          </section>

          {/* 7-Day Weekly Overview Frame */}
          <section className="card">
            <div className="workout-week-header">
              <h2 className="workout-week-title">Khung lịch tập 7 ngày</h2>
              <p className="workout-week-hint">
                Nhấn vào từng ngày bên dưới để xem chi tiết bài tập
              </p>
            </div>

            <div className="workout-week-grid">
              {WEEK_DAYS.map((dayObj) => {
                const session = sessionByDay[dayObj.key];
                const isActive = selectedDay === dayObj.key;
                const muscleSummary = session
                  ? (session.target_muscles || [])
                      .map((m) => MUSCLE_LABELS[m] || m)
                      .join(" · ")
                  : "";
                const exerciseCount = session
                  ? session.exercise_count ?? session.exercises?.length ?? 0
                  : 0;

                return (
                  <div
                    key={dayObj.key}
                    role="button"
                    tabIndex={0}
                    onClick={() => setSelectedDay(dayObj.key)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        setSelectedDay(dayObj.key);
                      }
                    }}
                    className={[
                      "workout-day-card",
                      session ? "has-session" : "is-rest",
                      isActive ? "active" : "",
                    ]
                      .filter(Boolean)
                      .join(" ")}
                  >
                    <div className="workout-day-head">
                      <span className="workout-day-name">{dayObj.label}</span>
                      <span
                        className={
                          session
                            ? "workout-day-pill"
                            : "workout-day-pill rest"
                        }
                      >
                        {session ? "Tập luyện" : "Nghỉ"}
                      </span>
                    </div>

                    {session ? (
                      <>
                        <div className="workout-day-summary">
                          <span className="workout-day-split">
                            {formatSessionName(
                              session.session_name,
                              plan.split_type
                            )}
                          </span>
                          <span className="workout-day-muscles">
                            {muscleSummary}
                          </span>
                        </div>
                        <ul className="workout-day-exercises">
                          {(session.exercises || []).map((ex, eIdx) => {
                            const displayName = formatExerciseName(ex.name);
                            return (
                              <li
                                key={`${ex.exercise_id}-${eIdx}`}
                                className="workout-day-ex-item"
                                title={`${displayName} (${ex.sets}×${ex.reps})`}
                              >
                                <button
                                  type="button"
                                  className="workout-day-ex-name workout-day-ex-btn"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleOpenExercise(ex.exercise_id);
                                  }}
                                >
                                  {displayName}
                                </button>
                                <span className="workout-day-ex-sets">
                                  {ex.sets}×{ex.reps}
                                </span>
                              </li>
                            );
                          })}
                        </ul>
                        <div className="workout-day-meta">
                          <span>{exerciseCount} bài</span>
                          <span>{session.actual_duration_mins} phút</span>
                        </div>
                      </>
                    ) : (
                      <div className="workout-day-summary">
                        <span className="workout-day-split">
                          Ngày nghỉ ngơi
                        </span>
                        <span className="workout-day-muscles">
                          Phục hồi cơ bắp &amp; tái tạo năng lượng
                        </span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </section>

          {/* Selected Day Detail */}
          {selectedSession ? (
            <section className="card">
              <div className="workout-session-header">
                <div>
                  <h2 className="workout-session-title">
                    {DAY_LABELS[selectedSession.day] || selectedSession.day} —{" "}
                    {formatSessionName(
                      selectedSession.session_name,
                      plan.split_type
                    )}
                  </h2>
                  <div className="tag-list" style={{ marginTop: "8px" }}>
                    {(selectedSession.target_muscles || []).map((muscle) => (
                      <span key={muscle} className="badge">
                        {MUSCLE_LABELS[muscle] || muscle}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="workout-session-meta">
                  <span className="badge badge-success">
                    {selectedSession.actual_duration_mins} /{" "}
                    {selectedSession.max_allowed_mins} phút
                  </span>
                  <span className="badge">
                    {selectedSession.exercise_count ??
                      selectedSession.exercises?.length ??
                      0}{" "}
                    bài tập
                  </span>
                </div>
              </div>

              <div className="workout-table-wrap">
                <table className="workout-table">
                  <thead>
                    <tr>
                      <th style={{ width: "52px" }}>STT</th>
                      <th>Tên bài tập</th>
                      <th>Nhóm cơ</th>
                      <th>Hiệp x Số lần</th>
                      <th>Nghỉ giữa hiệp</th>
                      <th>Nghỉ giữa các bài</th>
                      <th>Thời gian dự kiến</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(selectedSession.exercises || []).map((ex, eIdx) => (
                      <tr key={`${ex.exercise_id}-${eIdx}`}>
                        <td>{eIdx + 1}</td>
                        <td className="workout-ex-name">
                          <button
                            type="button"
                            className="workout-ex-link"
                            title="Xem hướng dẫn chi tiết bài tập"
                            onClick={() => handleOpenExercise(ex.exercise_id)}
                          >
                            {formatExerciseName(ex.name)}
                          </button>
                        </td>
                        <td>
                          <span className="badge">
                            {MUSCLE_LABELS[ex.target_muscle] ||
                              ex.target_muscle}
                          </span>
                        </td>
                        <td>
                          <strong>{ex.sets}</strong> hiệp ×{" "}
                          <strong>{ex.reps}</strong> lần
                        </td>
                        <td>{ex.rest_seconds ?? 120} giây</td>
                        <td>
                          {eIdx < (selectedSession.exercises || []).length - 1
                            ? `${ex.rest_between_exercises_seconds ?? 120} giây`
                            : "Kết thúc buổi"}
                        </td>
                        <td>
                          {ex.estimated_time_seconds != null
                            ? `${(ex.estimated_time_seconds / 60).toFixed(1)} phút`
                            : "-"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          ) : (
            <section className="card workout-empty">
              <h2 className="workout-empty-title">
                {DAY_LABELS[selectedDay] || selectedDay} — Ngày nghỉ phục hồi
              </h2>
              <p className="workout-empty-desc">
                Không có buổi tập nào được xếp vào ngày này. Hãy tận dụng thời
                gian để nghỉ ngơi, ngủ đủ giấc và giữ chế độ dinh dưỡng theo mục
                tiêu.
              </p>
            </section>
          )}
        </>
      )}

      <ExerciseDetailModal
        isOpen={modalOpen}
        exercise={modalExercise}
        loading={modalLoading}
        error={modalError}
        onClose={handleCloseModal}
      />
    </div>
  );
}
