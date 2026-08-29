import { AlertCircle, CheckCircle2, LoaderCircle, Sparkles } from 'lucide-react'
import Card from './ui/Card'

type StatusCardProps = {
  title: string
  description: string
  tone?: 'success' | 'warning' | 'neutral'
  icon?: 'success' | 'warning' | 'loading' | 'neutral'
}

function StatusCard({ title, description, tone = 'neutral', icon = 'neutral' }: StatusCardProps) {
  const toneClass = {
    success: 'border-neon-cyan/30 bg-neon-cyan/10 text-neon-cyan',
    warning: 'border-neon-danger/30 bg-neon-danger/10 text-neon-danger',
    neutral: 'border-cyber-border/70 bg-white/5 text-text-muted',
  }[tone]

  const iconMap = {
    success: <CheckCircle2 size={18} />,
    warning: <AlertCircle size={18} />,
    loading: <LoaderCircle size={18} className="animate-spin" />,
    neutral: <Sparkles size={18} />,
  }

  return (
    <Card className={`p-4 ${toneClass}`}>
      <div className="flex items-start gap-3">
        <div className="mt-0.5">{iconMap[icon] ?? iconMap.neutral}</div>
        <div>
          <h3 className="font-medium text-white">{title}</h3>
          <p className="mt-1 text-sm leading-6 text-text-muted">{description}</p>
        </div>
      </div>
    </Card>
  )
}

export default StatusCard
