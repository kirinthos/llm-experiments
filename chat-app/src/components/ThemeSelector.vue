<template>
  <div class="theme-selector" :class="{ open: isOpen }">
    <button
      class="theme-selector-button"
      @click="toggleDropdown"
      :title="`Current theme: ${currentThemeInfo?.theme.name || 'Unknown'}`"
    >
      <span class="theme-icon">{{ currentThemeInfo?.theme.icon || "🌙" }}</span>
    </button>

    <div class="theme-dropdown">
      <div class="theme-options">
        <button
          v-for="{ id, theme } in availableThemes"
          :key="id"
          class="theme-option"
          :class="{ active: currentTheme === id }"
          @click="selectTheme(id)"
        >
          <span class="theme-option-icon">{{ theme.icon }}</span>
          <span class="theme-option-name">{{ theme.name }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { useTheme } from "../composables/useTheme";
import type { ThemeId } from "../composables/useTheme";

const { currentTheme, availableThemes, currentThemeInfo, setTheme } =
  useTheme();

const isOpen = ref(false);

function toggleDropdown() {
  isOpen.value = !isOpen.value;
}

function selectTheme(themeId: ThemeId) {
  setTheme(themeId);
  isOpen.value = false;
}

function handleClickOutside(event: Event) {
  const target = event.target as Element;
  if (!target.closest(".theme-selector")) {
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
.theme-selector {
  position: relative;
  z-index: 1000;
}

.theme-selector-button {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md, 0.5rem);
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  transition: all 0.2s ease;
  box-shadow: none;
}

.theme-selector-button:hover {
  background: var(--color-surface-hover);
  border-color: var(--color-primary);
}

.theme-selector-button:active {
  background: var(--color-surface-hover);
}

.theme-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: var(--spacing-sm, 0.5rem);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg, 0.75rem);
  box-shadow: var(--shadow-lg);
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px) scale(0.95);
  transition: all 0.2s ease;
  min-width: 160px;
  overflow: hidden;
}

.theme-selector.open .theme-dropdown {
  opacity: 1;
  visibility: visible;
  transform: translateY(0) scale(1);
}

.theme-options {
  padding: var(--spacing-xs, 0.25rem);
}

.theme-option {
  width: 100%;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm, 0.5rem);
  padding: var(--spacing-sm, 0.5rem) var(--spacing-md, 1rem);
  border: none;
  background: transparent;
  color: var(--color-text);
  cursor: pointer;
  border-radius: var(--radius-md, 0.5rem);
  transition: all 0.2s ease;
  font-size: 14px;
}

.theme-option:hover {
  background: var(--color-surface-hover);
}

.theme-option.active {
  background: var(--color-primary);
  color: var(--color-chat-bubble-user-text);
}

.theme-option.active:hover {
  background: var(--color-primary-hover);
}

.theme-option-icon {
  font-size: 16px;
  width: 20px;
  text-align: center;
}

.theme-option-name {
  flex: 1;
  text-align: left;
}
</style>
