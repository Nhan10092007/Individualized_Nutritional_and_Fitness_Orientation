import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../context/useAuth";
import { getApiErrorMessage } from "../../services/api";
import { workoutService } from "../../services/workoutService";

const DAY_LABELS = {
  Mon: "Thứ 2",
  Tue: "Thứ 3",
  Wed: "Thứ 4",
  Thu: "Thứ 5",
  Fri: "Thứ 6",
  Sat: "Thứ 7",
  Sun: "Chủ nhật",
};

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

const CONDITION_LABELS = {
  knee_osteoarthritis: "Thoái hóa / Đau khớp gối",
  hypertension: "Huyết áp cao",
};

const MUSCLE_LABELS = {
  Chest: "Ngực",
  Back: "Lưng / Xô",
  Shoulders: "Vai",
  "Rear Delts": "Vai sau",
  Biceps: "Tay trước",
  Triceps: "Tay sau",
  Quadriceps: "Đùi trước",
  Hamstrings: "Đùi sau",
  Glutes: "Mông",
  Calves: "Bắp chân",
  Abs: "Bụng",
};

const SPLIT_DESCRIPTIONS = {
  "Full Body": "Toàn thân mỗi buổi, tối ưu phục hồi cho lịch 2-3 ngày/tuần",
  "Upper/Lower": "Luân phiên Thân trên & Thân dưới cho lịch 4 ngày/tuần",
  "Push/Pull/Legs": "Chia nhóm Đẩy - Kéo - Chân cho lịch 5-6 ngày/tuần",
};

export default function WorkoutPage() {
  const { user } = useAuth();

  const [plan, setPlan] = useState(null);
  const [hasPlan, setHasPlan] = useState(false);
  const [createdAt, setCreatedAt] = useState(null);
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
        const data = await workoutService.getWorkoutPlan();
        if (!isMounted) return;
        setHasPlan(Boolean(data?.has_plan && data?.workout_plan));
        setPlan(data?.workout_plan || null);
        setCreatedAt(data?.created_at || null);
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
      setPlan(data?.workout_plan || null);
      setHasPlan(Boolean(data?.workout_plan));
      setCreatedAt(new Date().toISOString());
      setSelectedDay("ALL");
      setSuccessMsg(data?.message || "Đã tạo và lưu lịch tập thành công!");
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

  const visibleSessions =
    selectedDay === "ALL"
      ? weeklySchedule
      : weeklySchedule.filter((s) => s.day === selectedDay);

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
      {successMsg && <div className="alert alert-success">{successMsg}</div>}

      {/* Medical filter notice */}
      {medicalConditions.length > 0 && (
        <div className="alert alert-warning" style={{ marginBottom: 0 }}>
          <strong>Chế độ lọc an toàn y khoa đang bật:</strong> Hệ thống tự động
          loại trừ các bài tập chống chỉ định với{" "}
          {medicalConditions
            .map((c) => CONDITION_LABELS[c] || c)
            .join(", ")}
          .
        </div>
      )}

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

          {/* Day Filter Tabs */}
          <div className="workout-tabs">
            <button
              type="button"
              className={
                selectedDay === "ALL" ? "workout-tab active" : "workout-tab"
              }
              onClick={() => setSelectedDay("ALL")}
            >
              Cả tuần ({weeklySchedule.length} buổi)
            </button>
            {weeklySchedule.map((session, idx) => (
              <button
                key={`${session.day}-${idx}`}
                type="button"
                className={
                  selectedDay === session.day
                    ? "workout-tab active"
                    : "workout-tab"
                }
                onClick={() => setSelectedDay(session.day)}
              >
                {DAY_LABELS[session.day] || session.day} ·{" "}
                {session.exercise_count ?? session.exercises?.length ?? 0} bài
              </button>
            ))}
          </div>

          {/* Session Cards */}
          {visibleSessions.map((session, sIdx) => (
            <section key={`${session.day}-${sIdx}`} className="card">
              <div className="workout-session-header">
                <div>
                  <h2 className="workout-session-title">
                    {DAY_LABELS[session.day] || session.day} —{" "}
                    {session.session_name}
                  </h2>
                  <div className="tag-list" style={{ marginTop: "8px" }}>
                    {(session.target_muscles || []).map((muscle) => (
                      <span key={muscle} className="badge">
                        {MUSCLE_LABELS[muscle] || muscle}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="workout-session-meta">
                  <span className="badge badge-success">
                    {session.actual_duration_mins} / {session.max_allowed_mins}{" "}
                    phút
                  </span>
                  <span className="badge">
                    {session.exercise_count ?? session.exercises?.length ?? 0}{" "}
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
                      <th>Thời gian dự kiến</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(session.exercises || []).map((ex, eIdx) => (
                      <tr key={`${ex.exercise_id}-${eIdx}`}>
                        <td>{eIdx + 1}</td>
                        <td className="workout-ex-name">{ex.name}</td>
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
                        <td>{ex.rest_seconds} giây</td>
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
          ))}
        </>
      )}
    </div>
  );
}
