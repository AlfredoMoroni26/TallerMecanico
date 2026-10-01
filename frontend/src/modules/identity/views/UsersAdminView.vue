<script setup lang="ts">
import { onMounted, ref } from 'vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import http, { getErrorMessage } from '@/api/http'
import type { Role, User } from '../types'

const users = ref<User[]>([]); const roles = ref<Role[]>([]); const error = ref(''); const dialog = ref(false); const saving = ref(false)
const blank = () => ({ username: '', email: '', password: '', role_ids: [] as string[] })
const form = ref(blank())
async function load() { try { [users.value, roles.value] = await Promise.all([http.get<User[]>('/users').then(r => r.data), http.get<Role[]>('/roles').then(r => r.data)]) } catch (e) { error.value = getErrorMessage(e) } }
async function create() {
  if (!/^[a-zA-Z0-9_.-]{3,50}$/.test(form.value.username)) { error.value = 'El usuario debe tener de 3 a 50 caracteres válidos.'; return }
  if (!/.+@.+\..+/.test(form.value.email)) { error.value = 'Ingresa un correo válido.'; return }
  if (!/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/.test(form.value.password)) { error.value = 'La contraseña debe incluir 8 caracteres, mayúscula, minúscula y número.'; return }
  if (!form.value.role_ids.length) { error.value = 'Selecciona al menos un rol.'; return }
  saving.value = true; error.value = ''; try { await http.post('/users', form.value); dialog.value = false; form.value = blank(); await load() } catch (e) { error.value = getErrorMessage(e) } finally { saving.value = false }
}
async function toggle(user: User) { try { await http.patch(`/users/${user.id}`, { is_active: !user.is_active }); await load() } catch (e) { error.value = getErrorMessage(e) } }
onMounted(load)
</script>
<template><AdminLayout><div class="d-flex align-center mb-5"><h1 class="text-h5">Administración de usuarios</h1><v-spacer/><v-btn color="primary" prepend-icon="mdi-account-plus" @click="dialog = true">Nuevo usuario</v-btn></div><v-alert v-if="error" type="error" class="mb-4" closable @click:close="error = ''">{{ error }}</v-alert><v-table><thead><tr><th>Usuario</th><th>Correo</th><th>Roles</th><th>Estado</th><th>Acción</th></tr></thead><tbody><tr v-for="user in users" :key="user.id"><td>{{ user.username }}</td><td>{{ user.email }}</td><td><v-chip v-for="role in user.roles" :key="role.id" size="small" class="mr-1">{{ role.name }}</v-chip></td><td><v-chip :color="user.is_active ? 'success' : 'error'" size="small">{{ user.is_active ? 'Activo' : 'Inactivo' }}</v-chip></td><td><v-btn size="small" variant="text" @click="toggle(user)">{{ user.is_active ? 'Desactivar' : 'Activar' }}</v-btn></td></tr></tbody></v-table><v-dialog v-model="dialog" max-width="520"><v-card title="Crear usuario"><v-card-text><v-text-field v-model.trim="form.username" label="Nombre de usuario"/><v-text-field v-model.trim="form.email" label="Correo" type="email"/><v-text-field v-model="form.password" label="Contraseña" type="password" hint="Mayúscula, minúscula, número y 8 caracteres."/><v-select v-model="form.role_ids" :items="roles" item-title="name" item-value="id" label="Roles" multiple chips/></v-card-text><v-card-actions><v-spacer/><v-btn @click="dialog = false">Cancelar</v-btn><v-btn color="primary" :loading="saving" @click="create">Guardar</v-btn></v-card-actions></v-card></v-dialog></AdminLayout></template>
