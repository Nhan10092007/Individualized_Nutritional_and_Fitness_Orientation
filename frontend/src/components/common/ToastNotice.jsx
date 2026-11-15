import { useEffect } from "react";

export default function ToastNotice({ message, onClose, durationMs = 3000 }) {
  useEffect(() => {
    if (!message) return undefined;
    const timer = setTimeout(() => {
      onClose?.();
    }, durationMs);
    return () => clearTimeout(timer);
  }, [message, durationMs, onClose]);

  if (!message) return null;

  return (
    <div className="toast-notice" role="status" aria-live="polite">
      <span>{message}</span>
      <button
        type="button"
        className="toast-close-btn"
        onClick={onClose}
        aria-label="Đóng thông báo"
      >
        ×
      </button>
    </div>
  );
}
