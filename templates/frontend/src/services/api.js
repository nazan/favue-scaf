import { config } from '../config'

const TOKEN_KEY = 'access_token'

export function getStoredToken() {
  if (typeof localStorage === 'undefined') {
    return null
  }
  return localStorage.getItem(TOKEN_KEY)
}

export function setStoredToken(token) {
  if (typeof localStorage === 'undefined') {
    return
  }
  if (token) {
    localStorage.setItem(TOKEN_KEY, token)
  } else {
    localStorage.removeItem(TOKEN_KEY)
  }
}

export function clearStoredToken() {
  setStoredToken(null)
}

/**
 * FastAPI error JSON: {"detail": "..."} or list of field errors
 */
function extractErrorMessage(text, status) {
  if (!text) {
    return `HTTP ${status}`
  }
  try {
    const errorJson = JSON.parse(text)
    if (errorJson.detail) {
      if (Array.isArray(errorJson.detail)) {
        return errorJson.detail.map((err) => {
          const field = err.loc && err.loc.length > 1
            ? err.loc.slice(1).join('.')
            : (err.loc?.[0] || 'field')
          return `${field}: ${err.msg || 'validation error'}`
        }).join('; ')
      }
      return String(errorJson.detail)
    }
    if (errorJson.message) {
      return String(errorJson.message)
    }
    return JSON.stringify(errorJson)
  } catch (parseError) {
    return text.trim() || `HTTP ${status}`
  }
}

async function request(path, options = {}) {
  const url = `${config.apiBaseUrl}${path}`
  const { headers: customHeaders, body, ...restOptions } = options
  const requestBody = body && typeof body === 'object' && !(body instanceof FormData) && !(body instanceof URLSearchParams)
    ? JSON.stringify(body)
    : body
  const headers = {
    'Content-Type': 'application/json',
    ...(customHeaders || {}),
  }
  const res = await fetch(url, {
    ...restOptions,
    headers,
    body: requestBody,
  })
  if (!res.ok) {
    const t = await res.text().catch(() => '')
    const errorMessage = extractErrorMessage(t, res.status)
    const err = new Error(errorMessage)
    err.status = res.status
    throw err
  }
  const ct = res.headers.get('content-type') || ''
  return ct.includes('application/json') ? res.json() : res.text()
}

export function authHeaders() {
  const t = getStoredToken()
  return t ? { Authorization: `Bearer ${t}` } : {}
}

export async function authRequest(path, options = {}) {
  return request(path, {
    ...options,
    headers: { ...options.headers, ...authHeaders() },
  })
}

export async function registerUser({ username, email, password }) {
  return request('/api/auth/register', {
    method: 'POST',
    body: { username, email, password },
  })
}

/**
 * OAuth2 form: `username` field carries the email.
 */
export async function loginWithPassword(email, password) {
  const body = new URLSearchParams()
  body.set('username', email)
  body.set('password', password)
  const url = `${config.apiBaseUrl}/api/auth/login`
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body.toString(),
  })
  if (!res.ok) {
    const t = await res.text().catch(() => '')
    const err = new Error(extractErrorMessage(t, res.status))
    err.status = res.status
    throw err
  }
  return res.json()
}

export async function getMe() {
  return authRequest('/api/auth/me')
}

export async function verifyEmailToken(token) {
  return request('/api/auth/verify-email', {
    method: 'POST',
    body: { token: String(token || '').trim() },
  })
}

export async function runInfraSecureJob() {
  return authRequest('/api/v1/infra/secure-worker-ws', { method: 'POST' })
}
