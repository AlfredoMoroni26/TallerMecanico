<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import AdminShell from '@/layouts/AdminShell.vue'
import http, { getErrorMessage } from '@/api/http'

type Client = {
  id: string
  first_name: string
  paternal_last_name: string
  maternal_last_name: string
}

type Vehicle = {
  id: string
  client_id: string
  client_name: string
  vin: string
  plate: string
  brand: string
  model: string
  year: number
  version: string
  color: string
  mileage: number | null
  photo_path: string | null
  is_active: boolean
}

type VehicleForm = {
  client_id: string
  vin: string
  plate: string
  brand: string
  model: string
  year: number
  version: string
  color: string
  mileage: string
}

type VehicleUpdateForm = Omit<VehicleForm, 'client_id' | 'vin'>

const blankForm = (): VehicleForm => ({
  client_id: '', vin: '', plate: '', brand: '', model: '',
  year: new Date().getFullYear(), version: '', color: '', mileage: '',
})

const clients = ref<Client[]>([])
const vehicles = ref<Vehicle[]>([])
const form = ref<VehicleForm>(blankForm())
const editForm = ref<VehicleUpdateForm>({ plate: '', brand: '', model: '', year: new Date().getFullYear(), version: '', color: '', mileage: '' })
const photo = ref<File | null>(null)
const preview = ref('')
const selectedVehicle = ref<Vehicle | null>(null)
const modalOpen = ref(false)
const saving = ref(false)
const error = ref('')
const success = ref('')
const submitted = ref(false)
const editSubmitted = ref(false)
const statusVehicle = ref<Vehicle | null>(null)

const sortedVehicles = computed(() => vehicles.value)

function fullName(client: Client): string {
  return `${client.first_name} ${client.paternal_last_name} ${client.maternal_last_name}`
}

function validVehicle(formData: VehicleUpdateForm): boolean {
  return Boolean(
    formData.plate.trim() && formData.brand.trim() && formData.model.trim()
    && formData.year >= 1900 && formData.year <= 2100 && formData.version.trim()
    && formData.color.trim() && formData.mileage !== '' && Number(formData.mileage) >= 0,
  )
}

async function load() {
  try {
    const [clientsResponse, vehiclesResponse] = await Promise.all([
      http.get<Client[]>('/clients', { params: { active_only: true } }),
      http.get<Vehicle[]>('/vehicles'),
    ])
    clients.value = clientsResponse.data
    vehicles.value = vehiclesResponse.data
  } catch (requestError) {
    error.value = getErrorMessage(requestError)
  }
}

function selectPhoto(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0] ?? null
  photo.value = file
  if (preview.value) URL.revokeObjectURL(preview.value)
  preview.value = file ? URL.createObjectURL(file) : ''
}

async function save() {
  submitted.value = true
  const { client_id: _clientId, ...mainData } = form.value
  if (!form.value.client_id || !photo.value || !validVehicle(mainData)) {
    error.value = 'Completa todos los campos obligatorios del vehículo y selecciona una fotografía.'
    return
  }

  saving.value = true
  error.value = ''
  success.value = ''
  try {
    const payload = new FormData()
    Object.entries(form.value).forEach(([key, value]) => payload.append(key, String(value)))
    payload.append('photo', photo.value)
    await http.post('/vehicles', payload, { headers: { 'Content-Type': 'multipart/form-data' } })
    success.value = 'Vehículo registrado correctamente.'
    form.value = blankForm()
    photo.value = null
    if (preview.value) URL.revokeObjectURL(preview.value)
    preview.value = ''
    submitted.value = false
    await load()
  } catch (requestError) {
    error.value = getErrorMessage(requestError)
  } finally {
    saving.value = false
  }
}

function openEdit(vehicle: Vehicle) {
  selectedVehicle.value = vehicle
  editForm.value = {
    plate: vehicle.plate,
    brand: vehicle.brand,
    model: vehicle.model,
    year: vehicle.year,
    version: vehicle.version,
    color: vehicle.color,
    mileage: vehicle.mileage === null ? '' : String(vehicle.mileage),
  }
  editSubmitted.value = false
  error.value = ''
  modalOpen.value = true
}

function requestStatusChange(vehicle: Vehicle) {
  statusVehicle.value = vehicle
}

function closeStatusConfirmation() {
  statusVehicle.value = null
}

