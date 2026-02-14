import { createContext } from 'react'

type ToastVariant = 'error' | 'success' | 'info'

export interface ToastContextValue {
  showToast: (message: string, variant?: ToastVariant) => void
  hideToast: (id: string) => void
}

export const ToastContext = createContext<ToastContextValue | undefined>(undefined)
