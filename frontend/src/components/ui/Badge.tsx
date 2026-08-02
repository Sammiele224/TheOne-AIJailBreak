type BadgeProps = {
  children: React.ReactNode
  tone?: 'cyan' | 'magenta' | 'danger' | 'neutral'
}

const tones = {
  cyan: 'border-neon-cyan/30 bg-neon-cyan/10 text-neon-cyan',
  magenta: 'border-neon-magenta/30 bg-neon-magenta/10 text-neon-magenta',
  danger: 'border-neon-danger/30 bg-neon-danger/10 text-neon-danger',
  neutral: 'border-cyber-border bg-white/5 text-text-muted',
}

function Badge({ children, tone = 'neutral' }: BadgeProps) {
  return <span className={`inline-flex items-center rounded-full border px-3 py-1 text-[11px] font-medium uppercase tracking-[0.28em] ${tones[tone]}`}>{children}</span>
}

export default Badge
