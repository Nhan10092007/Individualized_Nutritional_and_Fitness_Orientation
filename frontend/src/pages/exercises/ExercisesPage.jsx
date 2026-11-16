import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import ExerciseDetailModal from "../../components/exercises/ExerciseDetailModal";
import {
  INTENSITY_LABELS,
  MUSCLE_LABELS,
} from "../../constants/exerciseLabels";
import { useAuth } from "../../context/useAuth";
import { getApiErrorMessage } from "../../services/api";
import { exerciseService } from "../../services/exerciseService";

const RAW_GH_PREFIX =
  "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/";
const JSDELIVR_PREFIX =
  "https://cdn.jsdelivr.net/gh/yuhonas/free-exercise-db@main/";

function getExerciseImageUrls(src) {
  if (!src) return [];
  if (src.startsWith(RAW_GH_PREFIX)) {
    return [src.replace(RAW_GH_PREFIX, JSDELIVR_PREFIX), src];
  }
  return [src];
}

function ExerciseThumbnailImg({ urls, alt }) {
  const [urlIndex, setUrlIndex] = useState(0);
  const currentSrc = urls[urlIndex];

  if (!currentSrc) return null;

  return (
    <div className="exercises-item-thumb-wrap">
      <img
        src={currentSrc}
        alt={alt}
        className="exercises-item-thumb"
        loading="lazy"
        onError={() => setUrlIndex((idx) => idx + 1)}
      />
    </div>
  );
}

function ExerciseThumbnail({ src, alt }) {
  const urls = getExerciseImageUrls(src);
  if (urls.length === 0) return null;
  return <ExerciseThumbnailImg key={src} urls={urls} alt={alt} />;
}

