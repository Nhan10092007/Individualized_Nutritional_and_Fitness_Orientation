import {
  Dumbbell,
  LayoutDashboard,
  TrendingUp,
  User,
  Utensils,
} from "lucide-react";
import { NavLink } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Tổng quan", icon: LayoutDashboard },
  { to: "/workout", label: "Lịch tập luyện", icon: Dumbbell },
  { to: "/nutrition", label: "Dinh dưỡng", icon: Utensils },
  { to: "/progress", label: "Tiến độ", icon: TrendingUp },
  { to: "/profile", label: "Hồ sơ cá nhân", icon: User },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-section-label">Điều hướng</div>
      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                isActive ? "sidebar-link active" : "sidebar-link"
              }
            >
              <Icon size={17} className="sidebar-link-icon" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
}
