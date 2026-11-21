import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, CheckCircle2, Search } from "lucide-react";
import {
  INTENSITY_LABELS,
  MUSCLE_LABELS,
} from "../../constants/exerciseLabels";
import { getApiErrorMessage } from "../../services/api";
import { exerciseService } from "../../services/exerciseService";

function getIntensityPreviewWarning(fitnessLevel, intensityLevel) {
  const level = String(fitnessLevel || "beginner").toLowerCase();
  const intensity = String(intensityLevel || "Moderate").toLowerCase();

  if (level === "beginner" && intensity === "vigorous") {
    return {
      type: "danger",
      text: "Cảnh báo: Cường độ cao đối với người mới",
    };
  }
  if ((level === "experienced" || level === "advanced") && intensity === "light") {
    return {
      type: "easy",
      text: "Cường độ nhẹ so với trình độ hiện tại",
    };
  }
  return null;
}

export default function SwapExerciseModal({
  isOpen,
  targetExercise,
  sessionExerciseIds = [],
  fitnessLevel = "beginner",
  swapping = false,
  onSelectExercise,
  onClose,
}) {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    if (!isOpen) return undefined;
    function onKeyDown(e) {
      if (e.key === "Escape" && !swapping) {
        onClose();
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [isOpen, swapping, onClose]);

  useEffect(() => {
    if (!isOpen || !targetExercise?.target_muscle) return undefined;
    let isMounted = true;

    async function loadCandidates() {
      setLoading(true);
      setError("");
      setSearchTerm("");
      try {
        const data = await exerciseService.getExercises({
          target_muscle: targetExercise.target_muscle,
          safe_only: true,
        });
        if (!isMounted) return;
        setCandidates(Array.isArray(data?.exercises) ? data.exercises : []);
      } catch (err) {
        if (isMounted) {
          setError(
            getApiErrorMessage(err, "Không thể tải danh sách bài tập thay thế.")
          );
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadCandidates();
    return () => {
      isMounted = false;
    };
  }, [isOpen, targetExercise]);

  const excludedIdSet = useMemo(
    () => new Set(sessionExerciseIds.map((id) => String(id))),
    [sessionExerciseIds]
  );

  const filteredCandidates = useMemo(() => {
    const q = searchTerm.trim().toLowerCase();
    return candidates.filter((ex) => {
      if (excludedIdSet.has(String(ex.id))) return false;
      if (!q) return true;
      return (
        String(ex.name_vi || "").toLowerCase().includes(q) ||
        String(ex.name_en || "").toLowerCase().includes(q) ||
        String(ex.equipment || "").toLowerCase().includes(q)
      );
    });
  }, [candidates, excludedIdSet, searchTerm]);

  if (!isOpen || !targetExercise) return null;

  const muscleLabel =
    MUSCLE_LABELS[targetExercise.target_muscle] || targetExercise.target_muscle;

  return (
    <div
      className="exercises-modal-backdrop"
      role="dialog"
      aria-modal="true"
      aria-labelledby="swap-exercise-title"
      onClick={(e) => {
        if (e.target === e.currentTarget && !swapping) onClose();
      }}
    >
      <div className="card exercises-modal-card swap-modal-card">
        <div className="workout-session-header">
          <div>
            <h2 id="swap-exercise-title" className="workout-session-title">
              Đổi bài tập nhóm cơ {muscleLabel}
            </h2>
            <p className="page-description" style={{ margin: "4px 0 0" }}>
              Đang thay thế: <strong>{targetExercise.name}</strong> (chỉ hiển thị
              bài cùng nhóm cơ chính &amp; an toàn với bệnh nền)
            </p>
          </div>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onClose}
            disabled={swapping}
          >
            Đóng
          </button>
        </div>

        <div className="swap-modal-search">
          <Search size={16} aria-hidden="true" />
          <input
            type="text"
            className="input"
            placeholder="Tìm theo tên bài tập hoặc dụng cụ..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            disabled={loading || swapping}
          />
        </div>

        {loading ? (
          <p className="page-description" style={{ margin: 0 }}>
            Đang tải danh sách bài tập thay thế...
          </p>
        ) : error ? (
          <div className="alert alert-error" style={{ margin: 0 }}>
            {error}
          </div>
        ) : filteredCandidates.length === 0 ? (
          <div className="swap-modal-empty">
            Không còn bài tập thay thế nào khác cho nhóm cơ{" "}
            <strong>{muscleLabel}</strong> (các bài an toàn khác đều đã có trong
            buổi tập hôm nay).
          </div>
        ) : (
          <div className="swap-modal-list">
            {filteredCandidates.map((ex) => {
              const warning = getIntensityPreviewWarning(
                fitnessLevel,
                ex.intensity_level
              );
              const intensityBadgeClass =
                ex.intensity_level === "Vigorous"
                  ? "badge badge-danger"
                  : ex.intensity_level === "Light"
                  ? "badge badge-success"
                  : "badge";

              return (
                <div key={ex.id} className="swap-modal-item">
                  <div className="swap-modal-item-info">
                    <div className="swap-modal-item-head">
                      <strong className="swap-modal-item-name">
                        {ex.name_vi || ex.name_en}
                      </strong>
                      <span className={intensityBadgeClass}>
                        {INTENSITY_LABELS[ex.intensity_level] ||
                          ex.intensity_level}
                      </span>
                    </div>
                    <div className="swap-modal-item-sub">
                      <span>{ex.name_en}</span>
                      {ex.equipment && <span>· Dụng cụ: {ex.equipment}</span>}
                    </div>
                    {warning && (
                      <div
                        className={`swap-modal-warning ${
                          warning.type === "danger"
                            ? "workout-intensity-alert-danger"
                            : "workout-intensity-alert-easy"
                        }`}
                      >
                        {warning.type === "danger" ? (
                          <AlertTriangle size={14} aria-hidden="true" />
                        ) : (
                          <CheckCircle2 size={14} aria-hidden="true" />
                        )}
                        <span>{warning.text}</span>
                      </div>
                    )}
                  </div>

                  <button
                    type="button"
                    className="btn btn-primary swap-modal-choose-btn"
                    disabled={swapping}
                    onClick={() => onSelectExercise(ex.id)}
                  >
                    {swapping ? "Đang đổi..." : "Chọn bài này"}
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
