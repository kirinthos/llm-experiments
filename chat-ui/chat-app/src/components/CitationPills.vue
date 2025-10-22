<template>
  <div v-if="citations.length > 0" class="citations-container">
    <h4 class="citations-title">Sources</h4>
    <div class="citations-grid">
      <div
        v-for="citation in citations"
        :key="citation.id"
        class="citation-card"
        @click="openCitation(citation)"
      >
        <div class="citation-header">
          <span class="citation-number">{{ citation.id }}</span>
          <span class="citation-domain">{{ citation.domain }}</span>
        </div>
        <h5 class="citation-title">{{ citation.title }}</h5>
        <div class="citation-url">{{ formatUrl(citation.url) }}</div>
        <div class="citation-actions">
          <button
            class="citation-action"
            @click.stop="copyUrl(citation.url)"
            title="Copy URL"
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
              <path d="m5 15-2-2 2-2"></path>
            </svg>
          </button>
          <button
            class="citation-action"
            @click.stop="openCitation(citation)"
            title="Open source"
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="m9 18 6-6-6-6"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";

interface Citation {
  id: number;
  url: string;
  title: string;
  domain: string;
}

interface Props {
  citations: Citation[];
}

const props = defineProps<Props>();

const copiedUrl = ref<string>("");

const formatUrl = (url: string): string => {
  try {
    const urlObj = new URL(url);
    const path =
      urlObj.pathname.length > 30
        ? urlObj.pathname.substring(0, 30) + "..."
        : urlObj.pathname;
    return urlObj.hostname + path;
  } catch {
    return url.length > 50 ? url.substring(0, 50) + "..." : url;
  }
};

const openCitation = (citation: Citation) => {
  if (citation.url && citation.url !== "#") {
    window.open(citation.url, "_blank", "noopener,noreferrer");
  }
};

const copyUrl = async (url: string) => {
  try {
    await navigator.clipboard.writeText(url);
    copiedUrl.value = url;
    setTimeout(() => {
      copiedUrl.value = "";
    }, 2000);
  } catch (error) {
    console.error("Failed to copy URL:", error);
  }
};
</script>

<style scoped>
.citations-container {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}

.citations-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-text-muted);
  margin: 0 0 0.75rem 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.citations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 0.75rem;
}

.citation-card {
  position: relative;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md, 0.5rem);
  padding: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
  overflow: hidden;
}

.citation-card:hover {
  border-color: var(--color-primary);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.citation-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.citation-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  background: var(--color-primary);
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 50%;
  flex-shrink: 0;
}

.citation-domain {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.citation-title {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--color-text);
  margin: 0 0 0.5rem 0;
  line-height: 1.3;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.citation-url {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas,
    monospace;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 0.75rem;
}

.citation-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.citation-card:hover .citation-actions {
  opacity: 1;
}

.citation-action {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm, 0.375rem);
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
}

.citation-action:hover {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .citations-grid {
    grid-template-columns: 1fr;
  }

  .citation-actions {
    opacity: 1;
  }

  .citation-card {
    padding: 0.75rem;
  }
}

/* Animation for citation pills in text */
@keyframes citationPulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

/* Global styles for citation pills in markdown content */
:global(.citation-pill:hover) {
  animation: citationPulse 0.3s ease;
}
</style>
