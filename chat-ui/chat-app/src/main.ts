/**
 * Main entry point for the Universal AI Chat application
 */

import { createApp } from 'vue'
import App from './App.vue'
import './style.css'
import { loadConfig } from './config'

// Load configuration before starting the app
loadConfig().then(() => {
  console.log('✅ Configuration loaded, starting app...');
  const app = createApp(App);
  app.mount('#app');
}).catch((error) => {
  console.warn('⚠️ Failed to load configuration, using defaults:', error);
  const app = createApp(App);
  app.mount('#app');
});