<template>
  <div class="server-status" :class="{ open: isOpen }">
    <button
      class="status-button"
      :class="[`status-${worstStatus}`]"
      @click="toggleDropdown"
      @blur="handleBlur"
    >
      <span class="status-icon">{{ statusIcon }}</span>
      <span class="status-text">{{ statusText }}</span>
      <svg
        class="dropdown-arrow"
        :class="{ rotated: isOpen }"
        width="12"
        height="12"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
      >
        <path d="m6 9 6 6 6-6" />
      </svg>
    </button>

    <div v-if="isOpen" class="status-dropdown">
      <div class="status-header">
        <h3>Server Status</h3>
      </div>

      <div class="status-list">
        <div class="status-item" :class="`status-${aiServerStatus}`">
          <div class="status-indicator">
            <span class="indicator-dot"></span>
          </div>
          <div class="status-details">
            <div class="status-name">AI Server</div>
            <div class="status-description">{{ aiServerDescription }}</div>
            <div class="status-url">{{ aiServerUrl }}</div>
          </div>
        </div>

        <div class="status-item" :class="`status-${mcpServerStatus}`">
          <div class="status-indicator">
            <span class="indicator-dot"></span>
          </div>
          <div class="status-details">
            <div class="status-name">MCP Server</div>
            <div class="status-description">{{ mcpServerDescription }}</div>
            <div class="status-url">{{ mcpServerUrl }}</div>
          </div>
        </div>
      </div>

      <div class="status-footer">
        <button
          @click="refreshStatus"
          class="refresh-button"
          :disabled="isRefreshing"
        >
          <svg
            class="refresh-icon"
            :class="{ spinning: isRefreshing }"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" />
            <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" />
          </svg>
          Refresh
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { getApiUrl, getConfig } from "../config";

interface ServerStatusState {
  status: "healthy" | "degraded" | "error" | "unknown";
  description: string;
  lastChecked?: string;
  details?: any;
}

const isOpen = ref(false);
const isRefreshing = ref(false);
const aiServerStatus = ref<ServerStatusState["status"]>("unknown");
const mcpServerStatus = ref<ServerStatusState["status"]>("unknown");
const aiServerDescription = ref("Checking...");
const mcpServerDescription = ref("Checking...");
const aiServerUrl = getApiUrl();
const mcpServerUrl = `${getApiUrl()} (MCP)`;

const worstStatus = computed(() => {
  const statuses = [aiServerStatus.value, mcpServerStatus.value];
  if (statuses.includes("error")) return "error";
  if (statuses.includes("degraded")) return "degraded";
  if (statuses.includes("unknown")) return "unknown";
  return "healthy";
});

const statusIcon = computed(() => {
  switch (worstStatus.value) {
    case "healthy":
      return "🟢";
    case "degraded":
      return "🟡";
    case "error":
      return "🔴";
    default:
      return "⚪";
  }
});

const statusText = computed(() => {
  switch (worstStatus.value) {
    case "healthy":
      return "All Systems Operational";
    case "degraded":
      return "Degraded Performance";
    case "error":
      return "Service Issues";
    default:
      return "Checking Status...";
  }
});

function toggleDropdown() {
  isOpen.value = !isOpen.value;
  if (isOpen.value) {
    refreshStatus();
  }
}

function handleBlur(event: FocusEvent) {
  // Close dropdown if clicking outside
  setTimeout(() => {
    const dropdown = document.querySelector(".status-dropdown");
    if (dropdown && !dropdown.contains(event.relatedTarget as Node)) {
      isOpen.value = false;
    }
  }, 100);
}

async function checkServerHealth(
  url: string,
  endpoint: string
): Promise<ServerStatusState> {
  try {
    const response = await fetch(`${url}${endpoint}`, {
      method: "GET",
      timeout: 5000,
    } as RequestInit);

    if (!response.ok) {
      return {
        status: "error",
        description: `HTTP ${response.status}: ${response.statusText}`,
        lastChecked: new Date().toISOString(),
      };
    }

    const data = await response.json();
    return {
      status: "healthy",
      description:
        data.status === "healthy"
          ? "Connected and operational"
          : "Connected but degraded",
      lastChecked: new Date().toISOString(),
      details: data,
    };
  } catch (error) {
    return {
      status: "error",
      description: error instanceof Error ? error.message : "Connection failed",
      lastChecked: new Date().toISOString(),
    };
  }
}

