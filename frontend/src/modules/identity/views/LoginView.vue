<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AuthLayout from '@/layouts/AuthLayout.vue'
import { useAuthStore } from '../stores/auth'
import { getErrorMessage } from '@/api/http'

const auth = useAuthStore(); const router = useRouter(); const route = useRoute()
const login = ref(''); const password = ref(''); const loading = ref(false); const error = ref(''); const submitted = ref(false)
const valid = () => login.value.trim().length >= 3 && password.value.length >= 8
async function submit() {
  submitted.value = true; if (!valid()) return; loading.value = true; error.value = ''
  try { await auth.login(login.value, password.value); await router.push((route.query.redirect as string) || '/') } catch (e) { error.value = getErrorMessage(e) } finally { loading.value = false }
}
</script>
<template><AuthLayout><p class="eyebrow">Portal de operación</p><h1>Bienvenido de vuelta</h1><p class="intro">Ingresa tus datos para continuar al panel del taller.</p><p v-if="error" class="notice error" role="alert">{{ error }}</p><form class="form-stack" novalidate @submit.prevent="submit"><label class="field">Correo o usuario<span class="input-wrap"><span class="input-icon">✉</span><input v-model.trim="login" class="input" autocomplete="username" placeholder="nombre@taller.com" /></span><span v-if="submitted && login.length < 3" class="field-error">Ingresa tu correo o usuario.</span></label><label class="field">Contraseña<span class="input-wrap"><span class="input-icon">⌁</span><input v-model="password" class="input" type="password" autocomplete="current-password" placeholder="Tu contraseña" /></span><span v-if="submitted && password.length < 8" class="field-error">Debe tener al menos 8 caracteres.</span></label><button class="primary-button" type="submit" :disabled="loading">{{ loading ? 'Ingresando…' : 'Iniciar sesión →' }}</button></form><div class="form-footer"><RouterLink to="/register">Crear cuenta</RouterLink><RouterLink to="/forgot-password">¿Olvidaste tu contraseña?</RouterLink></div></AuthLayout></template>
