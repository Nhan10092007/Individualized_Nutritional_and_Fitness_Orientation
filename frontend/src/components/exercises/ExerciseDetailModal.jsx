import { useEffect } from "react";
import {
  CONDITION_LABELS,
  INTENSITY_LABELS,
  MUSCLE_LABELS,
} from "../../constants/exerciseLabels";

export default function ExerciseDetailModal({
  isOpen,
  exercise,
  loading = false,
  error = "",
  userWeightKg = 65,
  onClose,
}) {
  useEffect(() => {
    if (!isOpen) return undefined;
    function onKeyDown(e) {
      if (e.key === "Escape") {
        onClose();
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const estCal30Min = exercise?.met_value
    ? Math.round(((exercise.met_value * 3.5 * userWeightKg) / 200) * 30)
    : null;

  return (
    <div
      className="exercises-modal-backdrop"
      role="dialog"
      aria-modal="true"
      aria-labelledby="exercise-detail-title"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="card exercises-modal-card">
        <div className="workout-session-header">
          <div>
            <h2 id="exercise-detail-title" className="workout-session-title">
              {exercise ? exercise.name_en : "Chi tiết bài tập"}
            </h2>
            {exercise?.name_vi && (
              <p className="page-description" style={{ margin: 0 }}>
                {exercise.name_vi}
              </p>
            )}
          </div>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onClose}
          >
            Đóng
          </button>
        </div>

        {loading ? (
          <p className="page-description" style={{ margin: 0 }}>
            Đang tải thông tin bài tập...
          </p>
        ) : error ? (
          <div className="alert alert-error" style={{ margin: 0 }}>
            {error}
          </div>
        ) : exercise ? (
          <>
            <div className="exercises-detail-metrics">
              <div className="metric-box">
                <div className="metric-label">Nhóm cơ chính</div>
                <div className="metric-value" style={{ fontSize: 16 }}>
                  {exercise.target_muscle
                    ? MUSCLE_LABELS[exercise.target_muscle] ||
                      exercise.target_muscle
                    : "Toàn thân / Cardio"}
                </div>
              </div>

              <div className="metric-box">
                <div className="metric-label">Dụng cụ tập</div>
                <div className="metric-value" style={{ fontSize: 15 }}>
                  {exercise.equipment || "Không yêu cầu dụng cụ"}
                </div>
              </div>

              <div className="metric-box">
                <div className="metric-label">Cường độ</div>
                <div className="metric-value" style={{ fontSize: 16 }}>
                  {INTENSITY_LABELS[exercise.intensity_level] ||
                    exercise.intensity_level}
                </div>
              </div>

              <div className="metric-box">
                <div className="metric-label">Chỉ số MET</div>
                <div className="metric-value" style={{ fontSize: 16 }}>
                  {exercise.met_value}
                </div>
                {estCal30Min != null && (
                  <div className="metric-sub">
                    ~{estCal30Min} kcal / 30 phút ({userWeightKg} kg)
                  </div>
                )}
              </div>
            </div>

            {exercise.image && (
              <div className="exercises-media-wrap">
                <img
                  src={exercise.image}
                  alt={exercise.name_en}
                  className="exercises-media-img"
                />
              </div>
            )}

            {exercise.video_url && (
              <div className="exercises-detail-section">
                <h3 className="exercises-detail-heading">Video hướng dẫn</h3>
                {/\.(mp4|webm|ogg)(\?.*)?$/i.test(exercise.video_url) ? (
                  <div className="exercises-media-wrap">
                    <video
                      src={exercise.video_url}
                      controls
                      className="exercises-media-video"
                    />
                  </div>
                ) : (
                  <div>
                    <a
                      href={exercise.video_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-secondary"
                    >
                      Xem video hướng dẫn
                    </a>
                  </div>
                )}
              </div>
            )}

            <div className="exercises-detail-section">
              <h3 className="exercises-detail-heading">Nhóm cơ phụ tham gia</h3>
              {exercise.secondary_muscle?.length > 0 ? (
                <div className="tag-list">
                  {exercise.secondary_muscle.map((m) => (
                    <span key={m} className="badge">
                      {MUSCLE_LABELS[m] || m}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="page-description" style={{ margin: 0 }}>
                  Không có dữ liệu nhóm cơ phụ riêng.
                </p>
              )}
            </div>

            <div className="exercises-detail-section">
              <h3 className="exercises-detail-heading">
                Mô tả &amp; Lưu ý kỹ thuật
              </h3>
              <p className="exercises-detail-text">
                {exercise.description || "Chưa có mô tả chi tiết."}
              </p>
            </div>

            <div className="exercises-detail-section">
              <h3 className="exercises-detail-heading">
                Hướng dẫn thực hiện từng bước
              </h3>
              {exercise.instructions?.length > 0 ? (
                <ol className="exercises-steps-list">
                  {exercise.instructions.map((step, index) => (
                    <li key={index} className="exercises-step-item">
                      {step}
                    </li>
                  ))}
                </ol>
              ) : (
                <p className="page-description" style={{ margin: 0 }}>
                  Chưa có hướng dẫn từng bước cho bài tập này.
                </p>
              )}
            </div>

            <div className="exercises-detail-section">
              <h3 className="exercises-detail-heading">
                Cảnh báo &amp; Chống chỉ định y khoa
              </h3>
              {exercise.banned_for?.length > 0 ? (
                <div className="alert alert-warning" style={{ margin: 0 }}>
                  <strong>Hạn chế với:</strong>{" "}
                  {exercise.banned_for
                    .map((c) => CONDITION_LABELS[c] || c)
                    .join(", ")}
                  {exercise.clinical_reasons && (
                    <div style={{ marginTop: 6 }}>
                      <strong>Lý do y khoa:</strong>{" "}
                      {exercise.clinical_reasons}
                    </div>
                  )}
                </div>
              ) : (
                <p className="page-description" style={{ margin: 0 }}>
                  Không ghi nhận chống chỉ định đặc biệt với nhóm bệnh lý hiện
                  tại.
                </p>
              )}
            </div>
          </>
        ) : (
          <p className="page-description" style={{ margin: 0 }}>
            Không tìm thấy thông tin bài tập.
          </p>
        )}
      </div>
    </div>
  );
}
