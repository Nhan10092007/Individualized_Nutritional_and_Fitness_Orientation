import { NavLink } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Tổng quan" },
  { to: "/workout", label: "Lịch tập luyện" },
  { to: "/nutrition", label: "Dinh dưỡng" },
  { to: "/progress", label: "Tiến độ" },
  { to: "/profile", label: "Hồ sơ cá nhân" },
  { to: "/onboarding", label: "Thông tin khảo sát" },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              isActive ? "sidebar-link active" : "sidebar-link"
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
