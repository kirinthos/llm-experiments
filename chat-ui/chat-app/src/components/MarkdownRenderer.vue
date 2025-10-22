<template>
  <div class="markdown-content" v-html="renderedContent"></div>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";
import { marked } from "marked";
import hljs from "highlight.js";
import "highlight.js/styles/github-dark.css";

interface Props {
  content: string;
  extractCitations?: boolean;
}

interface Citation {
  id: number;
  url: string;
  title: string;
  domain: string;
}

const props = withDefaults(defineProps<Props>(), {
  extractCitations: true,
});

const emit = defineEmits<{
  citations: [citations: Citation[]];
}>();

// Configure marked with custom renderer
const renderer = new marked.Renderer();

// Custom heading renderer
renderer.heading = (text, level) => {
  const anchor = text.toLowerCase().replace(/[^\w]+/g, "-");
  return `<h${level} id="${anchor}" class="markdown-heading markdown-h${level}">${text}</h${level}>`;
};

// Custom paragraph renderer with citation detection
renderer.paragraph = (text) => {
  // Convert citation patterns [1], [2], etc. to citation pills
  const citationPattern = /\[(\d+)\]/g;
  const textWithCitations = text.replace(citationPattern, (match, num) => {
    return `<span class="citation-pill" data-citation="${num}">${match}</span>`;
  });

  return `<p class="markdown-paragraph">${textWithCitations}</p>`;
};

// Custom link renderer for external links
renderer.link = (href, title, text) => {
  const titleAttr = title ? ` title="${title}"` : "";
  return `<a href="${href}" target="_blank" rel="noopener noreferrer" class="markdown-link"${titleAttr}>${text}</a>`;
};

// Custom code block renderer with syntax highlighting
renderer.code = (code, language) => {
  const validLanguage =
    language && hljs.getLanguage(language) ? language : "plaintext";
  const highlighted = hljs.highlight(code, { language: validLanguage }).value;

  return `
    <div class="code-block-wrapper">
      <div class="code-block-header">
        <span class="code-language">${validLanguage}</span>
        <button class="copy-button" onclick="copyToClipboard(this)" data-code="${encodeURIComponent(
          code
        )}">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="m5 15-2-2 2-2"></path>
          </svg>
          Copy
        </button>
      </div>
      <pre class="code-block"><code class="hljs language-${validLanguage}">${highlighted}</code></pre>
    </div>
  `;
};

// Custom inline code renderer
renderer.codespan = (code) => {
  return `<code class="inline-code">${code}</code>`;
};

// Custom table renderer
renderer.table = (header, body) => {
  return `
    <div class="table-wrapper">
      <table class="markdown-table">
        <thead>${header}</thead>
        <tbody>${body}</tbody>
      </table>
    </div>
  `;
};

// Custom list renderer
renderer.list = (body, ordered, start) => {
  const type = ordered ? "ol" : "ul";
  const startAttr = ordered && start !== 1 ? ` start="${start}"` : "";
  return `<${type} class="markdown-list"${startAttr}>${body}</${type}>`;
};

// Custom blockquote renderer
renderer.blockquote = (quote) => {
  return `<blockquote class="markdown-blockquote">${quote}</blockquote>`;
};

// Configure marked options
marked.setOptions({
  renderer,
  gfm: true,
  breaks: true,
  sanitize: false,
});

// Extract citations from content
const extractCitations = (content: string): Citation[] => {
  const citations: Citation[] = [];
  const citationPattern = /\[(\d+)\][\s]*(?:\(([^)]+)\))?/g;
  const urlPattern = /https?:\/\/[^\s]+/g;

  let match;
  const urls = content.match(urlPattern) || [];

  while ((match = citationPattern.exec(content)) !== null) {
    const id = parseInt(match[1]);
    const url = match[2] || urls[id - 1] || "#";

    // Extract domain from URL
    let domain = "";
    let title = `Source ${id}`;

    try {
      const urlObj = new URL(url);
      domain = urlObj.hostname.replace("www.", "");
      title = domain;
    } catch {
      domain = "Unknown";
    }

    citations.push({
      id,
      url,
      title,
      domain,
    });
  }

  return citations;
};

const renderedContent = computed(() => {
  try {
    const rendered = marked(props.content);

    // Extract and emit citations if enabled
    if (props.extractCitations) {
      const citations = extractCitations(props.content);
      if (citations.length > 0) {
        emit("citations", citations);
      }
    }

    return rendered;
  } catch (error) {
    console.error("Markdown rendering error:", error);
    return `<p class="markdown-error">Error rendering markdown: ${error}</p>`;
  }
});

// Add global copy function for code blocks
onMounted(() => {
  if (!window.copyToClipboard) {
    window.copyToClipboard = (button: HTMLButtonElement) => {
      const code = decodeURIComponent(button.dataset.code || "");
      navigator.clipboard.writeText(code).then(() => {
        const originalText = button.innerHTML;
        button.innerHTML = `
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20,6 9,17 4,12"></polyline>
          </svg>
          Copied!
        `;
        setTimeout(() => {
          button.innerHTML = originalText;
        }, 2000);
      });
    };
  }
});
</script>