export default function ExercisesPage() {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const requestedId = searchParams.get("id");

  const [exercises, setExercises] = useState([]);
  const [muscles, setMuscles] = useState([]);

  const [searchText, setSearchText] = useState("");
  const [selectedMuscle, setSelectedMuscle] = useState("ALL");
  const [selectedIntensity, setSelectedIntensity] = useState("ALL");
  const [safeOnly, setSafeOnly] = useState(false);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isMounted = true;

    async function fetchExercises() {
      setLoading(true);
      setError("");
      try {
        const data = await exerciseService.getExercises({
          q: searchText.trim() || undefined,
          target_muscle: selectedMuscle !== "ALL" ? selectedMuscle : undefined,
          intensity_level:
            selectedIntensity !== "ALL" ? selectedIntensity : undefined,
          safe_only: safeOnly,
        });
        if (!isMounted) return;

        const list = Array.isArray(data?.exercises) ? data.exercises : [];
        setExercises(list);
        setMuscles(Array.isArray(data?.muscles) ? data.muscles : []);
      } catch (err) {
        if (isMounted) {
          setError(
            getApiErrorMessage(err, "Không thể tải danh sách kho bài tập.")
          );
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    fetchExercises();
    return () => {
      isMounted = false;
    };
  }, [searchText, selectedMuscle, selectedIntensity, safeOnly]);

  const selectedExercise = requestedId
    ? exercises.find((ex) => String(ex.id) === String(requestedId)) || null
    : null;

  function handleSelectExercise(ex) {
    setSearchParams({ id: String(ex.id) });
  }

  function handleCloseDetail() {
    setSearchParams({}, { replace: true });
  }

  function handleResetFilters() {
    setSearchText("");
    setSelectedMuscle("ALL");
    setSelectedIntensity("ALL");
    setSafeOnly(false);
  }

  const hasActiveFilters =
    Boolean(searchText.trim()) ||
    selectedMuscle !== "ALL" ||
    selectedIntensity !== "ALL" ||
    safeOnly;

  const userConditions = Array.isArray(user?.constraints?.medical_conditions)
    ? user.constraints.medical_conditions
    : [];
  const safeCount = exercises.filter((ex) => ex.is_safe_for_user).length;

  return (
    <div className="dash-stack">
      {/* Header / Hero */}
      <section className="dash-hero">
        <div>
          <div className="dash-hero-badges">
            <span className="badge badge-success">
              {exercises.length} bài tập hiển thị
            </span>
            <span className="badge">{muscles.length} nhóm cơ</span>
            {userConditions.length > 0 && (
              <span className="badge badge-warning">
                Lọc y khoa: {safeCount}/{exercises.length} bài an toàn
              </span>
            )}
          </div>
          <h1 className="dash-hero-title">Kho lưu trữ bài tập</h1>
          <p className="dash-hero-desc">
            Tra cứu thông tin bài tập theo nhóm cơ, mức độ vận động, dụng cụ tập
            và cảnh báo chống chỉ định theo hồ sơ sức khỏe.
          </p>
        </div>
      </section>

      {error && <div className="alert alert-error">{error}</div>}

      {/* Left: Search/Filter Panel | Right: Exercises Grid */}
      <section className="exercises-layout">
        <aside className="card exercises-filter-sidebar">
          <div className="exercises-sidebar-header">
            <h2 className="exercises-sidebar-title">Tìm kiếm &amp; Bộ lọc</h2>
            {hasActiveFilters && (
              <button
                type="button"
                className="exercises-reset-btn"
                onClick={handleResetFilters}
              >
                Đặt lại
              </button>
            )}
          </div>

          <div className="exercises-filter-group">
            <label htmlFor="ex-search" className="exercises-filter-label">
              Từ khóa
            </label>
            <input
              id="ex-search"
              type="text"
              className="input"
              placeholder="Tên bài tập, dụng cụ, mô tả..."
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
            />
          </div>

          <div className="exercises-filter-group">
            <label htmlFor="ex-intensity" className="exercises-filter-label">
              Cường độ
            </label>
            <select
              id="ex-intensity"
              className="input"
              value={selectedIntensity}
              onChange={(e) => setSelectedIntensity(e.target.value)}
            >
              <option value="ALL">Tất cả cường độ</option>
              <option value="Light">Nhẹ (Light)</option>
              <option value="Moderate">Trung bình (Moderate)</option>
              <option value="Vigorous">Cao (Vigorous)</option>
            </select>
          </div>

          <div className="exercises-filter-group">
            <span className="exercises-filter-label">Nhóm cơ</span>
            <div className="workout-tabs">
              <button
                type="button"
                className={
                  selectedMuscle === "ALL" ? "workout-tab active" : "workout-tab"
                }
                onClick={() => setSelectedMuscle("ALL")}
              >
                Tất cả nhóm cơ
              </button>
              {muscles.map((muscle) => (
                <button
                  key={muscle}
                  type="button"
                  className={
                    selectedMuscle === muscle
                      ? "workout-tab active"
                      : "workout-tab"
                  }
                  onClick={() => setSelectedMuscle(muscle)}
                >
                  {MUSCLE_LABELS[muscle] || muscle}
                </button>
              ))}
              {userConditions.length > 0 && (
                <button
                  type="button"
                  className={safeOnly ? "workout-tab active" : "workout-tab"}
                  aria-pressed={safeOnly}
                  onClick={() => setSafeOnly((prev) => !prev)}
                >
                  An toàn
                </button>
              )}
            </div>
          </div>
        </aside>

        <div className="exercises-main-col">
          {loading ? (
            <div className="card">
              <p className="page-description">Đang tải kho bài tập...</p>
            </div>
          ) : exercises.length === 0 ? (
            <div className="card workout-empty">
              <h2 className="workout-empty-title">
                Không tìm thấy bài tập phù hợp
              </h2>
              <p className="workout-empty-desc">
                Hãy thử xóa bớt từ khóa tìm kiếm hoặc chọn lại bộ lọc nhóm cơ /
                cường độ.
              </p>
            </div>
          ) : (
            <div className="exercises-grid">
              {exercises.map((ex) => {
                const isSelected = selectedExercise?.id === ex.id;
                return (
                  <button
                    key={ex.id}
                    type="button"
                    onClick={() => handleSelectExercise(ex)}
                    className={[
                      "exercises-item-card",
                      isSelected ? "active" : "",
                    ]
                      .filter(Boolean)
                      .join(" ")}
                  >
                    <ExerciseThumbnail src={ex.image} alt={ex.name_en} />
                    <div className="exercises-item-top">
                      <span className="exercises-item-name">{ex.name_en}</span>
                    </div>
                    <div className="exercises-item-sub">{ex.name_vi}</div>
                    <div className="exercises-item-meta">
                      <span className="badge">
                        {ex.target_muscle
                          ? MUSCLE_LABELS[ex.target_muscle] || ex.target_muscle
                          : ex.category}
                      </span>
                      <span className="badge">
                        {INTENSITY_LABELS[ex.intensity_level] ||
                          ex.intensity_level}
                      </span>
                      {ex.equipment && (
                        <span className="badge">{ex.equipment}</span>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </section>

      {/* Modal Detail View */}
      <ExerciseDetailModal
        isOpen={Boolean(selectedExercise)}
        exercise={selectedExercise}
        onClose={handleCloseDetail}
      />
    </div>
  );
}
