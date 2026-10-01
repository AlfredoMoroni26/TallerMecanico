import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import type { ApiError, TokenPair } from '@/modules/identity/types'

const ACCESS_KEY = 'tm_access_token'
const REFRESH_KEY = 'tm_refresh_token'
// Permite operar localmente incluso si Vite se inició antes de crear el .env.
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1'
let refreshing: Promise<string | null> | null = null

export const tokenStorage = {
  get access() { return sessionStorage.getItem(ACCESS_KEY) },
  get refresh() { return sessionStorage.getItem(REFRESH_KEY) },
  save(tokens: TokenPair) { sessionStorage.setItem(ACCESS_KEY, tokens.access_token); sessionStorage.setItem(REFRESH_KEY, tokens.refresh_token) },
  clear() { sessionStorage.removeItem(ACCESS_KEY); sessionStorage.removeItem(REFRESH_KEY) },
}

const http = axios.create({ baseURL: API_BASE_URL, headers: { 'Content-Type': 'application/json' } })

http.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = tokenStorage.access
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

async function renewAccessToken(): Promise<string | null> {
  if (!tokenStorage.refresh) return null
  try {
    const { data } = await axios.post<TokenPair>(`${API_BASE_URL}/auth/refresh`, { refresh_token: tokenStorage.refresh })
    tokenStorage.save(data)
    return data.access_token
  } catch {
    tokenStorage.clear()
    return null
  }
}

http.interceptors.response.use(
  response => response,
  async (error: AxiosError<ApiError>) => {
    const original = error.config as (InternalAxiosRequestConfig & { _retried?: boolean }) | undefined
    if (error.response?.status === 401 && original && !original._retried && !original.url?.includes('/auth/')) {
      original._retried = true
      refreshing ??= renewAccessToken().finally(() => { refreshing = null })
      const access = await refreshing
      if (access) { original.headers.Authorization = `Bearer ${access}`; return http(original) }
      window.location.assign('/login')
    }
    // Las vistas muestran error.response.data.detail; no exponemos detalles internos.
    return Promise.reject(error)
  },
)

export const getErrorMessage = (error: unknown): string => {
  if (axios.isAxiosError<ApiError>(error)) return error.response?.data?.detail ?? 'No fue posible comunicarse con el servidor.'
  return 'Ocurrió un error inesperado.'
}
export default http
