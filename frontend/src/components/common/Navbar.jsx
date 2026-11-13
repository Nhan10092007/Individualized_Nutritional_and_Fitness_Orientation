import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/useAuth";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <header className="navbar">
      <div className="navbar-brand">FiLan</div>

      <div className="navbar-user">
        {user && (
          <div className="navbar-user-info">
            <div className="navbar-user-name">{user.full_name}</div>
            <div className="navbar-user-email">{user.email}</div>
          </div>
        )}
        <button type="button" className="btn btn-secondary" onClick={handleLogout}>
          Đăng xuất
        </button>
      </div>
    </header>
  );
}
