import { Link, NavLink } from 'react-router-dom'
import { AudioLines, Command, MoonStar, Settings2, ShieldCheck, Sparkles } from 'lucide-react'
import Button from './ui/Button'
import Badge from './ui/Badge'

type LayoutProps = {
  children: React.ReactNode
  title?: string
  subtitle?: string
  action?: React.ReactNode
}

function Layout({ children, title, subtitle, action }: LayoutProps) {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,rgba(78,246,255,0.16),transparent_25%),linear-gradient(135deg,#06070d_0%,#090c15_100%)] text-white">
      <div className="mx-auto flex min-h-screen max-w-7xl flex-col px-4 py-4 sm:px-6 lg:px-8">
        <header className="mb-4 rounded-[28px] border border-cyber-border/80 bg-cyber-panel/70 px-4 py-3 shadow-[0_0_30px_rgba(78,246,255,0.08)] backdrop-blur-xl">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <Link to="/" className="flex items-center gap-3">
              <div className="rounded-2xl border border-neon-cyan/30 bg-neon-cyan/10 p-2 text-neon-cyan">
                <ShieldCheck size={18} />
              </div>
              <div>
                <p className="font-mono text-[10px] uppercase tracking-[0.32em] text-neon-cyan">NeuroCorp</p>
                <h2 className="text-sm font-semibold">Security Relay</h2>
              </div>
            </Link>
            <nav className="flex flex-wrap items-center gap-2 text-sm text-text-muted">
              <NavLink to="/" className={({ isActive }) => `rounded-full px-3 py-2 transition ${isActive ? 'bg-white/10 text-white' : 'hover:bg-white/5 hover:text-white'}`}>
                Hub
              </NavLink>
              <NavLink to="/level/1" className={({ isActive }) => `rounded-full px-3 py-2 transition ${isActive ? 'bg-white/10 text-white' : 'hover:bg-white/5 hover:text-white'}`}>
                Lab
              </NavLink>
              <NavLink to="/result" className={({ isActive }) => `rounded-full px-3 py-2 transition ${isActive ? 'bg-white/10 text-white' : 'hover:bg-white/5 hover:text-white'}`}>
                Results
              </NavLink>
            </nav>
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="sm" className="rounded-full">
                <Command size={16} className="mr-2" /> Command
              </Button>
              <Button variant="secondary" size="sm" className="rounded-full">
                <MoonStar size={16} />
              </Button>
            </div>
          </div>
        </header>

        <main className="flex-1">
          {(title || subtitle || action) && (
            <div className="mb-5 flex flex-col gap-4 rounded-3xl border border-cyber-border/70 bg-cyber-panel/60 px-5 py-5 backdrop-blur-xl sm:flex-row sm:items-end sm:justify-between">
              <div>
                {title ? <h1 className="text-2xl font-semibold tracking-tight">{title}</h1> : null}
                {subtitle ? <p className="mt-2 max-w-2xl text-sm leading-7 text-text-muted">{subtitle}</p> : null}
              </div>
              <div className="flex items-center gap-2">
                <Badge tone="cyan">Live Session</Badge>
                {action}
              </div>
            </div>
          )}
          {children}
        </main>

        <footer className="mt-4 flex flex-col gap-3 rounded-3xl border border-cyber-border/70 bg-cyber-panel/60 px-4 py-4 text-sm text-text-muted backdrop-blur-xl sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-2">
            <Sparkles size={16} className="text-neon-cyan" />
            <span>NeuroCorp Relay • Secure prompt experiments with calm precision.</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1"><AudioLines size={14} /> Audio On</span>
            <span className="flex items-center gap-1"><Settings2 size={14} /> Live Settings</span>
          </div>
        </footer>
      </div>
    </div>
  )
}

export default Layout
