import { useCallback, useState } from 'react'

function addTokens(rawInput, items, max, onChange) {
  const raw = rawInput
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean)
  if (raw.length === 0) return
  const next = [...items]
  for (const token of raw) {
    if (next.length >= max) break
    if (!next.includes(token)) next.push(token)
  }
  onChange(next)
}

/**
 * @param {{
 *   label: string
 *   description?: string
 *   value: string[]
 *   onChange: (next: string[]) => void
 *   max: number
 *   placeholder?: string
 * }} props
 */
export function PillInput({
  label,
  description,
  value,
  onChange,
  max,
  placeholder = 'Type and press Enter or comma…',
}) {
  const [draft, setDraft] = useState('')

  const flushDraft = useCallback(() => {
    const trimmed = draft.trim()
    if (!trimmed) return
    addTokens(trimmed, value, max, onChange)
    setDraft('')
  }, [draft, max, onChange, value])

  const atCapacity = value.length >= max

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      flushDraft()
      return
    }
    if (e.key === ',') {
      e.preventDefault()
      const segment = draft.trim()
      if (segment) addTokens(segment, value, max, onChange)
      setDraft('')
      return
    }
    if (e.key === 'Backspace' && !draft && value.length) {
      onChange(value.slice(0, -1))
    }
  }

  const remove = (idx) => {
    onChange(value.filter((_, i) => i !== idx))
  }

  return (
    <div className="space-y-2">
      <div className="flex items-baseline justify-between gap-2">
        <label className="text-sm font-medium text-slate-800">{label}</label>
        <span className="text-xs text-slate-500">
          {value.length}/{max}
        </span>
      </div>
      {description ? (
        <p className="text-xs text-slate-500">{description}</p>
      ) : null}
      <div
        className={`flex min-h-[42px] flex-wrap items-center gap-2 rounded-lg border border-slate-200 bg-white px-2 py-1.5 shadow-sm focus-within:border-primary focus-within:ring-2 focus-within:ring-primary/15 ${
          atCapacity ? 'opacity-80' : ''
        }`}
      >
        {value.map((pill, idx) => (
          <span
            key={`${pill}-${idx}`}
            className="inline-flex items-center gap-1 rounded-md border border-slate-200 bg-slate-50 px-2 py-0.5 text-xs font-medium text-slate-700"
          >
            {pill}
            <button
              type="button"
              onClick={() => remove(idx)}
              className="rounded p-0.5 text-slate-500 hover:bg-slate-200 hover:text-slate-800"
              aria-label={`Remove ${pill}`}
            >
              ×
            </button>
          </span>
        ))}
        <input
          className="min-w-[120px] flex-1 border-0 bg-transparent py-1 text-sm outline-none placeholder:text-slate-400"
          placeholder={atCapacity ? 'Maximum reached' : placeholder}
          value={draft}
          disabled={atCapacity}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={handleKeyDown}
          onBlur={() => {
            if (draft.includes(',')) {
              addTokens(draft, value, max, onChange)
              setDraft('')
            }
          }}
        />
      </div>
    </div>
  )
}
