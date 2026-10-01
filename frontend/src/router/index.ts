import { createRouter, createWebHistory, type RouteLocationNormalized } from 'vue-router'
import { useAuthStore } from '@/modules/identity/stores/auth'
import { tokenStorage } from '@/api/http'

declare module 'vue-router' { interface RouteMeta { requiresAuth?: boolean; roles?: string[] } }
const routes = [
  { path: '/', component: () => import('@/modules/identity/views/DashboardView.vue'), meta: { requiresAuth: true } },
  { path: '/login', component: () => import('@/modules/identity/views/LoginView.vue') },
  { path: '/register', component: () => import('@/modules/identity/views/RegisterView.vue') },
  { path: '/forgot-password', component: () => import('@/modules/identity/views/ForgotPasswordView.vue') },
  { path: '/admin/users', component: () => import('@/modules/identity/views/UsersAdminView.vue'), meta: { requiresAuth: true, roles: ['administrador_taller'] } },
  { path: '/admin/roles', component: () => import('@/modules/identity/views/RolesAdminView.vue'), meta: { requiresAuth: true, roles: ['administrador_taller'] } },
]
const router = createRouter({ history: createWebHistory(), routes })
router.beforeEach(async (to: RouteLocationNormalized) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth) {
    if (!tokenStoragePresent()) return { path: '/login', query: { redirect: to.fullPath } }
    if (!auth.user) {
      try { await auth.loadProfile() } catch { tokenStorage.clear(); return { path: '/login', query: { redirect: to.fullPath } } }
    }
  }
  if (to.meta.roles && !auth.hasRole(to.meta.roles)) return '/login'
  if (to.path === '/login' && auth.isAuthenticated) return '/'
})
function tokenStoragePresent() { return Boolean(sessionStorage.getItem('tm_access_token')) }
export default router
