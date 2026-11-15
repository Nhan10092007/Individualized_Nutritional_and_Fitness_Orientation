import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../../context/useAuth";

export default function ProtectedRoute({ requireOnboarded = false }) {
  const { isAuthenticated, loading, user } = useAuth();
  const location = useLocation();

  if (loading) {
    return <div className="loading-screen">Đang tải dữ liệu...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requireOnboarded && !user?.is_onboarded) {
    return <Navigate to="/onboarding" replace />;
  }

  return <Outlet />;
}
