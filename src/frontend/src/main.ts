import { createApp } from 'vue'
import { Icon } from '@iconify/vue'
import './style.css'
import App from './App.vue'
import router from './router';
import { createPinia } from 'pinia'
import persistState from 'pinia-plugin-persistedstate';
import UI from './components/ui'

const app = createApp(App)
const pinia = createPinia();
pinia.use(persistState);

app.component('Icon', Icon)
app.use(router);
app.use(pinia);
app.use(UI);
app.mount('#app')
