<template>
  <div class="model-selector">
    <label class="model-label">Model:</label>
    <select
      class="model-select"
      :value="currentModel?.id || ''"
      @change="handleModelChange"
    >
      <option
        v-for="model in availableModels"
        :key="model.id"
        :value="model.id"
      >
        {{ model.name }} ({{ model.provider }})
      </option>
    </select>
  </div>
</template>

<script setup lang="ts">
import type { Model } from "../types";

interface Props {
  availableModels: Model[];
  currentModel?: Model;
}

interface Emits {
  (e: "change", model: Model): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

function handleModelChange(event: Event) {
  const target = event.target as HTMLSelectElement;
  const selectedModel = props.availableModels.find(
    (model) => model.id === target.value
  );
  if (selectedModel) {
    emit("change", selectedModel);
  }
}
</script>

<style scoped>
.model-selector {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm, 0.5rem);
  margin-bottom: var(--spacing-md, 1rem);
}

.model-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  white-space: nowrap;
}

.model-select {
  padding: var(--spacing-sm, 0.5rem) var(--spacing-md, 1rem);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md, 0.5rem);
  background-color: var(--color-surface);
  color: var(--color-text);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 200px;
}

.model-select:hover {
  border-color: var(--color-primary);
}

.model-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px var(--color-primary);
}

.model-select option {
  background-color: var(--color-surface);
  color: var(--color-text);
  padding: var(--spacing-sm, 0.5rem);
}
</style>
