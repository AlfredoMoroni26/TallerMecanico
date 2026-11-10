<script setup lang="ts">
import { ref } from 'vue'
import AdminShell from '@/layouts/AdminShell.vue'
import http, { getErrorMessage } from '@/api/http'

const name = ref('')
const saving = ref(false)
const submitted = ref(false)
const error = ref('')
const success = ref('')
const valid = () => name.value.trim().length >= 3 && name.value.trim().length <= 80

async function createRole() {
  submitted.value = true
  success.value = ''
  error.value = ''
  if (!valid()) return
  saving.value = true
  try {
    const { data } = await http.post<{ id_rol: number; name: string }>('/roles', { name: name.value })
    success.value = `El rol “${data.name.replaceAll('_', ' ')}” fue registrado correctamente con el ID ${data.id_rol}.`
    name.value = ''
    submitted.value = false
  } catch (exception) {
    error.value = getErrorMessage(exception)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <AdminShell>
    <section class="create-role-page">
      <div class="create-role-copy">
        <p class="eyebrow">Fase 2 · Identidad y acceso</p>
        <h1>Crear nuevo rol</h1>
        <p>Registra un rol para ampliar la estructura de acceso del sistema.</p>
      </div>

      <section class="create-role-card" aria-labelledby="create-role-title">
        <div class="create-role-icon">＋</div>
        <h2 id="create-role-title">Datos del rol</h2>
        <p class="subtle">El nombre se normaliza para evitar duplicados por mayúsculas o espacios adicionales.</p>

        <p v-if="error" class="notice error" role="alert">{{ error }}</p>
        <p v-if="success" class="notice success" role="status">{{ success }}</p>

        <form class="create-role-form" novalidate @submit.prevent="createRole">
          <label for="role-name">Nombre del rol</label>
          <input id="role-name" v-model="name" maxlength="80" autocomplete="off" placeholder="Ej. Supervisor de taller" autofocus />
          <span v-if="submitted && !valid()" class="field-error">Ingresa un nombre de entre 3 y 80 caracteres.</span>
          <p class="field-hint">Se guardará en formato estándar: <strong>{{ name.trim() ? name.trim().toLowerCase().split(/\s+/).join('_') : 'supervisor_de_taller' }}</strong></p>
          <button class="primary-button" type="submit" :disabled="saving">{{ saving ? 'Registrando…' : 'Registrar rol' }}</button>
        </form>
      </section>
    </section>
  </AdminShell>
</template>
