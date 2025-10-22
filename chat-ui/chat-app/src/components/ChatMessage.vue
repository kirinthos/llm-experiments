<template>
  <div class="message" :class="messageClass">
    <div class="message-content">
      <div v-if="showHeader" class="message-header">
        <span class="message-role">{{ headerText }}</span>
        <span class="message-time">{{ formattedTime }}</span>
      </div>
      <ThinkingProcess
        v-if="shouldShowThinking && message.thinkingSteps"
        :thinking-steps="message.thinkingSteps"
      />
      <div class="message-text">
        <MarkdownRenderer
          v-if="shouldRenderMarkdown"
          :content="message.content"
          @citations="handleCitations"
        />
        <span v-else>{{ message.content }}</span>
      </div>
      <CitationPills v-if="citations.length > 0" :citations="citations" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import type { Message } from "../types";
import MarkdownRenderer from "./MarkdownRenderer.vue";
import CitationPills from "./CitationPills.vue";
import ThinkingProcess from "./ThinkingProcess.vue";

interface Citation {
  id: number;
  url: string;
  title: string;
  domain: string;
}

interface Props {
  message: Message;
}

const props = defineProps<Props>();

const citations = ref<Citation[]>([]);

const messageClass = computed(() => {
  return {
    "user-message": props.message.role === "user",
    "assistant-message": props.message.role === "assistant",
    "system-message": props.message.role === "system",
  };
});

const showHeader = computed(() => {
  return props.message.role !== "system";
});

const headerText = computed(() => {
  switch (props.message.role) {
    case "user":
      return "You";
    case "assistant":
      return "Assistant";
    default:
      return "";
  }
});

const formattedTime = computed(() => {
  const date = new Date(props.message.timestamp);
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
});

// Determine if we should render markdown (for assistant messages)
const shouldRenderMarkdown = computed(() => {
  return props.message.role === "assistant" && props.message.content.length > 0;
});

// Determine if we should show thinking process (for assistant messages with thinking steps)
const shouldShowThinking = computed(() => {
  return (
    props.message.role === "assistant" &&
    props.message.thinkingSteps &&
    props.message.thinkingSteps.length > 0
  );
});

// Handle citations from markdown renderer
const handleCitations = (newCitations: Citation[]) => {
  citations.value = newCitations;
};
</script>

<style scoped>
.message {
  display: flex;
  margin-bottom: var(--spacing-lg, 1.5rem);
  animation: fadeInUp 0.3s ease;
}

.message-content {
  max-width: 80%;
  padding: var(--spacing-md, 1rem) var(--spacing-lg, 1.5rem);
  border-radius: var(--radius-lg, 0.75rem);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border);
}

.user-message .message-content {
  background-color: var(--color-chat-bubble-user);
  color: var(--color-chat-bubble-user-text);
  margin-left: auto;
  border-color: var(--color-chat-bubble-user);
}

.assistant-message .message-content {
  background-color: var(--color-chat-bubble-assistant);
  color: var(--color-chat-bubble-assistant-text);
  margin-right: auto;
}

.system-message .message-content {
  background-color: var(--color-surface);
  color: var(--color-text-muted);
  margin: 0 auto;
  max-width: 60%;
  text-align: center;
  font-size: 0.875rem;
  font-style: italic;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-sm, 0.5rem);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.user-message .message-header {
  color: rgba(255, 255, 255, 0.8);
}

.assistant-message .message-header {
  color: var(--color-text-muted);
}

.message-text {
  font-size: 0.95rem;
  line-height: 1.6;
  word-wrap: break-word;
}

/* Keep simple styling for user messages (non-markdown) */
.user-message .message-text span {
  white-space: pre-wrap;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