async function confirmStatusChange() {
  if (!statusVehicle.value) return
  const vehicle = statusVehicle.value
  const action = vehicle.is_active ? 'deactivate' : 'activate'
  const actionLabel = vehicle.is_active ? 'desactivado' : 'activado'

  saving.value = true
  error.value = ''
  success.value = ''
  try {
    await http.patch(`/vehicles/${vehicle.id}/${action}`)
    closeStatusConfirmation()
    success.value = `Vehículo ${actionLabel} correctamente.`
    await load()
  } catch (requestError) {
    error.value = getErrorMessage(requestError)
  } finally {
    saving.value = false
  }
}

function closeModal() {
  modalOpen.value = false
  selectedVehicle.value = null
  editSubmitted.value = false
}

async function updateVehicle() {
  editSubmitted.value = true
  if (!selectedVehicle.value || !validVehicle(editForm.value)) {
    error.value = 'Completa todos los campos para actualizar el vehículo.'
    return
  }

  saving.value = true
  error.value = ''
  success.value = ''
  try {
    await http.patch(`/vehicles/${selectedVehicle.value.id}`, {
      ...editForm.value,
      mileage: Number(editForm.value.mileage),
    })
    closeModal()
    success.value = 'Datos del vehículo actualizados correctamente.'
    await load()
  } catch (requestError) {
    error.value = getErrorMessage(requestError)
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<template>
  <AdminShell>
    <section class="client-card">
      <p class="eyebrow">Vehículos</p>
      <h1>Registrar vehículo</h1>
      <p class="subtle">Sólo puedes asociarlo a un cliente activo de tu taller.</p>
      <p v-if="error" class="notice error" role="alert">{{ error }}</p>
      <p v-if="success" class="notice success" role="status">{{ success }}</p>

      <form class="client-grid" novalidate @submit.prevent="save">
        <label class="full">Cliente
          <select v-model="form.client_id" required>
            <option value="">Selecciona un cliente activo</option>
            <option v-for="client in clients" :key="client.id" :value="client.id">{{ fullName(client) }}</option>
          </select>
          <span v-if="submitted && !form.client_id">Selecciona un cliente.</span>
        </label>
        <label>VIN / número de serie<input v-model.trim="form.vin" maxlength="17" required><span v-if="submitted && !form.vin">El VIN es obligatorio.</span></label>
        <label>Placa<input v-model.trim="form.plate" required><span v-if="submitted && !form.plate">La placa es obligatoria.</span></label>
        <label>Marca<input v-model.trim="form.brand" required><span v-if="submitted && !form.brand">La marca es obligatoria.</span></label>
        <label>Modelo<input v-model.trim="form.model" required><span v-if="submitted && !form.model">El modelo es obligatorio.</span></label>
        <label>Año<input v-model.number="form.year" type="number" min="1900" max="2100" required><span v-if="submitted && (form.year < 1900 || form.year > 2100)">Ingresa un año válido.</span></label>
        <label>Versión<input v-model.trim="form.version" required><span v-if="submitted && !form.version">La versión es obligatoria.</span></label>
        <label>Color<input v-model.trim="form.color" required><span v-if="submitted && !form.color">El color es obligatorio.</span></label>
        <label>Kilometraje<input v-model="form.mileage" type="number" min="0" required><span v-if="submitted && form.mileage === ''">El kilometraje es obligatorio.</span></label>
        <label class="full photo-drop">Fotografía del vehículo
          <input type="file" accept="image/jpeg,image/png,image/webp" required @change="selectPhoto">
          <span>{{ photo ? photo.name : 'Seleccionar fotografía (JPG, PNG o WEBP, máximo 5 MB)' }}</span>
        </label>
        <img v-if="preview" class="photo-preview full" :src="preview" alt="Vista previa del vehículo">
        <div class="client-actions full"><button class="primary-button" :disabled="saving">{{ saving ? 'Registrando…' : 'Registrar vehículo' }}</button></div>
      </form>
    </section>

    <section class="client-card vehicle-list">
      <div class="client-top"><div><p class="eyebrow">Vehículos del taller</p><h2>Vehículos registrados</h2><p class="subtle">Selecciona un vehículo para actualizar sus datos principales.</p></div></div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Vehículo</th><th>Cliente asociado</th><th>VIN / placa</th><th>Kilometraje</th><th>Estado</th><th class="align-right">Acciones</th></tr></thead>
          <tbody>
            <tr v-for="vehicle in sortedVehicles" :key="vehicle.id">
              <td><strong>{{ vehicle.brand }} {{ vehicle.model }}</strong><small>{{ vehicle.year }} · {{ vehicle.color }} · {{ vehicle.version }}</small></td>
              <td>{{ vehicle.client_name }}</td>
              <td>{{ vehicle.vin }}<small>{{ vehicle.plate }}</small></td>
              <td>{{ vehicle.mileage === null ? 'Sin registro' : `${vehicle.mileage.toLocaleString('es-MX')} km` }}</td>
              <td><span class="client-status" :class="vehicle.is_active ? 'active' : 'inactive'">{{ vehicle.is_active ? 'Activo' : 'Inactivo' }}</span></td>
              <td class="align-right"><button class="table-action" :disabled="saving" @click="openEdit(vehicle)">Actualizar</button><button class="table-action" :class="vehicle.is_active ? 'danger-action' : ''" :disabled="saving" @click="requestStatusChange(vehicle)">{{ vehicle.is_active ? 'Desactivar' : 'Activar' }}</button></td>
            </tr>
            <tr v-if="!sortedVehicles.length"><td colspan="6" class="empty-state">No hay vehículos registrados en tu taller.</td></tr>
          </tbody>
        </table>
      </div>
    </section>

    <div v-if="modalOpen && selectedVehicle" class="modal-backdrop" @click.self="closeModal">
      <section class="modal-card vehicle-modal" role="dialog" aria-modal="true" aria-labelledby="vehicle-update-title">
        <div class="modal-title"><div><p class="eyebrow">Actualizar vehículo</p><h2 id="vehicle-update-title">{{ selectedVehicle.brand }} {{ selectedVehicle.model }}</h2></div><button class="close-button" aria-label="Cerrar" @click="closeModal">×</button></div>
        <p class="vehicle-client">Cliente asociado: <strong>{{ selectedVehicle.client_name }}</strong></p>
        <p class="subtle">El cliente y el taller se conservan; sólo puedes actualizar los datos principales del vehículo.</p>
        <form class="client-grid" novalidate @submit.prevent="updateVehicle">
          <label>VIN / número de serie<input :value="selectedVehicle.vin" readonly><small>El VIN se conserva y no puede modificarse.</small></label>
          <label>Placa<input v-model.trim="editForm.plate" required><span v-if="editSubmitted && !editForm.plate">La placa es obligatoria.</span></label>
          <label>Marca<input v-model.trim="editForm.brand" required><span v-if="editSubmitted && !editForm.brand">La marca es obligatoria.</span></label>
          <label>Modelo<input v-model.trim="editForm.model" required><span v-if="editSubmitted && !editForm.model">El modelo es obligatorio.</span></label>
          <label>Año<input v-model.number="editForm.year" type="number" min="1900" max="2100" required><span v-if="editSubmitted && (editForm.year < 1900 || editForm.year > 2100)">Ingresa un año válido.</span></label>
          <label>Versión<input v-model.trim="editForm.version" required><span v-if="editSubmitted && !editForm.version">La versión es obligatoria.</span></label>
          <label>Color<input v-model.trim="editForm.color" required><span v-if="editSubmitted && !editForm.color">El color es obligatorio.</span></label>
          <label>Kilometraje<input v-model="editForm.mileage" type="number" min="0" required><span v-if="editSubmitted && editForm.mileage === ''">El kilometraje es obligatorio.</span></label>
          <div class="client-actions full"><button type="button" class="secondary-button" @click="closeModal">Cancelar</button><button class="primary-button" :disabled="saving">{{ saving ? 'Actualizando…' : 'Guardar cambios' }}</button></div>
        </form>
      </section>
    </div>

    <div v-if="statusVehicle" class="modal-backdrop" @click.self="closeStatusConfirmation">
      <section class="modal-card confirmation-modal" role="dialog" aria-modal="true" aria-labelledby="vehicle-status-title">
        <div class="modal-title"><div><p class="eyebrow">Confirmar acción</p><h2 id="vehicle-status-title">{{ statusVehicle.is_active ? 'Desactivar vehículo' : 'Activar vehículo' }}</h2></div><button class="close-button" aria-label="Cerrar" @click="closeStatusConfirmation">×</button></div>
        <p>¿Estás seguro de que deseas {{ statusVehicle.is_active ? 'desactivar' : 'activar' }} el vehículo <strong>{{ statusVehicle.brand }} {{ statusVehicle.model }}</strong>?</p>
        <p class="subtle">El vehículo conservará su historial y su asociación con {{ statusVehicle.client_name }}.</p>
        <div class="modal-actions"><button type="button" class="secondary-button" :disabled="saving" @click="closeStatusConfirmation">Cancelar</button><button class="primary-button" :disabled="saving" @click="confirmStatusChange">{{ saving ? 'Procesando…' : statusVehicle.is_active ? 'Sí, desactivar' : 'Sí, activar' }}</button></div>
      </section>
    </div>
  </AdminShell>
</template>
