import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify'
import './styles/main.css'
import './styles/admin.css'
import './styles/fase2-roles.css'
import './styles/fase3-administrar-roles.css'
import './styles/fase4-alta-taller.css'
import './styles/clients.css'

createApp(App).use(createPinia()).use(router).use(vuetify).mount('#app')
