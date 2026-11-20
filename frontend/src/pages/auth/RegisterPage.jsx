import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/useAuth";
import { getApiErrorMessage } from "../../services/api";

export default function RegisterPage() {
  const { isAuthenticated, user, loading, register } = useAuth();
  const navigate = useNavigate();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

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

    const trimmedName = fullName.trim();
    const trimmedEmail = email.trim();

    if (trimmedName.length < 3 || trimmedName.length > 100) {
      setError("Họ và tên phải có độ dài từ 3 đến 100 ký tự.");
      return;
    }

    if (!trimmedEmail) {
      setError("Vui lòng nhập email hợp lệ.");
      return;
    }

    if (password.length < 8 || password.length > 64) {
      setError("Mật khẩu phải có độ dài từ 8 đến 64 ký tự.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Mật khẩu xác nhận không khớp.");
      return;
    }

    setSubmitting(true);
    try {
      await register(trimmedEmail, password, trimmedName);
      navigate("/login", {
        replace: true,
        state: {
          email: trimmedEmail,
          message: "Đăng ký tài khoản thành công. Vui lòng đăng nhập để tiếp tục.",
        },
      });
    } catch (err) {
      setError(getApiErrorMessage(err, "Đăng ký thất bại. Vui lòng thử lại."));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-brand">FiLan</div>
        <h1 className="auth-title">Đăng ký tài khoản</h1>
        <p className="auth-subtitle">
          Tạo tài khoản mới để thiết lập chỉ số cơ thể và kế hoạch cá nhân hóa.
        </p>

        {error && <div className="alert alert-error">{error}</div>}

        <form className="form-stack" onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="register-name">
              Họ và tên
            </label>
            <input
              id="register-name"
              type="text"
              className="form-input"
              placeholder="Nguyễn Văn A"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              minLength={3}
              maxLength={100}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="register-email">
              Email
            </label>
            <input
              id="register-email"
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
            <label className="form-label" htmlFor="register-password">
              Mật khẩu
            </label>
            <input
              id="register-password"
              type="password"
              className="form-input"
              placeholder="Ít nhất 8 ký tự"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              minLength={8}
              maxLength={64}
              autoComplete="new-password"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="register-confirm">
              Xác nhận mật khẩu
            </label>
            <input
              id="register-confirm"
              type="password"
              className="form-input"
              placeholder="Nhập lại mật khẩu"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              autoComplete="new-password"
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-full"
            disabled={submitting}
          >
            {submitting ? "Đang tạo tài khoản..." : "Đăng ký"}
          </button>
        </form>

        <div className="auth-footer">
          Đã có tài khoản? <Link to="/login">Đăng nhập</Link>
        </div>
      </div>
    </div>
  );
}
