export function ErrorBanner({ message, onDismiss }) {
  if (!message) return null
  return (
    <div
      className="flex items-start justify-between gap-3 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800"
      role="alert"
    >
      <p className="leading-relaxed">{message}</p>
      {onDismiss ? (
        <button
          type="button"
          onClick={onDismiss}
          className="shrink-0 rounded px-2 py-0.5 text-xs font-medium text-red-700 hover:bg-red-100"
        >
          Dismiss
        </button>
      ) : null}
    </div>
  )
}
