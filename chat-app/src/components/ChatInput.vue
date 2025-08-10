<template>
  <div class="input-container">
    <div class="input-wrapper">
      <textarea
        ref="textareaRef"
        v-model="inputText"
        class="message-input"
        placeholder="Type your message..."
        :disabled="isLoading"
        @keydown="handleKeydown"
        @input="adjustHeight"
        rows="1"
      />
      <button class="send-button" :disabled="!canSend" @click="handleSend">
        <span v-if="isLoading" class="loading-spinner">⏳</span>
        <span v-else>Send</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from "vue";

interface Props {
  isLoading: boolean;
}

interface Emits {
  (e: "send", message: string): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const inputText = ref("");
const textareaRef = ref<HTMLTextAreaElement>();

const canSend = computed(() => {
  return !props.isLoading && inputText.value.trim().length > 0;
});

function handleSend() {
  if (canSend.value) {
    emit("send", inputText.value.trim());
    inputText.value = "";
    resetHeight();
  }
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    handleSend();
  }
}

function adjustHeight() {
  nextTick(() => {
    if (textareaRef.value) {
      textareaRef.value.style.height = "auto";
      textareaRef.value.style.height =
        Math.min(textareaRef.value.scrollHeight, 120) + "px";
    }
  });
}

function resetHeight() {
  nextTick(() => {
    if (textareaRef.value) {
      textareaRef.value.style.height = "auto";
    }
  });
}

onMounted(() => {
  if (textareaRef.value) {
    textareaRef.value.focus();
  }
});
</script>

<style scoped>
.input-container {
  padding: var(--spacing-lg, 1.5rem);
  background-color: var(--color-surface);
  border-top: 1px solid var(--color-border);
}

.input-wrapper {
  display: flex;
  gap: var(--spacing-md, 1rem);
  align-items: flex-end;
  max-width: 100%;
}

.message-input {
  flex: 1;
  padding: var(--spacing-md, 1rem) var(--spacing-lg, 1.5rem);
  border: 2px solid var(--color-input-border);
  border-radius: var(--radius-lg, 0.75rem);
  font-size: 1rem;
  background-color: var(--color-input-background);
  color: var(--color-text);
  transition: all 0.2s ease;
  resize: none;
  min-height: 56px;
  max-height: 120px;
  line-height: 1.5;
  font-family: inherit;
}

.message-input:focus {
  outline: none;
  border-color: var(--color-input-focus);
  box-shadow: 0 0 0 3px var(--color-input-focus);
}

.message-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.message-input::placeholder {
  color: var(--color-text-muted);
}

.send-button {
  padding: var(--spacing-md, 1rem) var(--spacing-lg, 1.5rem);
  background-color: var(--color-primary);
  color: var(--color-chat-bubble-user-text);
  border: none;
  border-radius: var(--radius-lg, 0.75rem);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  min-height: 56px;
  white-space: nowrap;
}

.send-button:hover:not(:disabled) {
  background-color: var(--color-primary-hover);
  transform: translateY(-1px);
}

.send-button:active:not(:disabled) {
  transform: translateY(0);
}

.send-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
