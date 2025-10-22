<template>
  <div v-if="thinkingSteps.length > 0" class="thinking-container">
    <button
      class="thinking-toggle"
      @click="isExpanded = !isExpanded"
      :class="{ expanded: isExpanded }"
    >
      <div class="toggle-content">
        <div class="toggle-icon">
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            :class="{ rotated: isExpanded }"
          >
            <polyline points="6,9 12,15 18,9"></polyline>
          </svg>
        </div>
        <span class="toggle-text">
          {{ isExpanded ? "Hide" : "Show" }} thinking process
        </span>
        <div class="step-summary">
          {{ thinkingSteps.length }} step{{
            thinkingSteps.length !== 1 ? "s" : ""
          }}
          <span v-if="totalDuration" class="duration">
            • {{ formatDuration(totalDuration) }}
          </span>
        </div>
      </div>
    </button>

    <Transition name="thinking-expand">
      <div v-if="isExpanded" class="thinking-steps">
        <div
          v-for="(step, index) in thinkingSteps"
          :key="index"
          class="thinking-step"
          :class="`step-${step.type}`"
        >
          <div class="step-header">
            <div class="step-icon">
              <component :is="getStepIcon(step.type)" />
            </div>
            <div class="step-info">
              <h4 class="step-title">{{ step.title }}</h4>
              <div class="step-meta">
                <span class="step-time">{{ formatTime(step.timestamp) }}</span>
                <span v-if="step.duration_ms" class="step-duration">
                  {{ formatDuration(step.duration_ms) }}
                </span>
                <span class="step-type">{{ formatStepType(step.type) }}</span>
              </div>
            </div>
          </div>

          <div class="step-content">
            <div class="step-text">{{ step.content }}</div>

            <!-- Metadata display for certain step types -->
            <div
              v-if="step.metadata && Object.keys(step.metadata).length > 0"
              class="step-metadata"
            >
              <div v-if="step.type === 'tool_execution'" class="tool-args">
                <strong>Arguments:</strong>
                <code>{{
                  JSON.stringify(step.metadata.arguments, null, 2)
                }}</code>
              </div>
              <div
                v-else-if="step.type === 'tool_result'"
                class="tool-result-meta"
              >
                <span
                  class="result-status"
                  :class="{
                    success: step.metadata.success,
                    error: !step.metadata.success,
                  }"
                >
                  {{ step.metadata.success ? "✓" : "✗" }}
                </span>
                <span class="result-size"
                  >{{ step.metadata.result_length }} characters</span
                >
              </div>
              <div
                v-else-if="step.type === 'tool_planning'"
                class="tool-planning-meta"
              >
                <strong>{{ step.metadata.tool_count }} tools available</strong>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";

interface ThinkingStep {
  type: string;
  title: string;
  content: string;
  timestamp: string;
  duration_ms?: number;
  metadata?: Record<string, any>;
}

interface Props {
  thinkingSteps: ThinkingStep[];
}

const props = defineProps<Props>();

const isExpanded = ref(false);

const totalDuration = computed(() => {
  return props.thinkingSteps
    .filter((step) => step.duration_ms)
    .reduce((total, step) => total + (step.duration_ms || 0), 0);
});

const formatDuration = (ms: number): string => {
  if (ms < 1000) return `${ms}ms`;
  const seconds = (ms / 1000).toFixed(1);
  return `${seconds}s`;
};

const formatTime = (timestamp: string): string => {
  const date = new Date(timestamp);
  return date.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    fractionalSecondDigits: 1,
  });
};

const formatStepType = (type: string): string => {
  return type.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
};

const getStepIcon = (type: string) => {
  const icons = {
    user_input: "UserIcon",
    tool_planning: "PlanIcon",
    tool_execution: "ExecuteIcon",
    tool_result: "ResultIcon",
    reasoning: "BrainIcon",
    final_response: "CheckIcon",
  };
  return icons[type as keyof typeof icons] || "DefaultIcon";
};

// Icon components as simple SVGs
const UserIcon = () => `
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
    <circle cx="12" cy="7" r="4"></circle>
  </svg>
`;

const PlanIcon = () => `
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
    <line x1="9" y1="9" x2="15" y2="9"></line>
    <line x1="9" y1="12" x2="15" y2="12"></line>
    <line x1="9" y1="15" x2="13" y2="15"></line>
  </svg>
`;

const ExecuteIcon = () => `
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <polygon points="5,3 19,12 5,21 5,3"></polygon>
  </svg>
`;

const ResultIcon = () => `
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
    <polyline points="14,2 14,8 20,8"></polyline>
    <line x1="16" y1="13" x2="8" y2="13"></line>
    <line x1="16" y1="17" x2="8" y2="17"></line>
    <polyline points="10,9 9,9 8,9"></polyline>
  </svg>
`;

