import { useMemo, useState } from 'react'
import { ErrorBanner } from '../ErrorBanner.jsx'
import { Modal } from '../Modal.jsx'
import { ImpactBadge, UrgencyBadge } from '../badges.jsx'
import {
  API_V1,
  apiRequest,
  buildV1Query,
  deriveBriefActions,
  normalizeBattlecardPayload,
} from '../../lib/api.js'
import { getSession } from '../../lib/session.js'

export function CompetitiveBriefTab() {
  const session = useMemo(() => getSession(), [])
  const competitors = session?.competitors?.length ? session.competitors : []

  const [competitor, setCompetitor] = useState(competitors[0] || '')
  const [summary, setSummary] = useState('')
  const [signals, setSignals] = useState([])
  const [actions, setActions] = useState([])
  const [loadingBrief, setLoadingBrief] = useState(false)
  const [loadingCard, setLoadingCard] = useState(false)
  const [error, setError] = useState('')
  const [battleText, setBattleText] = useState('')
  const [modalOpen, setModalOpen] = useState(false)
  const [copyLabel, setCopyLabel] = useState('Copy')

  const generateBrief = async () => {
    setError('')
    const s = getSession()
    if (!s?.company?.trim()) {
      setError('Missing company. Start a new session from setup.')
      return
    }
    if (!competitor) {
      setError('Select a competitor to analyze.')
      return
    }
    setLoadingBrief(true)
    try {
      const q = buildV1Query({
        company_name: s.company.trim(),
        competitors: competitor,
      })
      const sigRes = await apiRequest(`${API_V1}/signals${q}`, { method: 'GET' })
      const sigs = Array.isArray(sigRes.signals) ? sigRes.signals : []

      const agentRes = await apiRequest(`${API_V1}/agent/analyze`, {
        method: 'POST',
        body: JSON.stringify({
          company_name: s.company.trim(),
          competitors: [competitor],
          query:
            'Write an executive competitive brief: 3 short paragraphs on momentum, risks, and what our sales team should watch.',
        }),
      })

      const analysis =
        typeof agentRes.analysis === 'string' ? agentRes.analysis : ''
      setSummary(analysis)
      setSignals(sigs)
      setActions(deriveBriefActions(sigs))
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to generate brief.')
    } finally {
      setLoadingBrief(false)
    }
  }

  const generateBattlecard = async () => {
    setError('')
    const s = getSession()
    if (!s?.company?.trim() || !competitor) {
      setError('Select a competitor and ensure your company is set in setup.')
      return
    }
    setLoadingCard(true)
    try {
      const data = await apiRequest(`${API_V1}/agent/analyze`, {
        method: 'POST',
        body: JSON.stringify({
          company_name: s.company.trim(),
          competitors: [competitor],
          query:
            'Produce a concise markdown battle card: our positioning vs this competitor, their likely moves, landmines in deals, and 5 bullet talk tracks for AEs.',
        }),
      })
      const text = normalizeBattlecardPayload(data)
      setBattleText(text || JSON.stringify(data, null, 2))
      setModalOpen(true)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to generate battle card.')
    } finally {
      setLoadingCard(false)
    }
  }

  const copyBattle = async () => {
    try {
      await navigator.clipboard.writeText(battleText)
      setCopyLabel('Copied')
      setTimeout(() => setCopyLabel('Copy'), 2000)
    } catch {
      setCopyLabel('Copy failed')
      setTimeout(() => setCopyLabel('Copy'), 2000)
    }
  }

  if (!competitors.length) {
    return (
      <p className="rounded-lg border border-slate-200 bg-white p-6 text-sm text-slate-600 shadow-sm">
        No competitors on file. Complete setup with at least one competitor.
      </p>
    )
  }

  const hasResults = Boolean(summary || signals.length || actions.length)

  return (
    <div className="space-y-6">
      <ErrorBanner message={error} onDismiss={() => setError('')} />

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-card">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div className="max-w-md flex-1 space-y-2">
            <label
              htmlFor="competitor"
              className="text-sm font-medium text-slate-800"
            >
              Competitor
            </label>
            <select
              id="competitor"
              value={competitor}
              onChange={(e) => setCompetitor(e.target.value)}
              className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm shadow-sm outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
            >
              {competitors.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
          <button
            type="button"
            onClick={generateBrief}
            disabled={loadingBrief}
            className="inline-flex items-center justify-center rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-primary-hover disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loadingBrief ? 'Generating…' : 'Generate Brief'}
          </button>
        </div>

        {loadingBrief ? (
          <p className="mt-6 text-sm text-slate-500">Analyzing competitive signals…</p>
        ) : null}
      </section>

      {hasResults ? (
        <div className="space-y-6">
          <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-card">
            <h2 className="text-sm font-semibold text-slate-900">Summary</h2>
            <p className="mt-3 text-sm leading-relaxed text-slate-700">{summary}</p>
          </section>

          <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-card">
            <h2 className="text-sm font-semibold text-slate-900">Signals</h2>
            <ul className="mt-4 space-y-4">
              {signals.map((s, idx) => (
                <li
                  key={`${s.title}-${idx}`}
                  className="rounded-lg border border-slate-100 bg-slate-50/60 p-4"
                >
                  <div className="flex flex-wrap items-center gap-2">
                    <ImpactBadge impact={s.impact} />
                    <span className="text-xs font-medium uppercase tracking-wide text-slate-500">
                      {s.source}
                    </span>
                  </div>
                  <h3 className="mt-2 text-sm font-semibold text-slate-900">
                    {s.title}
                  </h3>
                  <p className="mt-1 text-sm leading-relaxed text-slate-600">
                    {s.body}
                  </p>
                </li>
              ))}
            </ul>
          </section>

          <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-card">
            <h2 className="text-sm font-semibold text-slate-900">Recommended actions</h2>
            <ul className="mt-4 space-y-3">
              {actions.map((a, idx) => (
                <li
                  key={`${a.text}-${idx}`}
                  className="flex flex-wrap items-start gap-3 rounded-lg border border-slate-100 bg-white px-4 py-3"
                >
                  <UrgencyBadge urgency={a.urgency} />
                  <p className="flex-1 text-sm text-slate-700">{a.text}</p>
                </li>
              ))}
            </ul>
          </section>

          <div className="flex justify-end">
            <button
              type="button"
              onClick={generateBattlecard}
              disabled={loadingCard}
              className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-800 shadow-sm transition hover:border-primary hover:text-primary disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loadingCard ? 'Generating…' : 'Generate Battle Card'}
            </button>
          </div>
        </div>
      ) : null}

      <Modal
        title="Battle card"
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        footer={
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={copyBattle}
              className="rounded-lg bg-primary px-3 py-2 text-xs font-semibold text-white hover:bg-primary-hover"
            >
              {copyLabel}
            </button>
          </div>
        }
      >
        <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed text-slate-700">
          {battleText}
        </pre>
      </Modal>
    </div>
  )
}
