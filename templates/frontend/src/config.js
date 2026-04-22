// With nginx gateway: use VITE_API_BASE_URL from env (e.g. http://localhost). Direct-to-uvicorn: http://localhost:8000
const defaultBase = 'http://localhost:8000'

export const config = {
  apiBaseUrl: (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_BASE_URL)
    || (typeof window !== 'undefined' && window.API_BASE_URL)
    || defaultBase,
}

export function getWsBaseUrl() {
  const b = config.apiBaseUrl
  if (b) {
    return b.replace(/^http/, 'ws')
  }
  if (typeof window !== 'undefined') {
    return `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}`
  }
  return 'ws://localhost'
}
