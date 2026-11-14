import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/useAuth";
import { getApiErrorMessage } from "../../services/api";

export default function LoginPage() {
  const { isAuthenticated, user, loading, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState(location.state?.email || "");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const successMessage = location.state?.message || "";

  if (!loading && isAuthenticated) {
    return (
      <Navigate
        to={user?.is_onboarded ? "/dashboard" : "/onboarding"}
        replace
      />
    );
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (!email.trim() || !password) {
      setError("Vui lòng nhập đầy đủ email và mật khẩu.");
      return;
    }

    setSubmitting(true);
    try {
      const profile = await login(email.trim(), password);
      if (profile?.is_onboarded) {
        navigate("/dashboard", { replace: true });
      } else {
        navigate("/onboarding", { replace: true });
      }
    } catch (err) {
      setError(getApiErrorMessage(err, "Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin."));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-brand">FiLan</div>
        <h1 className="auth-title">Đăng nhập</h1>
        <p className="auth-subtitle">
          Đăng nhập để truy cập lộ trình tập luyện và dinh dưỡng của bạn.
        </p>

        {successMessage && (
          <div className="alert alert-success">{successMessage}</div>
        )}
        {error && <div className="alert alert-error">{error}</div>}

        <form className="form-stack" onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="login-email">
              Email
            </label>
            <input
              id="login-email"
              type="email"
              className="form-input"
              placeholder="name@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="login-password">
              Mật khẩu
            </label>
            <input
              id="login-password"
              type="password"
              className="form-input"
              placeholder="Nhập mật khẩu"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-full"
            disabled={submitting}
          >
            {submitting ? "Đang đăng nhập..." : "Đăng nhập"}
          </button>
        </form>

        <div className="auth-footer">
          Chưa có tài khoản? <Link to="/register">Đăng ký ngay</Link>
        </div>
      </div>
    </div>
  );
}
