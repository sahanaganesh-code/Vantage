const SESSION_KEY = 'vantage_session'

export function getSession() {
  try {
    const raw = localStorage.getItem(SESSION_KEY)
    if (!raw) return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export function getSessionId() {
  return localStorage.getItem('session_id')
}

/**
 * @param {{ sessionId: string, company: string, competitors: string[], accounts: string[] }} payload
 */
export function saveSession({ sessionId, company, competitors, accounts }) {
  localStorage.setItem('session_id', sessionId)
  localStorage.setItem(
    SESSION_KEY,
    JSON.stringify({
      sessionId,
      company,
      competitors,
      accounts,
    }),
  )
}

export function clearSession() {
  localStorage.removeItem('session_id')
  localStorage.removeItem(SESSION_KEY)
}

export function hasSession() {
  return Boolean(getSessionId())
}
