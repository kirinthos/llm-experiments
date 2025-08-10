<template>
  <div class="chat-container">
    <!-- Header -->
    <header class="header">
      <div class="header-left">
        <h1 class="app-title">Universal AI Chat</h1>
        <div class="connection-status" :class="{ 'test-mode': !useRealAPI }">
          {{ useRealAPI ? "🟢 Connected to API" : "🟡 Test Mode" }}
        </div>
      </div>

      <div class="header-right">
        <ModelSelector
          :available-models="availableModels"
          :current-model="currentModel"
          @change="changeModel"
        />

        <ToolsDropdown
          :available-tools="availableTools"
          :tools-enabled="toolsEnabled"
          @toggle="toggleTools"
        />

        <ThemeSelector />

        <button class="clear-button" @click="clearChat">🗑️ Clear</button>
      </div>
    </header>

    <!-- Messages -->
    <div class="messages-container" ref="messagesRef">
      <div v-if="messages.length === 0" class="welcome-message">
        <h2>Welcome to Universal AI Chat! 🤖</h2>
        <p>Start a conversation with your AI assistant.</p>
        <div class="example-prompts">
          <h3>Try asking:</h3>
          <ul>
            <li>"Convert 72°F to Celsius"</li>
            <li>"Generate 2 random numbers and add them"</li>
            <li>"What's the current time?"</li>
            <li v-if="useRealAPI">"Take a screenshot of google.com"</li>
          </ul>
        </div>
      </div>

      <ChatMessage
        v-for="message in messages"
        :key="message.id"
        :message="message"
      />

      <div v-if="isLoading" class="loading-indicator">
        <div class="loading-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
        <span class="loading-text">AI is thinking...</span>
      </div>
    </div>

    <!-- Input -->
    <ChatInput :is-loading="isLoading" @send="sendMessage" />
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch, onMounted } from "vue";
import { useChat } from "../composables/useChat";
import ChatMessage from "./ChatMessage.vue";
import ChatInput from "./ChatInput.vue";
import ModelSelector from "./ModelSelector.vue";
import ToolsDropdown from "./ToolsDropdown.vue";
import ThemeSelector from "./ThemeSelector.vue";

const {
  messages,
  currentModel,
  availableModels,
  isLoading,
  useRealAPI,
  availableTools,
  toolsEnabled,
  initialize,
  sendMessage,
  changeModel,
  clearChat,
  toggleTools,
} = useChat();

const messagesRef = ref<HTMLElement>();

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight;
    }
  });
}

// Watch for new messages and scroll to bottom
watch(
  messages,
  () => {
    scrollToBottom();
  },
  { deep: true }
);

// Watch for loading state changes and scroll to bottom
watch(isLoading, () => {
  scrollToBottom();
});

onMounted(async () => {
  await initialize();
  scrollToBottom();
});
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: var(--color-background);
  color: var(--color-text);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg, 1.5rem);
  background-color: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-md, 1rem);
}

.app-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text);
}

.connection-status {
  padding: var(--spacing-xs, 0.25rem) var(--spacing-sm, 0.5rem);
  background-color: var(--color-success);
  color: white;
  border-radius: var(--radius-md, 0.5rem);
  font-size: 0.75rem;
  font-weight: 600;
}

.connection-status.test-mode {
  background-color: var(--color-warning);
  color: var(--color-text);
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-md, 1rem);
}

.clear-button {
  padding: var(--spacing-sm, 0.5rem) var(--spacing-md, 1rem);
  background-color: var(--color-danger);
  color: white;
  border: none;
  border-radius: var(--radius-md, 0.5rem);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.clear-button:hover {
  background-color: var(--color-danger);
  opacity: 0.8;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-lg, 1.5rem);
  scroll-behavior: smooth;
}

.welcome-message {
  text-align: center;
  padding: var(--spacing-xl, 2rem);
  color: var(--color-text-secondary);
}

.welcome-message h2 {
  margin: 0 0 var(--spacing-md, 1rem) 0;
  color: var(--color-text);
}

.welcome-message p {
  margin: 0 0 var(--spacing-lg, 1.5rem) 0;
  font-size: 1.1rem;
}

.example-prompts {
  max-width: 400px;
  margin: 0 auto;
  text-align: left;
}

.example-prompts h3 {
  margin: 0 0 var(--spacing-sm, 0.5rem) 0;
  color: var(--color-text);
  font-size: 1rem;
}

.example-prompts ul {
  margin: 0;
  padding-left: var(--spacing-lg, 1.5rem);
}

.example-prompts li {
  margin-bottom: var(--spacing-xs, 0.25rem);
  font-style: italic;
  color: var(--color-text-muted);
}

.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm, 0.5rem);
  padding: var(--spacing-lg, 1.5rem);
  color: var(--color-text-secondary);
}

.loading-dots {
  display: flex;
  gap: var(--spacing-xs, 0.25rem);
}

.loading-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--color-primary);
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

.loading-text {
  font-size: 0.875rem;
  font-style: italic;
}

@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

/* Scrollbar styling */
.messages-container::-webkit-scrollbar {
  width: 8px;
}

.messages-container::-webkit-scrollbar-track {
  background: var(--color-surface);
}

.messages-container::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 4px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-muted);
}
</style>
