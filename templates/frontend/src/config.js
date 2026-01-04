const defaultBase = 'http://localhost:${API_PORT}'

export const config = {
  apiBaseUrl: (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_BASE_URL)
    || (typeof window !== 'undefined' && window.API_BASE_URL)
    || defaultBase
}

