const impactStyles = {
  high: 'border-red-200 bg-red-50 text-red-700',
  medium: 'border-amber-200 bg-amber-50 text-amber-800',
  low: 'border-slate-200 bg-slate-100 text-slate-600',
}

export function ImpactBadge({ impact }) {
  const key = impact === 'high' || impact === 'medium' || impact === 'low' ? impact : 'low'
  return (
    <span
      className={`inline-flex items-center rounded-md border px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide ${impactStyles[key]}`}
    >
      {key}
    </span>
  )
}

const urgencyStyles = {
  'this-week': 'border-blue-200 bg-blue-50 text-blue-800',
  'this-month': 'border-slate-200 bg-slate-100 text-slate-600',
}

export function UrgencyBadge({ urgency }) {
  const key =
    urgency === 'this-week' || urgency === 'this-month' ? urgency : 'this-month'
  return (
    <span
      className={`inline-flex items-center rounded-md border px-2 py-0.5 text-[11px] font-semibold capitalize ${urgencyStyles[key]}`}
    >
      {key
        .split('-')
        .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
        .join(' ')}
    </span>
  )
}
