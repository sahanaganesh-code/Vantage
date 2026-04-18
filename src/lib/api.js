const API_BASE =
  import.meta.env.VITE_API_URL?.replace(/\/$/, '') || 'http://localhost:8000'

/** FastAPI surface (Person 3) — all live data + agent routes. */
export const API_V1 = '/api/v1'

/**
 * @param {Record<string, string | undefined | null>} params
 */
export function buildV1Query(params) {
  const sp = new URLSearchParams()
  for (const [k, v] of Object.entries(params)) {
    if (v != null && String(v).length) sp.set(k, String(v))
  }
  const q = sp.toString()
  return q ? `?${q}` : ''
}

function parseErrorMessage(data, fallback) {
  if (data == null) return fallback
  if (typeof data === 'string') return data
  if (typeof data.detail === 'string') return data.detail
  if (Array.isArray(data.detail)) {
    return data.detail
      .map((d) => (typeof d === 'string' ? d : d?.msg || JSON.stringify(d)))
      .filter(Boolean)
      .join(' ')
  }
  if (data.message) return String(data.message)
  if (data.error) return String(data.error)
  try {
    return JSON.stringify(data)
  } catch {
    return fallback
  }
}

/**
 * @param {string} path
 * @param {RequestInit} [options]
 */
export async function apiRequest(path, options = {}) {
  const url = `${API_BASE}${path.startsWith('/') ? path : `/${path}`}`
  const headers = {
    Accept: 'application/json',
    ...(options.body ? { 'Content-Type': 'application/json' } : {}),
    ...options.headers,
  }

  const res = await fetch(url, {
    ...options,
    headers,
  })

  const text = await res.text()
  let data = null
  if (text) {
    try {
      data = JSON.parse(text)
    } catch {
      data = text
    }
  }

  if (!res.ok) {
    const msg = parseErrorMessage(
      typeof data === 'object' && data !== null ? data : null,
      res.statusText || 'Request failed',
    )
    throw new Error(msg)
  }

  return data
}

export function normalizeBriefPayload(data) {
  if (!data || typeof data !== 'object') {
    return { summary: '', signals: [], actions: [] }
  }
  return {
    summary:
      data.summary ??
      data.overview ??
      (typeof data.analysis === 'string' ? data.analysis : ''),
    signals: Array.isArray(data.signals) ? data.signals : [],
    actions: Array.isArray(data.actions) ? data.actions : [],
  }
}

export function normalizeBattlecardPayload(data) {
  if (data == null) return ''
  if (typeof data === 'string') return data
  return (
    data.battlecard ??
    data.content ??
    data.text ??
    data.markdown ??
    data.body ??
    (typeof data.analysis === 'string' ? data.analysis : '') ??
    ''
  )
}

export function normalizeRankedAccounts(data) {
  if (Array.isArray(data)) return data
  if (data && typeof data === 'object') {
    if (Array.isArray(data.accounts)) return data.accounts
    if (Array.isArray(data.results)) return data.results
    if (Array.isArray(data.ranked_accounts)) return data.ranked_accounts
  }
  return []
}

export function normalizeSignalsList(data) {
  if (Array.isArray(data)) return data
  if (data && typeof data === 'object' && Array.isArray(data.signals)) {
    return data.signals
  }
  return []
}

/** When the backend has no `actions` list, derive a short GTM checklist from signals. */
export function deriveBriefActions(signals) {
  const out = []
  const highs = signals.filter((s) => s.impact === 'high').slice(0, 2)
  for (const s of highs) {
    const t = (s.title || s.source || 'Signal').slice(0, 120)
    out.push({
      text: `Pressure-test your pitch against: ${t}`,
      urgency: 'this-week',
    })
  }
  out.push({
    text: 'Align AE and marketing on the narratives surfaced in the signal list this month.',
    urgency: 'this-month',
  })
  return out.slice(0, 4)
}

/**
 * Client-side account ranking using the merged signal feed (no `/api/prioritize` yet).
 * @param {string[]} accounts
 * @param {Array<{ title?: string, body?: string, company?: string, impact?: string }>} signals
 */
export function rankTargetAccounts(accounts, signals) {
  const list = (accounts || []).map((name) => {
    const words = name
      .toLowerCase()
      .split(/\s+/)
      .filter((w) => w.length > 2)
    let score = 25
    const matched = []
    for (const sig of signals || []) {
      const blob = `${sig.title || ''} ${sig.body || ''} ${sig.company || ''}`.toLowerCase()
      const hit = words.some((w) => blob.includes(w))
      if (hit) {
        score += 14
        if (matched.length < 3) matched.push(sig)
      }
    }
    score = Math.min(100, score)
    const reason = matched.length
      ? `Stronger overlap with the current signal set (${matched.length} related items).`
      : 'Few direct keyword hits in the current corpus; rank reflects baseline ICP priority.'
    return { name, score, reason, signals: matched }
  })
  return list.sort((a, b) => b.score - a.score).slice(0, 10)
}
