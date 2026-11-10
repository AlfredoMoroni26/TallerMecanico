<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/modules/identity/stores/auth'
const router = useRouter(); const auth = useAuthStore()
const isAdmin = () => auth.hasRole('administrador_taller')
const canRegisterWorkshop = () => auth.hasRole(['administrador_taller', 'recepcionista', 'secretaria'])
const canManageClients = () => auth.hasRole(['administrador_taller', 'recepcionista'])
async function logout() { await auth.logout(); await router.push('/login') }
</script>
<template><main class="console"><header class="console-header"><RouterLink class="console-brand" to="/"><span class="brand-mark">⚙</span><span>Taller Mecánico</span></RouterLink><nav class="console-nav"><RouterLink to="/">Inicio</RouterLink><RouterLink v-if="canManageClients()" to="/clients">Clientes</RouterLink><RouterLink v-if="canManageClients()" to="/vehicles/new">Registrar vehículo</RouterLink><RouterLink v-if="canRegisterWorkshop()" to="/workshops/new">Alta de taller</RouterLink><RouterLink v-if="isAdmin()" to="/admin/users">Usuarios</RouterLink><RouterLink v-if="isAdmin()" to="/admin/roles">Administrar roles</RouterLink><RouterLink v-if="isAdmin()" to="/admin/roles/create">Crear rol</RouterLink></nav><div class="console-account"><span>{{ auth.user?.username }}</span><button class="text-button" @click="logout">Salir</button></div></header><section class="console-content"><slot /></section></main></template>
