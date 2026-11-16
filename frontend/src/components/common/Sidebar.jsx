import { useEffect, useRef, useState } from "react";
import {
  BookOpen,
  ChevronLeft,
  ChevronRight,
  Dumbbell,
  LayoutDashboard,
  TrendingUp,
  User,
  Utensils,
} from "lucide-react";
import { NavLink, useLocation } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Tổng quan", icon: LayoutDashboard },
  { to: "/workout", label: "Lịch tập luyện", icon: Dumbbell },
  { to: "/exercises", label: "Kho bài tập", icon: BookOpen },
  { to: "/nutrition", label: "Dinh dưỡng", icon: Utensils },
  { to: "/progress", label: "Tiến độ", icon: TrendingUp },
  { to: "/profile", label: "Hồ sơ cá nhân", icon: User },
];

export default function Sidebar() {
  const [expanded, setExpanded] = useState(false);
  const location = useLocation();
  const navRef = useRef(null);
  const itemRefs = useRef([]);
  const [indicatorStyle, setIndicatorStyle] = useState({
    top: 0,
    height: 40,
    opacity: 0,
  });

  const activeIndex = NAV_ITEMS.findIndex((item) =>
    location.pathname.startsWith(item.to)
  );

  useEffect(() => {
    const frameId = requestAnimationFrame(() => {
      const activeEl = itemRefs.current[activeIndex];
      if (activeEl) {
        setIndicatorStyle({
          top: activeEl.offsetTop,
          height: activeEl.offsetHeight,
          opacity: 1,
        });
      } else {
        setIndicatorStyle((prev) => ({ ...prev, opacity: 0 }));
      }
    });
    return () => cancelAnimationFrame(frameId);
  }, [activeIndex, expanded]);

  function handleAsideClick(e) {
    if (!expanded && !e.target.closest("a, button")) {
      setExpanded(true);
    }
  }

  return (
    <aside
      className={expanded ? "sidebar expanded" : "sidebar collapsed"}
      onClick={handleAsideClick}
    >
      <div className="sidebar-header">
        {expanded && <span className="sidebar-section-label">Điều hướng</span>}
        <button
          type="button"
          className="sidebar-toggle"
          onClick={() => setExpanded((prev) => !prev)}
          aria-expanded={expanded}
          aria-label={expanded ? "Thu gọn thanh điều hướng" : "Mở rộng thanh điều hướng"}
          title={expanded ? "Thu gọn" : "Mở rộng"}
        >
          {expanded ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
        </button>
      </div>

      <nav className="sidebar-nav" ref={navRef}>
        <span
          className="sidebar-active-indicator"
          aria-hidden="true"
          style={{
            transform: `translateY(${indicatorStyle.top}px)`,
            height: `${indicatorStyle.height}px`,
            opacity: indicatorStyle.opacity,
          }}
        />
        {NAV_ITEMS.map((item, idx) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              ref={(el) => {
                itemRefs.current[idx] = el;
              }}
              to={item.to}
              title={!expanded ? item.label : undefined}
              aria-label={item.label}
              style={{ animationDelay: `${idx * 0.08}s` }}
              className={({ isActive }) =>
                isActive ? "sidebar-link active" : "sidebar-link"
              }
            >
              <Icon size={18} className="sidebar-link-icon" />
              <span className="sidebar-link-text">{item.label}</span>
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
}
