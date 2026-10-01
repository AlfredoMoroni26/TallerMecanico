import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import http, { tokenStorage } from '@/api/http'
import type { TokenPair, User } from '../types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  // El token confirma la sesión; el perfil se carga de forma asíncrona en la guarda de rutas.
  const isAuthenticated = computed(() => Boolean(tokenStorage.access))
  const roles = computed(() => user.value?.roles.map(role => role.name) ?? [])

  async function login(login: string, password: string) {
    const { data } = await http.post<TokenPair>('/auth/login', { login, password })
    tokenStorage.save(data)
    await loadProfile()
  }
  async function loadProfile() { user.value = (await http.get<User>('/users/me')).data }
  async function logout() {
    const refresh = tokenStorage.refresh
    try { if (refresh) await http.post('/auth/logout', { refresh_token: refresh }) } finally { tokenStorage.clear(); user.value = null }
  }
  function hasRole(required: string | string[]) { return (Array.isArray(required) ? required : [required]).some(role => roles.value.includes(role)) }
  return { user, roles, isAuthenticated, login, loadProfile, logout, hasRole }
})
