import { Activity, LogOut } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/useAuth";

function getInitials(fullName) {
  if (!fullName) return "FL";
  const parts = fullName.trim().split(/\s+/);
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <header className="navbar">
      <div className="navbar-brand">
        <span className="navbar-logo-mark" aria-hidden="true">
          <Activity size={18} strokeWidth={2.4} />
        </span>
        <span>FiLan</span>
        <span className="navbar-brand-sub">Fitness &amp; Nutrition</span>
      </div>

      <div className="navbar-user">
        {user && (
          <>
            <div className="navbar-user-info">
              <div className="navbar-user-name">{user.full_name}</div>
              <div className="navbar-user-email">{user.email}</div>
            </div>
            <div className="navbar-avatar" aria-hidden="true">
              {getInitials(user.full_name)}
            </div>
          </>
        )}
        <button type="button" className="btn btn-secondary" onClick={handleLogout}>
          <LogOut size={15} />
          <span>Đăng xuất</span>
        </button>
      </div>
    </header>
  );
}
