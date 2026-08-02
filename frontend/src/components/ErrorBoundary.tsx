import { Component, type ErrorInfo, type ReactNode } from 'react'
import Button from './ui/Button'

type Props = {
  children: ReactNode
}

type State = {
  hasError: boolean
}

class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('UI error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen items-center justify-center px-4 py-10">
          <div className="max-w-lg rounded-[28px] border border-neon-danger/30 bg-cyber-panel/80 p-8 text-center shadow-[0_0_50px_rgba(255,107,107,0.16)]">
            <h2 className="text-2xl font-semibold">Something went sideways</h2>
            <p className="mt-3 text-sm leading-7 text-text-muted">The interface hit an unexpected error. Retry or return home to recover.</p>
            <div className="mt-6 flex justify-center gap-3">
              <Button onClick={() => window.location.reload()}>Reload app</Button>
              <Button variant="secondary" onClick={() => window.location.assign('/')}>Back home</Button>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
