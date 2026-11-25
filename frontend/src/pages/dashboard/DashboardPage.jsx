import { CalendarDays, Coffee, Flame, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import heroSlide1 from "../../assets/pullups_man_workout_121789_1600x900.jpg";
import heroSlide2 from "../../assets/gym-couple-1600x900.jpg";
import heroSlide3 from "../../assets/kai-greene-g0-1600x900.jpg";
import { useAuth } from "../../context/useAuth";

const HERO_SLIDES = [
  {
    src: heroSlide1,
    alt: "Không gian tập luyện thể hình",
    eyebrow: "Sức mạnh & Kỷ luật",
    tagline: "Kỷ luật tạo nên bứt phá",
    caption:
      "Từng hiệp tập chuẩn kỹ thuật giúp bạn tiến gần hơn tới mục tiêu thể chất mỗi ngày.",
  },
  {
    src: heroSlide2,
    alt: "Rèn luyện sức khỏe và thể lực",
    eyebrow: "Bền bỉ mỗi ngày",
    tagline: "Tập luyện bền bỉ mỗi ngày",
    caption:
      "Duy trì nhịp vận động đều đặn để nâng cao sức bền, vóc dáng và tinh thần tích cực.",
  },
  {
    src: heroSlide3,
    alt: "Lối sống năng động và dinh dưỡng cân bằng",
    eyebrow: "Khoa học & Cân bằng",
    tagline: "Cân bằng tập luyện & dinh dưỡng",
    caption:
      "Kết hợp lịch tập cá nhân hóa cùng thực đơn chuẩn calo để tối ưu hiệu quả dài lâu.",
  },
];

const WORKFLOW_STEPS = [
  {
    step: "01",
    title: "Thiết lập hồ sơ",
    desc: "Cung cấp chiều cao, cân nặng, độ tuổi, mục tiêu thể chất, lịch rảnh trong tuần, ngân sách và bệnh nền nếu có.",
  },
  {
    step: "02",
    title: "Phân tích & Sàng lọc",
    desc: "Hệ thống tự động tính BMR, TDEE, BMI, nhu cầu Calo/Macro mục tiêu và loại trừ các bài tập có rủi ro y khoa.",
  },
  {
    step: "03",
    title: "Lập lịch tự động",
    desc: "Sinh lịch tập phân chia nhóm cơ khoa học cùng thực đơn 7 ngày cân đối dinh dưỡng trong mức chi tiêu.",
  },
];

const FEATURE_CARDS = [
  {
    tag: "01 · Tập luyện",
    title: "Lịch tập luyện cá nhân hóa",
    description:
      "Tự động lựa chọn mô hình chia lịch Full Body, Upper/Lower hoặc Push/Pull/Legs theo số ngày rảnh trong tuần và trình độ của bạn.",
    highlights: [
      "Tính toán số hiệp, số lần lặp và thời gian nghỉ giữa hiệp/giữa bài",
      "Lọc an toàn theo bệnh nền và xem hướng dẫn bài tập ngay trên lịch",
    ],
    to: "/workout",
    cta: "Mở Lịch tập luyện →",
  },
  {
    tag: "02 · Tra cứu",
    title: "Kho lưu trữ bài tập",
    description:
      "Thư viện bài tập hỗ trợ tìm kiếm nhanh theo tên, dụng cụ, nhóm cơ chính và mức độ cường độ vận động.",
    highlights: [
      "Xem thông tin bài tập, cường độ vận động, dụng cụ và nhóm cơ phụ",
      "Hướng dẫn thực hiện từng bước cùng lưu ý chống chỉ định y khoa",
    ],
    to: "/exercises",
    cta: "Khám phá Kho bài tập →",
  },
  {
    tag: "03 · Dinh dưỡng",
    title: "Thực đơn dinh dưỡng 7 ngày",
    description:
      "Tự động phân bổ 3 bữa Sáng · Trưa · Tối cho cả tuần dựa trên mức Calo và tỷ lệ Đạm · Tinh bột · Chất béo mục tiêu.",
    highlights: [
      "Kiểm soát chi phí trung bình ngày nằm trong phạm vi ngân sách thiết lập",
      "Theo dõi chi tiết khẩu phần, khối lượng món ăn và tổng quan từng ngày",
    ],
    to: "/nutrition",
    cta: "Xem Thực đơn dinh dưỡng →",
  },
  {
    tag: "04 · Cá nhân hóa",
    title: "Hồ sơ & Chỉ số cơ thể",
    description:
      "Trung tâm lưu trữ toàn bộ thông số nhân trắc học, mục tiêu tăng cơ/giảm mỡ/duy trì và các ràng buộc sức khỏe cá nhân.",
    highlights: [
      "Cập nhật nhanh các chỉ số BMR, TDEE, BMI và cân nặng lý tưởng",
      "Điều chỉnh lịch rảnh hoặc ngân sách để tái tạo lộ trình mới tức thì",
    ],
    to: "/profile",
    cta: "Quản lý Hồ sơ cá nhân →",
  },
];

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
  const [activeSlide, setActiveSlide] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setActiveSlide((prev) => (prev + 1) % HERO_SLIDES.length);
    }, 4500);
    return () => clearInterval(timer);
  }, []);

  const targets = user?.plan_targets || {};
  const availableDays = Array.isArray(targets.available_days)
    ? targets.available_days
    : [];
  const durationMins = Number(targets.session_duration_mins || 0);

  const now = new Date();
  const currentSlide = HERO_SLIDES[activeSlide];

  return (
    <div className="dash-stack">
      {/* Hero Banner with Auto-cycling Background Slideshow */}
      <section className="dash-hero dash-hero-banner">
        <div className="dash-hero-bg" aria-hidden="true">
          {HERO_SLIDES.map((slide, index) => (
            <img
              key={slide.src}
              src={slide.src}
              alt={slide.alt}
              className={
                index === activeSlide
                  ? "dash-hero-slide active"
                  : "dash-hero-slide"
              }
            />
          ))}
          <div className="dash-hero-overlay" />
        </div>

        <div className="dash-hero-top">
          <div className="dash-hero-badges">
            <span className="badge">
              <CalendarDays size={15} />
              <span>{formatTodayVi(now)}</span>
            </span>
            {availableDays.length > 0 ? (
              <span className="badge">
                <Flame size={15} />
                <span>
                  Lịch tập: {availableDays.length} buổi/tuần ({durationMins || 45} phút/buổi)
                </span>
              </span>
            ) : (
              <span className="badge">
                <Coffee size={15} />
                <span>Chưa thiết lập lịch tập</span>
              </span>
            )}
          </div>

          <span className="badge dash-hero-slide-badge">
            <Sparkles size={15} />
            <span>{currentSlide.eyebrow}</span>
          </span>
        </div>

        <div className="dash-hero-bottom">
          <div className="dash-hero-copy">
            <h1 className="dash-hero-title">
              Xin chào, {user?.full_name || "bạn"}!
            </h1>
            <div key={activeSlide} className="dash-hero-slide-copy">
              <p className="dash-hero-tagline">{currentSlide.tagline}</p>
              <p className="dash-hero-caption">{currentSlide.caption}</p>
            </div>
          </div>

          <div className="dash-hero-dots" aria-label="Chuyển ảnh nền">
            {HERO_SLIDES.map((slide, index) => (
              <button
                key={slide.src}
                type="button"
                onClick={() => setActiveSlide(index)}
                className={
                  index === activeSlide
                    ? "dash-hero-dot active"
                    : "dash-hero-dot"
                }
                aria-label={`Ảnh nền ${index + 1}`}
              />
            ))}
          </div>
        </div>
      </section>

      {/* Web Introduction */}
      <section className="dash-card">
        <div className="dash-intro-header">
          <span className="dash-section-eyebrow">Giới thiệu nền tảng</span>
          <h2 className="dash-intro-title">
            Hệ thống lập kế hoạch tập luyện &amp; dinh dưỡng cá nhân hóa
          </h2>
          <p className="dash-intro-desc">
            Ứng dụng giúp bạn xây dựng lộ trình rèn luyện sức khỏe khoa học và
            đồng bộ trên một nền tảng duy nhất: từ phân tích chỉ số cơ thể,
            sàng lọc bài tập an toàn theo bệnh lý nền đến tự động lập lịch tập
            theo tuần và thực đơn ăn uống phù hợp ngân sách hằng ngày.
          </p>
        </div>

        <div className="dash-workflow-grid">
          {WORKFLOW_STEPS.map((item) => (
            <div key={item.step} className="dash-workflow-step">
              <span className="dash-step-num">{item.step}</span>
              <h3 className="dash-step-title">{item.title}</h3>
              <p className="dash-step-desc">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Main Features */}
      <section className="dash-features-section">
        <div className="dash-section-heading">
          <span className="dash-section-eyebrow">Các chức năng chính</span>
          <h2 className="dash-card-title">Khám phá công cụ trên hệ thống</h2>
        </div>

        <div className="dash-features-grid">
          {FEATURE_CARDS.map((feature) => (
            <article key={feature.to} className="dash-card dash-feature-card">
              <span className="dash-feature-tag">{feature.tag}</span>
              <h3 className="dash-feature-title">{feature.title}</h3>
              <p className="dash-feature-desc">{feature.description}</p>
              <ul className="dash-feature-list">
                {feature.highlights.map((line) => (
                  <li key={line}>{line}</li>
                ))}
              </ul>
              <div className="dash-feature-footer">
                <Link to={feature.to} className="dash-feature-link">
                  {feature.cta}
                </Link>
              </div>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
