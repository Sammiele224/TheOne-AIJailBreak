function LoadingState() {
  return (
    <div className="grid gap-3 md:grid-cols-2">
      {[0, 1, 2, 3].map((item) => (
        <div key={item} className="animate-pulse rounded-2xl border border-cyber-border/70 bg-cyber-panel/60 p-4">
          <div className="h-3 w-24 rounded-full bg-white/10" />
          <div className="mt-3 h-3 w-full rounded-full bg-white/10" />
          <div className="mt-2 h-3 w-5/6 rounded-full bg-white/10" />
          <div className="mt-5 h-24 rounded-xl bg-white/10" />
        </div>
      ))}
    </div>
  )
}

export default LoadingState
