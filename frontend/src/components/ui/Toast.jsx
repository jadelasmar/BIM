import { createContext, useCallback, useContext, useMemo, useRef, useState } from "react";
import Icon from "../common/Icon";
import { X } from "../../constants/icons";

const ToastContext = createContext(null);

const TOAST_DISMISS_MS = 1500;
const TOAST_FADE_MS = 300;

const TONE_STYLES = {
  success: {
    border: "border-[rgb(var(--bim-green-rgb)/50%)]",
    text: "text-[var(--tone-green-text)]",
    icon: "check-circle-2"
  },
  error: {
    border: "border-[rgb(var(--bim-red-rgb)/60%)]",
    text: "text-[var(--tone-red-text)]",
    icon: "triangle-alert"
  }
};

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const nextId = useRef(0);

  const removeToast = useCallback((id) => {
    setToasts((current) => current.filter((toast) => toast.id !== id));
  }, []);

  const dismissToast = useCallback(
    (id) => {
      setToasts((current) =>
        current.map((toast) => (toast.id === id ? { ...toast, leaving: true } : toast))
      );
      setTimeout(() => removeToast(id), TOAST_FADE_MS);
    },
    [removeToast]
  );

  const showToast = useCallback(
    (tone, message) => {
      if (!message) return null;
      const id = ++nextId.current;
      setToasts((current) => [
        ...current.filter((toast) => toast.tone !== tone),
        { id, tone, message, leaving: false }
      ]);
      setTimeout(() => dismissToast(id), TOAST_DISMISS_MS);
      return id;
    },
    [dismissToast]
  );

  const value = useMemo(
    () => ({
      showSuccess: (message) => showToast("success", message),
      showError: (message) => showToast("error", message),
      dismissToast
    }),
    [showToast, dismissToast]
  );

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="pointer-events-none fixed inset-x-0 top-4 z-[60] flex flex-col items-center gap-2 px-4">
        {toasts.map((toast) => {
          const tone = TONE_STYLES[toast.tone] || TONE_STYLES.error;
          return (
            <div
              key={toast.id}
              role={toast.tone === "error" ? "alert" : "status"}
              className={`pointer-events-auto flex w-full max-w-md items-start gap-3 rounded-lg border ${tone.border} bg-nexus-panel px-4 py-3 text-sm font-semibold shadow-[var(--bim-card-shadow-hover)] ${tone.text} transition-opacity duration-300 ease-out ${toast.leaving ? "opacity-0" : "opacity-100"}`}
            >
              <Icon name={tone.icon} className="mt-0.5 h-4 w-4 shrink-0" />
              <span className="flex-1">{toast.message}</span>
              <button
                type="button"
                onClick={() => dismissToast(toast.id)}
                className="shrink-0 text-current opacity-70 hover:opacity-100"
                aria-label="Dismiss notification"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
}
