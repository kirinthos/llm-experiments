<template>
  <div class="tools-dropdown" :class="{ open: isOpen }">
    <button
      class="tools-button"
      @click="toggleDropdown"
      :class="{ active: toolsEnabled }"
    >
      🔧 Tools {{ toolsEnabled ? "ON" : "OFF" }}
      <span class="dropdown-arrow">{{ isOpen ? "▲" : "▼" }}</span>
    </button>

    <div class="tools-menu">
      <div class="tools-header">
        <label class="tools-toggle">
          <input
            type="checkbox"
            :checked="toolsEnabled"
            @change="$emit('toggle')"
          />
          <span>Enable Tools</span>
        </label>
      </div>

      <div v-if="availableTools.length > 0" class="tools-list">
        <h4 class="tools-category-title">Available Tools:</h4>
        <div
          v-for="category in toolCategories"
          :key="category.name"
          class="tools-category"
        >
          <h5 class="category-name">{{ category.name }}</h5>
          <div class="category-tools">
            <div
              v-for="tool in category.tools"
              :key="tool.name"
              class="tool-item"
            >
              <span class="tool-name">{{ tool.name }}</span>
              <span class="tool-description">{{ tool.description }}</span>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="no-tools">
        <p>No tools available in test mode</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";
import type { Tool } from "../providers/apiProvider";

interface Props {
  availableTools: Tool[];
  toolsEnabled: boolean;
}

interface Emits {
  (e: "toggle"): void;
}

const props = defineProps<Props>();
defineEmits<Emits>();

const isOpen = ref(false);

const toolCategories = computed(() => {
  const categories = new Map<string, Tool[]>();

  props.availableTools.forEach((tool) => {
    const category = tool.category || "Other";
    if (!categories.has(category)) {
      categories.set(category, []);
    }
    categories.get(category)!.push(tool);
  });

  return Array.from(categories.entries()).map(([name, tools]) => ({
    name,
    tools,
  }));
});

function toggleDropdown() {
  isOpen.value = !isOpen.value;
}

function handleClickOutside(event: Event) {
  const target = event.target as Element;
  if (!target.closest(".tools-dropdown")) {
    isOpen.value = false;
  }
}

onMounted(() => {
  document.addEventListener("click", handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener("click", handleClickOutside);
});
</script>

<style scoped>
.tools-dropdown {
  position: relative;
  display: inline-block;
}

.tools-button {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm, 0.5rem);
  padding: var(--spacing-sm, 0.5rem) var(--spacing-md, 1rem);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md, 0.5rem);
  background-color: var(--color-surface);
  color: var(--color-text);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tools-button:hover {
  border-color: var(--color-primary);
  background-color: var(--color-surface-hover);
}

.tools-button.active {
  background-color: var(--color-primary);
  color: var(--color-chat-bubble-user-text);
  border-color: var(--color-primary);
}

.dropdown-arrow {
  font-size: 0.75rem;
  transition: transform 0.2s ease;
}

.tools-dropdown.open .dropdown-arrow {
  transform: rotate(180deg);
}

.tools-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: var(--spacing-xs, 0.25rem);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md, 0.5rem);
  box-shadow: var(--shadow-lg);
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px);
  transition: all 0.2s ease;
  min-width: 300px;
  max-width: 400px;
  max-height: 400px;
  overflow-y: auto;
  z-index: 100;
}

.tools-dropdown.open .tools-menu {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.tools-header {
  padding: var(--spacing-md, 1rem);
  border-bottom: 1px solid var(--color-border);
}

.tools-toggle {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm, 0.5rem);
  cursor: pointer;
  font-weight: 600;
}

.tools-toggle input {
  margin: 0;
}

.tools-list {
  padding: var(--spacing-md, 1rem);
}

.tools-category-title {
  margin: 0 0 var(--spacing-md, 1rem) 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.tools-category {
  margin-bottom: var(--spacing-lg, 1.5rem);
}

.tools-category:last-child {
  margin-bottom: 0;
}

.category-name {
  margin: 0 0 var(--spacing-sm, 0.5rem) 0;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.category-tools {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm, 0.5rem);
}

.tool-item {
  padding: var(--spacing-sm, 0.5rem);
  background-color: var(--color-surface-hover);
  border-radius: var(--radius-sm, 0.375rem);
  border-left: 3px solid var(--color-primary);
}

.tool-name {
  display: block;
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--color-text);
  margin-bottom: var(--spacing-xs, 0.25rem);
}

.tool-description {
  display: block;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  line-height: 1.4;
}

.no-tools {
  padding: var(--spacing-md, 1rem);
  text-align: center;
  color: var(--color-text-muted);
  font-style: italic;
}

.no-tools p {
  margin: 0;
}
</style>
