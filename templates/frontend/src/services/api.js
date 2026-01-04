import { config } from '../config'

/**
 * Extract human-readable error message from API error response.
 * FastAPI returns errors as JSON: {"detail": "message"}
 */
function extractErrorMessage(text, status) {
  if (!text) {
    return `HTTP ${status}`
  }
  
  try {
    const errorJson = JSON.parse(text)
    if (errorJson.detail) {
      if (Array.isArray(errorJson.detail)) {
        return errorJson.detail.map(err => {
          const field = err.loc && err.loc.length > 1 ? err.loc.slice(1).join('.') : (err.loc?.[0] || 'field')
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
  
  const requestBody = body && typeof body === 'object' && !(body instanceof FormData) 
    ? JSON.stringify(body) 
    : body
  
  const headers = { 
    'Content-Type': 'application/json', 
    ...(customHeaders || {})
  }
  
  const res = await fetch(url, {
    ...restOptions,
    headers: headers,
    body: requestBody
  })
  
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    const errorMessage = extractErrorMessage(text, res.status)
    const err = new Error(errorMessage)
    err.status = res.status
    throw err
  }
  
  const ct = res.headers.get('content-type') || ''
  return ct.includes('application/json') ? res.json() : res.text()
}

export async function getDatabaseVersion() {
  return request('/api/dbversion')
}

