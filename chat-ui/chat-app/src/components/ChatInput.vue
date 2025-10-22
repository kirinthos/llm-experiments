<template>
  <div class="input-container">
    <div class="input-wrapper">
      <textarea
        ref="textareaRef"
        v-model="inputText"
        class="message-input"
        :placeholder="
          isDisabled
            ? 'Cannot send messages - connection error'
            : 'Type your message...'
        "
        :disabled="isLoading || isDisabled"
        @keydown="handleKeydown"
        @input="adjustHeight"
        rows="1"
      />
      <button
        class="send-button"
        :disabled="!canSend || isDisabled"
        @click="handleSend"
      >
        <span v-if="isLoading" class="loading-spinner">⏳</span>
        <svg
          v-else
          class="send-icon"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="m3 3 3 9-3 9 19-9Z" />
          <path d="m6 12 13 0" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from "vue";

interface Props {
  isLoading: boolean;
  isDisabled?: boolean;
  errorMessage?: string;
}

interface Emits {
  (e: "send", message: string): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const inputText = ref("");
const textareaRef = ref<HTMLTextAreaElement>();

const canSend = computed(() => {
  return (
    !props.isLoading && !props.isDisabled && inputText.value.trim().length > 0
  );
});

function handleSend() {
  if (canSend.value) {
    emit("send", inputText.value.trim());
    inputText.value = "";
    resetHeight();
  }
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === "Enter" && !event.shiftKey && !props.isDisabled) {
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
  padding: 0;
  background-color: var(--color-surface);
  border-top: 1px solid var(--color-border);
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  max-width: 100%;
}

.message-input {
  flex: 1;
  padding: var(--spacing-lg, 1.5rem);
  border: none;
  border-radius: 0;
  font-size: 1rem;
  background-color: var(--color-input-background);
  color: var(--color-text);
  transition: all 0.2s ease;
  resize: none;
  min-height: 64px;
  max-height: 120px;
  line-height: 1.5;
  font-family: inherit;
}

.message-input:focus {
  outline: none;
  background-color: var(--color-surface);
}

.message-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.message-input::placeholder {
  color: var(--color-text-muted);
}

.send-button {
  padding: var(--spacing-lg, 1.5rem);
  background-color: var(--color-primary);
  color: var(--color-chat-bubble-user-text);
  border: none;
  border-radius: 0;
  cursor: pointer;
  transition: all 0.2s ease;
  min-height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 64px;
}

.send-button:hover:not(:disabled) {
  background-color: var(--color-primary-hover);
}

.send-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.send-icon {
  transform: rotate(0deg);
  transition: transform 0.2s ease;
}

.send-button:hover:not(:disabled) .send-icon {
  transform: rotate(15deg);
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
