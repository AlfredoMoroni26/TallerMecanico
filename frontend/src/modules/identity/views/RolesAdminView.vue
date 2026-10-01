<script setup lang="ts">
import { onMounted, ref } from 'vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import http, { getErrorMessage } from '@/api/http'
import type { Role } from '../types'
const roles = ref<Role[]>([]); const error = ref(''); const dialog = ref(false); const name = ref(''); const description = ref(''); const saving = ref(false)
async function load() { try { roles.value = (await http.get<Role[]>('/roles')).data } catch (e) { error.value = getErrorMessage(e) } }
async function create() { if (!/^[a-z_]{3,80}$/.test(name.value)) { error.value = 'El rol debe usar minúsculas y guiones bajos.'; return } saving.value = true; try { await http.post('/roles', { name: name.value, description: description.value || null }); dialog.value = false; name.value = ''; description.value = ''; await load() } catch (e) { error.value = getErrorMessage(e) } finally { saving.value = false } }
async function remove(role: Role) { if (!confirm(`¿Eliminar el rol ${role.name}?`)) return; try { await http.delete(`/roles/${role.id}`); await load() } catch (e) { error.value = getErrorMessage(e) } }
onMounted(load)
</script>
<template><AdminLayout><div class="d-flex align-center mb-5"><h1 class="text-h5">Administración de roles</h1><v-spacer/><v-btn color="primary" prepend-icon="mdi-plus" @click="dialog = true">Nuevo rol</v-btn></div><v-alert v-if="error" type="error" class="mb-4" closable @click:close="error = ''">{{ error }}</v-alert><v-table><thead><tr><th>Nombre</th><th>Descripción</th><th>Tipo</th><th/></tr></thead><tbody><tr v-for="role in roles" :key="role.id"><td>{{ role.name }}</td><td>{{ role.description || '—' }}</td><td>{{ role.is_system ? 'Sistema' : 'Personalizado' }}</td><td><v-btn v-if="!role.is_system" color="error" variant="text" size="small" @click="remove(role)">Eliminar</v-btn></td></tr></tbody></v-table><v-dialog v-model="dialog" max-width="520"><v-card title="Crear rol"><v-card-text><v-text-field v-model.trim="name" label="Nombre" hint="Ejemplo: jefe_operaciones"/><v-text-field v-model.trim="description" label="Descripción"/></v-card-text><v-card-actions><v-spacer/><v-btn @click="dialog = false">Cancelar</v-btn><v-btn color="primary" :loading="saving" @click="create">Guardar</v-btn></v-card-actions></v-card></v-dialog></AdminLayout></template>
