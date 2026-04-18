export function VantageLogo({ className = '' }) {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <div
        className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-xs font-bold text-white shadow-sm"
        aria-hidden
      >
        V
      </div>
      <span className="text-sm font-semibold tracking-tight text-slate-900">
        Vantage
      </span>
    </div>
  )
}
