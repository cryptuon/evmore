import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './style.css'
import { useNetworkStore } from '@/stores/network'

const app = createApp(App)

const pinia = createPinia()
app.use(pinia)
app.use(router)

const networkStore = useNetworkStore()
networkStore.loadConfig().then(() => networkStore.startPolling())

app.mount('#app')
