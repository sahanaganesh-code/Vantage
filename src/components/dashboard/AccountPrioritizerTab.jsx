import { useState } from 'react'
import { ErrorBanner } from '../ErrorBanner.jsx'
import { API_V1, apiRequest, buildV1Query, rankTargetAccounts } from '../../lib/api.js'
import { getSession, getSessionId } from '../../lib/session.js'

export function AccountPrioritizerTab() {
  const [accounts, setAccounts] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const prioritize = async () => {
    setError('')
    const sessionId = getSessionId()
    if (!sessionId) {
      setError('Missing session. Start a new session from setup.')
      return
    }
    const session = getSession()
    if (!session?.accounts?.length) {
      setError('Add target accounts in setup first.')
      return
    }
    if (!session.company?.trim() || !session.competitors?.length) {
      setError('Add your company and competitors in setup.')
      return
    }

    setLoading(true)
    try {
      const q = buildV1Query({
        company_name: session.company.trim(),
        competitors: session.competitors.join(','),
      })
      const data = await apiRequest(`${API_V1}/signals${q}`, { method: 'GET' })
      const signals = Array.isArray(data.signals) ? data.signals : []
      setAccounts(rankTargetAccounts(session.accounts, signals))
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Prioritization failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <ErrorBanner message={error} onDismiss={() => setError('')} />

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-card">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-base font-semibold text-slate-900">
              Account Prioritizer
            </h2>
            <p className="mt-1 text-sm text-slate-600">
              Rank target accounts using the merged signal feed (client-side scoring
              until a dedicated prioritize API exists).
            </p>
          </div>
          <button
            type="button"
            onClick={prioritize}
            disabled={loading}
            className="inline-flex items-center justify-center rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-primary-hover disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? 'Prioritizing…' : 'Prioritize My Accounts'}
          </button>
        </div>
        {loading ? (
          <p className="mt-4 text-sm text-slate-500">Scoring accounts…</p>
        ) : null}
      </section>

      {accounts.length ? (
        <ol className="space-y-4">
          {accounts.map((acc, idx) => {
            const rank = idx + 1
            const score = Math.min(100, Math.max(0, Number(acc.score) || 0))
            const signalPills = (acc.signals || []).slice(0, 3)
            const accent = (impact) => {
              if (impact === 'high') return 'border-l-red-500'
              if (impact === 'medium') return 'border-l-amber-500'
              return 'border-l-slate-300'
            }
            return (
              <li
                key={`${acc.name}-${rank}`}
                className="rounded-xl border border-slate-200 bg-white p-5 shadow-card"
              >
                <div className="flex flex-wrap items-start gap-4">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full border border-slate-200 bg-primary-muted text-sm font-bold text-primary">
                    {rank}
                  </div>
                  <div className="min-w-0 flex-1 space-y-3">
                    <div className="flex flex-wrap items-baseline justify-between gap-2">
                      <h3 className="text-sm font-semibold text-slate-900">
                        {acc.name}
                      </h3>
                      <span className="text-xs font-medium text-slate-500">
                        Score {score}
                      </span>
                    </div>
                    <div>
                      <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
                        <div
                          className="h-full rounded-full bg-primary transition-all"
                          style={{ width: `${score}%` }}
                        />
                      </div>
                    </div>
                    <p className="text-sm leading-relaxed text-slate-600">
                      {acc.reason}
                    </p>
                    {signalPills.length ? (
                      <div className="flex flex-wrap gap-2">
                        {signalPills.map((s, sidx) => (
                          <span
                            key={`${s.title}-${sidx}`}
                            className={`max-w-[240px] truncate rounded-full border border-slate-200 border-l-4 bg-slate-50 px-3 py-1 text-xs font-medium text-slate-700 ${accent(s.impact)}`}
                          >
                            {s.title || s.source}
                          </span>
                        ))}
                      </div>
                    ) : null}
                  </div>
                </div>
              </li>
            )
          })}
        </ol>
      ) : null}
    </div>
  )
}