<style scoped>
.markdown-content {
  font-size: 0.95rem;
  line-height: 1.6;
  color: inherit;
}

/* Headings */
:deep(.markdown-heading) {
  margin: 1.5rem 0 1rem 0;
  font-weight: 600;
  line-height: 1.3;
}

:deep(.markdown-h1) {
  font-size: 1.75rem;
  border-bottom: 2px solid var(--color-border);
  padding-bottom: 0.5rem;
}

:deep(.markdown-h2) {
  font-size: 1.5rem;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 0.25rem;
}

:deep(.markdown-h3) {
  font-size: 1.25rem;
}

:deep(.markdown-h4) {
  font-size: 1.1rem;
}

:deep(.markdown-h5) {
  font-size: 1rem;
}

:deep(.markdown-h6) {
  font-size: 0.9rem;
  color: var(--color-text-muted);
}

/* Paragraphs */
:deep(.markdown-paragraph) {
  margin: 1rem 0;
}

/* Links */
:deep(.markdown-link) {
  color: var(--color-primary);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: all 0.2s ease;
}

:deep(.markdown-link:hover) {
  border-bottom-color: var(--color-primary);
}

/* Citation Pills */
:deep(.citation-pill) {
  display: inline-block;
  background: var(--color-primary);
  color: white;
  font-size: 0.75rem;
  font-weight: 500;
  padding: 2px 6px;
  border-radius: 10px;
  margin: 0 2px;
  cursor: pointer;
  transition: all 0.2s ease;
  vertical-align: super;
  line-height: 1;
}

:deep(.citation-pill:hover) {
  background: var(--color-primary-dark, #0056b3);
  transform: scale(1.05);
}

/* Code Blocks */
:deep(.code-block-wrapper) {
  margin: 1.5rem 0;
  border-radius: var(--radius-lg, 0.75rem);
  overflow: hidden;
  border: 1px solid var(--color-border);
  background: #1a1a1a;
}

:deep(.code-block-header) {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: #2d2d2d;
  border-bottom: 1px solid #3a3a3a;
}

:deep(.code-language) {
  font-size: 0.75rem;
  font-weight: 500;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

:deep(.copy-button) {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  background: transparent;
  border: 1px solid #555;
  border-radius: var(--radius-sm, 0.375rem);
  color: #ccc;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

:deep(.copy-button:hover) {
  background: #3a3a3a;
  border-color: #777;
}

:deep(.code-block) {
  margin: 0;
  padding: 1rem;
  background: #1a1a1a;
  overflow-x: auto;
  font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas,
    monospace;
  font-size: 0.875rem;
  line-height: 1.5;
}

:deep(.code-block code) {
  background: none;
  padding: 0;
  border-radius: 0;
  font-family: inherit;
  font-size: inherit;
}

/* Inline Code */
:deep(.inline-code) {
  background: var(--color-surface);
  color: var(--color-danger);
  padding: 2px 6px;
  border-radius: var(--radius-sm, 0.375rem);
  font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas,
    monospace;
  font-size: 0.875em;
  border: 1px solid var(--color-border);
}

/* Tables */
:deep(.table-wrapper) {
  margin: 1.5rem 0;
  overflow-x: auto;
  border-radius: var(--radius-lg, 0.75rem);
  border: 1px solid var(--color-border);
}

:deep(.markdown-table) {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

:deep(.markdown-table th) {
  background: var(--color-surface);
  font-weight: 600;
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 2px solid var(--color-border);
}

:deep(.markdown-table td) {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
}

:deep(.markdown-table tbody tr:hover) {
  background: var(--color-surface);
}

/* Lists */
:deep(.markdown-list) {
  margin: 1rem 0;
  padding-left: 1.5rem;
}

:deep(.markdown-list li) {
  margin: 0.25rem 0;
}

:deep(.markdown-list ul),
:deep(.markdown-list ol) {
  margin: 0.5rem 0;
}

/* Blockquotes */
:deep(.markdown-blockquote) {
  margin: 1.5rem 0;
  padding: 1rem 1.5rem;
  border-left: 4px solid var(--color-primary);
  background: var(--color-surface);
  border-radius: 0 var(--radius-md, 0.5rem) var(--radius-md, 0.5rem) 0;
  font-style: italic;
}

:deep(.markdown-blockquote p) {
  margin: 0;
}

/* Error styling */
:deep(.markdown-error) {
  color: var(--color-danger);
  background: var(--color-surface);
  padding: 1rem;
  border-radius: var(--radius-md, 0.5rem);
  border: 1px solid var(--color-danger);
  font-family: monospace;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  :deep(.code-block-header) {
    padding: 0.5rem;
  }

  :deep(.code-block) {
    padding: 0.75rem;
  }

  :deep(.markdown-table th),
  :deep(.markdown-table td) {
    padding: 0.5rem;
  }
}
</style>
