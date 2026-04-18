import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { VantageLogo } from '../components/VantageLogo.jsx'
import { AccountPrioritizerTab } from '../components/dashboard/AccountPrioritizerTab.jsx'
import { CompetitiveBriefTab } from '../components/dashboard/CompetitiveBriefTab.jsx'
import { SignalFeedTab } from '../components/dashboard/SignalFeedTab.jsx'
import { clearSession, getSession } from '../lib/session.js'

const tabs = [
  { id: 'brief', label: 'Competitive Brief' },
  { id: 'prioritizer', label: 'Account Prioritizer' },
  { id: 'signals', label: 'Signal Feed' },
]

export function DashboardPage() {
  const navigate = useNavigate()
  const session = useMemo(() => getSession(), [])
  const [activeTab, setActiveTab] = useState('brief')

  const newSession = () => {
    clearSession()
    navigate('/setup', { replace: true })
  }

  const companyName = session?.company || 'Your workspace'

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-6 py-4">
          <div className="flex min-w-0 items-center gap-4">
            <VantageLogo />
            <div className="hidden h-6 w-px bg-slate-200 sm:block" aria-hidden />
            <p className="truncate text-sm font-medium text-slate-700">
              {companyName}
            </p>
          </div>
          <button
            type="button"
            onClick={newSession}
            className="shrink-0 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-700 shadow-sm transition hover:border-slate-300 hover:bg-slate-50"
          >
            New Session
          </button>
        </div>
        <nav className="mx-auto flex max-w-5xl gap-6 px-6">
          {tabs.map((t) => {
            const active = activeTab === t.id
            return (
              <button
                key={t.id}
                type="button"
                onClick={() => setActiveTab(t.id)}
                className={`relative pb-3 text-sm font-medium transition ${
                  active
                    ? 'text-primary'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                {t.label}
                {active ? (
                  <span className="absolute inset-x-0 bottom-0 h-0.5 rounded-full bg-primary" />
                ) : null}
              </button>
            )
          })}
        </nav>
      </header>

      <main className="mx-auto max-w-5xl px-6 py-10">
        {activeTab === 'brief' ? <CompetitiveBriefTab /> : null}
        {activeTab === 'prioritizer' ? <AccountPrioritizerTab /> : null}
        {activeTab === 'signals' ? <SignalFeedTab /> : null}
      </main>
    </div>
  )
}
