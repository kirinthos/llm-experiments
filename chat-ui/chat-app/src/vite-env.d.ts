/// <reference types="vite/client" />

declare global {
  interface Window {
    copyToClipboard?: (button: HTMLButtonElement) => void;
  }
}
