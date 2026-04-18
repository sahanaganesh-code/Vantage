const API_BASE =
  import.meta.env.VITE_API_URL?.replace(/\/$/, '') || 'http://localhost:8000'

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
    summary: data.summary ?? data.overview ?? '',
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
