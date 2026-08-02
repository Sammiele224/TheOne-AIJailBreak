type CardProps = {
  children: React.ReactNode
  className?: string
}

function Card({ children, className = '' }: CardProps) {
  return <div className={`rounded-2xl border border-cyber-border/80 bg-cyber-panel/70 backdrop-blur-xl ${className}`}>{children}</div>
}

export default Card