async function refreshStatus() {
  if (isRefreshing.value) return;

  isRefreshing.value = true;

  try {
    // Check both servers in parallel
    const [aiHealth, mcpHealth] = await Promise.all([
      checkServerHealth(aiServerUrl, "/health"),
      checkServerHealth(mcpServerUrl, "/health"),
    ]);

    aiServerStatus.value = aiHealth.status;
    aiServerDescription.value = aiHealth.description;

    mcpServerStatus.value = mcpHealth.status;
    mcpServerDescription.value = mcpHealth.description;
  } catch (error) {
    console.error("Failed to refresh server status:", error);
  } finally {
    isRefreshing.value = false;
  }
}

onMounted(async () => {
  // Load config and start status monitoring
  const config = getConfig();
  refreshStatus();

  // Use configured refresh interval
  const interval = config.server.healthCheckInterval * 1000;
  setInterval(refreshStatus, interval);
});
</script>

<style scoped>
.server-status {
  position: relative;
  display: inline-block;
}

.status-button {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm, 0.5rem);
  padding: var(--spacing-sm, 0.5rem) var(--spacing-md, 1rem);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md, 0.5rem);
  background-color: var(--color-surface);
  color: var(--color-text);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.status-button:hover {
  background-color: var(--color-surface-hover);
}

.status-button.status-healthy {
  border-color: var(--color-success);
}

.status-button.status-degraded {
  border-color: var(--color-warning);
}

.status-button.status-error {
  border-color: var(--color-danger);
}

.status-button.status-unknown {
  border-color: var(--color-border);
}

.status-icon {
  font-size: 1rem;
}

.status-text {
  white-space: nowrap;
}

.dropdown-arrow {
  transition: transform 0.2s ease;
}

.dropdown-arrow.rotated {
  transform: rotate(180deg);
}

.status-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: var(--spacing-xs, 0.25rem);
  min-width: 320px;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg, 0.75rem);
  box-shadow: var(--shadow-lg);
  z-index: 1000;
  overflow: hidden;
}

.status-header {
  padding: var(--spacing-md, 1rem);
  background-color: var(--color-background);
  border-bottom: 1px solid var(--color-border);
}

.status-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
}

.status-list {
  padding: var(--spacing-sm, 0.5rem);
}

.status-item {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md, 1rem);
  padding: var(--spacing-md, 1rem);
  border-radius: var(--radius-md, 0.5rem);
  transition: background-color 0.2s ease;
}

.status-item:hover {
  background-color: var(--color-background);
}

.status-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.indicator-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--color-text-muted);
}

.status-item.status-healthy .indicator-dot {
  background-color: var(--color-success);
}

.status-item.status-degraded .indicator-dot {
  background-color: var(--color-warning);
}

.status-item.status-error .indicator-dot {
  background-color: var(--color-danger);
}

.status-details {
  flex: 1;
  min-width: 0;
}

.status-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: var(--spacing-xs, 0.25rem);
}

.status-description {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xs, 0.25rem);
}

.status-url {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  font-family: monospace;
}

.status-footer {
  padding: var(--spacing-md, 1rem);
  background-color: var(--color-background);
  border-top: 1px solid var(--color-border);
}

.refresh-button {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm, 0.5rem);
  padding: var(--spacing-sm, 0.5rem) var(--spacing-md, 1rem);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md, 0.5rem);
  background-color: var(--color-surface);
  color: var(--color-text);
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;
  justify-content: center;
}

.refresh-button:hover:not(:disabled) {
  background-color: var(--color-surface-hover);
}

.refresh-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.refresh-icon {
  transition: transform 0.2s ease;
}

.refresh-icon.spinning {
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