const BrainIcon = () => `
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <circle cx="12" cy="12" r="3"></circle>
    <path d="M12 1v6m0 6v6"></path>
    <path d="m21 12-6-6-6 6-6-6"></path>
  </svg>
`;

const CheckIcon = () => `
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <polyline points="20,6 9,17 4,12"></polyline>
  </svg>
`;

const DefaultIcon = () => `
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <circle cx="12" cy="12" r="10"></circle>
    <line x1="12" y1="16" x2="12" y2="12"></line>
    <line x1="12" y1="8" x2="12.01" y2="8"></line>
  </svg>
`;
</script>

<style scoped>
.thinking-container {
  margin: 1rem 0;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md, 0.5rem);
  background: var(--color-surface);
  overflow: hidden;
}

.thinking-toggle {
  width: 100%;
  background: transparent;
  border: none;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: var(--radius-md, 0.5rem);
}

.thinking-toggle:hover {
  background: rgba(var(--color-primary-rgb, 0, 123, 255), 0.05);
}

.thinking-toggle.expanded {
  border-bottom: 1px solid var(--color-border);
  border-radius: var(--radius-md, 0.5rem) var(--radius-md, 0.5rem) 0 0;
}

.toggle-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-align: left;
}

.toggle-icon {
  color: var(--color-text-muted);
  transition: transform 0.2s ease;
}

.toggle-icon .rotated {
  transform: rotate(180deg);
}

.toggle-text {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text);
}

.step-summary {
  margin-left: auto;
  font-size: 0.75rem;
  color: var(--color-text-muted);
  font-weight: 400;
}

.duration {
  color: var(--color-primary);
}

.thinking-steps {
  padding: 0;
}

.thinking-step {
  padding: 1rem;
  border-bottom: 1px solid var(--color-border);
  transition: background-color 0.2s ease;
}

.thinking-step:last-child {
  border-bottom: none;
}

.thinking-step:hover {
  background: rgba(var(--color-primary-rgb, 0, 123, 255), 0.02);
}

.step-header {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.step-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 2px;
}

/* Step type specific colors */
.step-user_input .step-icon {
  background: rgba(59, 130, 246, 0.1);
  color: rgb(59, 130, 246);
}

.step-tool_planning .step-icon {
  background: rgba(168, 85, 247, 0.1);
  color: rgb(168, 85, 247);
}

.step-tool_execution .step-icon {
  background: rgba(249, 115, 22, 0.1);
  color: rgb(249, 115, 22);
}

.step-tool_result .step-icon {
  background: rgba(34, 197, 94, 0.1);
  color: rgb(34, 197, 94);
}

.step-reasoning .step-icon {
  background: rgba(236, 72, 153, 0.1);
  color: rgb(236, 72, 153);
}

.step-final_response .step-icon {
  background: rgba(16, 185, 129, 0.1);
  color: rgb(16, 185, 129);
}

.step-info {
  flex: 1;
  min-width: 0;
}

.step-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 0.25rem 0;
}

.step-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.step-time {
  font-family: monospace;
}

.step-duration {
  color: var(--color-primary);
  font-weight: 500;
}

.step-type {
  background: var(--color-surface);
  padding: 2px 6px;
  border-radius: var(--radius-sm, 0.375rem);
  border: 1px solid var(--color-border);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.step-content {
  margin-left: 43px;
}

.step-text {
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--color-text);
  margin-bottom: 0.5rem;
}

.step-metadata {
  margin-top: 0.5rem;
}

.tool-args {
  background: var(--color-surface);
  padding: 0.5rem;
  border-radius: var(--radius-sm, 0.375rem);
  border: 1px solid var(--color-border);
  font-size: 0.75rem;
}

.tool-args code {
  background: transparent;
  color: var(--color-text);
  font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas,
    monospace;
  white-space: pre-wrap;
  word-break: break-all;
}

.tool-result-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
}

.result-status {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  font-weight: bold;
  font-size: 0.7rem;
}

.result-status.success {
  background: rgba(34, 197, 94, 0.1);
  color: rgb(34, 197, 94);
}

.result-status.error {
  background: rgba(239, 68, 68, 0.1);
  color: rgb(239, 68, 68);
}

.result-size {
  color: var(--color-text-muted);
}

.tool-planning-meta {
  font-size: 0.75rem;
  color: var(--color-primary);
  font-weight: 500;
}

/* Transition animations */
.thinking-expand-enter-active,
.thinking-expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.thinking-expand-enter-from,
.thinking-expand-leave-to {
  max-height: 0;
  opacity: 0;
}

.thinking-expand-enter-to,
.thinking-expand-leave-from {
  max-height: 1000px;
  opacity: 1;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .thinking-step {
    padding: 0.75rem;
  }

  .step-header {
    gap: 0.5rem;
  }

  .step-content {
    margin-left: 33px;
  }

  .step-meta {
    flex-wrap: wrap;
    gap: 0.25rem;
  }
}
</style>
