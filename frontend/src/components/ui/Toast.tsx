import { createContext, useContext, useState, useCallback } from 'react'
import type { ReactNode } from 'react'

type ToastVariant = 'error' | 'success' | 'info'

interface Toast {
  id: string
  message: string
  variant: ToastVariant
}

interface ToastContextValue {
  showToast: (message: string, variant?: ToastVariant) => void
  hideToast: (id: string) => void
}

const ToastContext = createContext<ToastContextValue | undefined>(undefined)

export function useToast() {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within ToastProvider')
  }
  return context
}

interface ToastProviderProps {
  children: ReactNode
}

export function ToastProvider({ children }: ToastProviderProps) {
  const [toasts, setToasts] = useState<Toast[]>([])

  const showToast = useCallback((message: string, variant: ToastVariant = 'info') => {
    const id = `toast-${Date.now()}-${Math.random()}`
    const toast: Toast = { id, message, variant }

    setToasts((prev) => [...prev, toast])

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      hideToast(id)
    }, 5000)
  }, [])

  const hideToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const getVariantStyles = (variant: ToastVariant) => {
    switch (variant) {
      case 'error':
        return 'bg-terracotta text-parchment border-terracotta'
      case 'success':
        return 'bg-olive text-parchment border-olive'
      case 'info':
        return 'bg-gold text-charcoal border-gold'
    }
  }

  return (
    <ToastContext.Provider value={{ showToast, hideToast }}>
      {children}

      {/* Toast Container */}
      <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`${getVariantStyles(toast.variant)} border rounded-lg shadow-lg px-4 py-3 flex items-start gap-3 animate-slide-in-right`}
          >
            <p className="font-sans text-sm flex-1">{toast.message}</p>
            <button
              onClick={() => hideToast(toast.id)}
              className="text-current hover:opacity-70 transition-opacity"
              aria-label="Dismiss"
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 16 16"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M12 4L4 12M4 4L12 12"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                />
              </svg>
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}
