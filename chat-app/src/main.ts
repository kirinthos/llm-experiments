/**
 * Main chat application entry point
 */

import './style.css';
import { ChatApp } from './chat/ChatApp';

// Initialize the chat application
const app = new ChatApp();
app.mount('#app').catch(error => {
  console.error('Failed to initialize chat app:', error);
  document.querySelector('#app')!.innerHTML = `
    <div style="padding: 2rem; text-align: center; color: #ef4444;">
      <h2>❌ Failed to Initialize</h2>
      <p>Could not connect to the chat service. Please try refreshing the page.</p>
      <pre style="margin-top: 1rem; padding: 1rem; background: #f3f4f6; border-radius: 8px; text-align: left; font-size: 0.875rem;">${error.message}</pre>
    </div>
  `;
});

// Handle page unload to save state
window.addEventListener('beforeunload', () => {
  app.cleanup();
});