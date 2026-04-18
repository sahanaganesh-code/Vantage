import { useEffect, useState } from 'react'
import { ErrorBanner } from '../ErrorBanner.jsx'
import { ImpactBadge } from '../badges.jsx'
import { API_V1, apiRequest, buildV1Query } from '../../lib/api.js'
import { getSession, getSessionId } from '../../lib/session.js'

function formatDate(value) {
  if (!value) return '—'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return value
  return d.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function SignalFeedTab() {
  const sessionId = getSessionId()
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(Boolean(sessionId))
  const [error, setError] = useState(
    sessionId ? '' : 'Missing session. Start a new session from setup.',
  )

  useEffect(() => {
    if (!sessionId) return undefined

    let cancelled = false

    const load = async () => {
      setLoading(true)
      setError('')
      try {
        const session = getSession()
        if (!session?.company?.trim() || !session?.competitors?.length) {
          if (!cancelled) {
            setError('Add your company and competitors in setup to load signals.')
          }
          return
        }
        const q = buildV1Query({
          company_name: session.company.trim(),
          competitors: session.competitors.join(','),
        })
        const data = await apiRequest(`${API_V1}/signals${q}`, { method: 'GET' })
        const list = Array.isArray(data.signals) ? data.signals : []
        if (!cancelled) setItems(list)
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : 'Could not load signals.')
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    load()
    return () => {
      cancelled = true
    }
  }, [sessionId])

  return (
    <div className="space-y-6">
      <ErrorBanner message={error} onDismiss={() => setError('')} />

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-card">
        <h2 className="text-base font-semibold text-slate-900">Signal feed</h2>
        <p className="mt-1 text-sm text-slate-600">
          Chronological intelligence across your competitive landscape.
        </p>
      </section>

      {loading ? (
        <p className="text-sm text-slate-500">Loading signals…</p>
      ) : null}

      {!loading && !items.length && !error ? (
        <p className="text-sm text-slate-600">No signals yet.</p>
      ) : null}

      <div className="space-y-4">
        {items.map((s, idx) => (
          <article
            key={`${s.title}-${s.date}-${idx}`}
            className="rounded-xl border border-slate-200 bg-white p-5 shadow-card"
          >
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded-md border border-slate-200 bg-slate-50 px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide text-slate-600">
                {s.source}
              </span>
              <ImpactBadge impact={s.impact} />
              <time className="ml-auto text-xs text-slate-500">
                {formatDate(s.date)}
              </time>
            </div>
            <h3 className="mt-3 text-sm font-semibold text-slate-900">
              {s.title}
            </h3>
            <p className="mt-2 text-sm leading-relaxed text-slate-600">{s.body}</p>
          </article>
        ))}
      </div>
    </div>
  )
}
