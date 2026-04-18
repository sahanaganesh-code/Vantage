import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ErrorBanner } from '../components/ErrorBanner.jsx'
import { PillInput } from '../components/PillInput.jsx'
import { VantageLogo } from '../components/VantageLogo.jsx'
import { saveSession } from '../lib/session.js'

export function SetupPage() {
  const navigate = useNavigate()
  const [company, setCompany] = useState('')
  const [competitors, setCompetitors] = useState([])
  const [accounts, setAccounts] = useState([])
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const onSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (!company.trim()) {
      setError('Please enter your company name.')
      return
    }
    if (competitors.length === 0) {
      setError('Add at least one competitor.')
      return
    }
    if (accounts.length === 0) {
      setError('Add at least one target account.')
      return
    }

    setSubmitting(true)
    try {
      const sessionId =
        typeof crypto !== 'undefined' && crypto.randomUUID
          ? crypto.randomUUID()
          : `session-${Date.now()}`
      saveSession({
        sessionId,
        company: company.trim(),
        competitors,
        accounts,
      })
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Setup failed.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="mx-auto flex min-h-screen max-w-lg flex-col justify-center px-6 py-16">
        <div className="mb-10">
          <VantageLogo className="mb-6" />
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900">
            Welcome to Vantage
          </h1>
          <p className="mt-2 text-sm leading-relaxed text-slate-600">
            Tell us who you sell to and who you watch. We will tailor competitive
            intelligence to your GTM motion.
          </p>
        </div>

        <form
          onSubmit={onSubmit}
          className="space-y-6 rounded-xl border border-slate-200 bg-white p-8 shadow-card"
        >
          <ErrorBanner message={error} onDismiss={() => setError('')} />

          <div className="space-y-2">
            <label
              htmlFor="company"
              className="text-sm font-medium text-slate-800"
            >
              Your company name
            </label>
            <input
              id="company"
              name="company"
              type="text"
              autoComplete="organization"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm shadow-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
              placeholder="e.g. Northwind Labs"
            />
          </div>

          <PillInput
            label="Competitors"
            description="Separate names with commas. Up to three tracked rivals."
            value={competitors}
            onChange={setCompetitors}
            max={3}
          />

          <PillInput
            label="Target accounts"
            description="Ideal customers to prioritize. Up to ten accounts."
            value={accounts}
            onChange={setAccounts}
            max={10}
          />

          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-primary-hover disabled:cursor-not-allowed disabled:opacity-60"
          >
            {submitting ? 'Saving…' : 'Continue to dashboard'}
          </button>
        </form>
      </div>
    </div>
  )
}
