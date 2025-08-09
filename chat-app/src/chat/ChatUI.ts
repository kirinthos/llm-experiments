/**
 * Chat User Interface component
 */

import type { Model, Message } from '../types';
import type { Tool } from '../providers/apiProvider';

export class ChatUI {
  private models: Model[];
  private currentModel: Model;
  private onSendMessage: (content: string) => Promise<void>;
  private onModelChange: (model: Model) => void;
  private onClearChat: () => void;
  private availableTools: Tool[];
  private onToolsToggle: (enabled: boolean) => void;
  private toolsEnabled: boolean = true;
  private container!: HTMLElement;
  private messagesContainer!: HTMLElement;
  private messageInput!: HTMLInputElement;
  private sendButton!: HTMLButtonElement;
  private modelSelector!: HTMLSelectElement;

  constructor(
    models: Model[],
    currentModel: Model,
    onSendMessage: (content: string) => Promise<void>,
    onModelChange: (model: Model) => void,
    onClearChat: () => void,
    availableTools: Tool[] = [],
    onToolsToggle: (enabled: boolean) => void = () => {}
  ) {
    this.models = models;
    this.currentModel = currentModel;
    this.onSendMessage = onSendMessage;
    this.onModelChange = onModelChange;
    this.onClearChat = onClearChat;
    this.availableTools = availableTools;
    this.onToolsToggle = onToolsToggle;
  }

  render(container: HTMLElement): void {
    this.container = container;
    
    container.innerHTML = `
      <div class="chat-app">
        <header class="chat-header">
          <div class="chat-title">
            <h1>🤖 Universal AI Chat</h1>
            <span class="subtitle">Multi-Provider Agent Interface</span>
          </div>
          <div class="chat-controls">
            ${this.availableTools.length > 0 ? `
              <div class="tools-dropdown">
                <button class="tools-button" id="toolsButton" title="Available Tools">
                  🔧 Tools (${this.availableTools.length})
                </button>
                <div class="tools-menu" id="toolsMenu" style="display: none;">
                  <div class="tools-header">
                    <label class="tools-toggle">
                      <input type="checkbox" id="toolsToggle" ${this.toolsEnabled ? 'checked' : ''}>
                      Enable Tools
                    </label>
                  </div>
                  <div class="tools-list">
                    ${this.renderToolsByCategory()}
                  </div>
                </div>
              </div>
            ` : ''}
            <select class="model-selector" id="modelSelector">
              ${this.models.map(model => `
                <option value="${model.id}" ${model.id === this.currentModel.id ? 'selected' : ''}>
                  ${model.name}
                </option>
              `).join('')}
            </select>
            <button class="clear-button" id="clearButton" title="Clear conversation">
              🗑️
            </button>
          </div>
        </header>

        <div class="messages-container" id="messagesContainer">
          <div class="welcome-message">
            <div class="welcome-content">
              <h2>Welcome to Universal AI Chat! 👋</h2>
              <p>Start a conversation with your AI assistant. You can:</p>
              <ul>
                <li>Ask questions about any topic</li>
                <li>Get help with coding, writing, or analysis</li>
                <li>Switch between different AI models</li>
                <li>Your conversation is saved automatically</li>
              </ul>
              <p class="current-model">Currently using: <strong>${this.currentModel.name}</strong></p>
            </div>
          </div>
        </div>

        <div class="input-container">
          <div class="input-wrapper">
            <input 
              type="text" 
              class="message-input" 
              id="messageInput" 
              placeholder="Type your message..."
              maxlength="1000"
            >
            <button class="send-button" id="sendButton">
              <span class="send-icon">➤</span>
            </button>
          </div>
          <div class="input-footer">
            <span class="model-indicator">
              ${this.getModelIcon(this.currentModel.provider)} ${this.currentModel.name}
            </span>
          </div>
        </div>

        <div class="loading-indicator" id="loadingIndicator" style="display: none;">
          <div class="typing-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    `;

    this.bindElements();
    this.attachEventListeners();
  }

  private bindElements(): void {
    this.messagesContainer = this.container.querySelector('#messagesContainer')!;
    this.messageInput = this.container.querySelector('#messageInput')!;
    this.sendButton = this.container.querySelector('#sendButton')!;
    this.modelSelector = this.container.querySelector('#modelSelector')!;
  }

  private attachEventListeners(): void {
    // Send message on button click
    this.sendButton.addEventListener('click', () => {
      this.handleSendMessage();
    });

    // Send message on Enter key
    this.messageInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.handleSendMessage();
      }
    });

    // Model selection
    this.modelSelector.addEventListener('change', () => {
      const selectedModel = this.models.find(m => m.id === this.modelSelector.value);
      if (selectedModel) {
        this.currentModel = selectedModel;
        this.onModelChange(selectedModel);
        this.updateModelIndicator();
      }
    });

    // Clear chat
    const clearButton = this.container.querySelector('#clearButton')!;
    clearButton.addEventListener('click', () => {
      if (confirm('Are you sure you want to clear the conversation?')) {
        this.onClearChat();
      }
    });

    // Tools dropdown
    if (this.availableTools.length > 0) {
      const toolsButton = this.container.querySelector('#toolsButton');
      const toolsMenu = this.container.querySelector('#toolsMenu') as HTMLElement;
      const toolsToggle = this.container.querySelector('#toolsToggle') as HTMLInputElement;

      if (toolsButton && toolsMenu && toolsToggle) {
        // Toggle tools menu
        toolsButton.addEventListener('click', (e) => {
          e.stopPropagation();
          const isVisible = toolsMenu.style.display !== 'none';
          toolsMenu.style.display = isVisible ? 'none' : 'block';
        });

        // Close menu when clicking outside
        document.addEventListener('click', () => {
          toolsMenu.style.display = 'none';
        });

        // Prevent menu close when clicking inside
        toolsMenu.addEventListener('click', (e) => {
          e.stopPropagation();
        });

        // Tools toggle
        toolsToggle.addEventListener('change', () => {
          this.toolsEnabled = toolsToggle.checked;
          this.onToolsToggle(this.toolsEnabled);
        });
      }
    }
  }

  private async handleSendMessage(): Promise<void> {
    const content = this.messageInput.value.trim();
    if (!content) return;

    this.messageInput.value = '';
    this.messageInput.disabled = true;
    this.sendButton.disabled = true;

    try {
      await this.onSendMessage(content);
    } finally {
      this.messageInput.disabled = false;
      this.sendButton.disabled = false;
      this.messageInput.focus();
    }
  }

  addMessage(message: Message): void {
    // Remove welcome message if it exists
    const welcomeMessage = this.messagesContainer.querySelector('.welcome-message');
    if (welcomeMessage) {
      welcomeMessage.remove();
    }

    const messageElement = document.createElement('div');
    messageElement.className = `message ${message.role}-message`;
    
    const time = message.timestamp.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });

    messageElement.innerHTML = `
      <div class="message-content">
        <div class="message-header">
          <span class="message-role">
            ${message.role === 'user' ? '👤 You' : `🤖 ${this.currentModel.name}`}
          </span>
          <span class="message-time">${time}</span>
        </div>
        <div class="message-text">${this.formatMessageContent(message.content)}</div>
      </div>
    `;

    this.messagesContainer.appendChild(messageElement);
    this.scrollToBottom();
  }

  private formatMessageContent(content: string): string {
    // Basic formatting for now - can be enhanced later
    return content
      .replace(/\n/g, '<br>')
      .replace(/`([^`]+)`/g, '<code>$1</code>');
  }

  setLoading(loading: boolean): void {
    const loadingIndicator = this.container.querySelector('#loadingIndicator') as HTMLElement;
    loadingIndicator.style.display = loading ? 'block' : 'none';
    
    if (loading) {
      this.scrollToBottom();
    }
  }

  clearMessages(): void {
    this.messagesContainer.innerHTML = `
      <div class="welcome-message">
        <div class="welcome-content">
          <h2>Welcome to Universal AI Chat! 👋</h2>
          <p>Start a conversation with your AI assistant. You can:</p>
          <ul>
            <li>Ask questions about any topic</li>
            <li>Get help with coding, writing, or analysis</li>
            <li>Switch between different AI models</li>
            <li>Your conversation is saved automatically</li>
          </ul>
          <p class="current-model">Currently using: <strong>${this.currentModel.name}</strong></p>
        </div>
      </div>
    `;
  }

  showModelChanged(model: Model): void {
    const notification = document.createElement('div');
    notification.className = 'model-change-notification';
    notification.innerHTML = `
      <div class="notification-content">
        ${this.getModelIcon(model.provider)} Switched to <strong>${model.name}</strong>
      </div>
    `;

    this.messagesContainer.appendChild(notification);
    this.scrollToBottom();

    // Remove notification after 3 seconds
    setTimeout(() => {
      notification.remove();
    }, 3000);
  }

  private updateModelIndicator(): void {
    const indicator = this.container.querySelector('.model-indicator')!;
    indicator.innerHTML = `${this.getModelIcon(this.currentModel.provider)} ${this.currentModel.name}`;
  }

  private getModelIcon(provider: string): string {
    switch (provider) {
      case 'openai': return '🔵';
      case 'gemini': return '🟢';
      case 'claude': return '🟣';
      default: return '🤖';
    }
  }

  private scrollToBottom(): void {
    setTimeout(() => {
      this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }, 100);
  }

  private renderToolsByCategory(): string {
    // Group tools by category
    const categories: Record<string, Tool[]> = {};
    this.availableTools.forEach(tool => {
      if (!categories[tool.category]) {
        categories[tool.category] = [];
      }
      categories[tool.category].push(tool);
    });

    return Object.entries(categories).map(([category, tools]) => `
      <div class="tool-category">
        <div class="category-header">${category}</div>
        <div class="category-tools">
          ${tools.map(tool => `
            <div class="tool-item" title="${tool.description}">
              <span class="tool-icon">${tool.icon}</span>
              <span class="tool-name">${tool.name}</span>
            </div>
          `).join('')}
        </div>
      </div>
    `).join('');
  }

  showConnectionStatus(isRealAPI: boolean): void {
    const statusElement = document.createElement('div');
    statusElement.className = 'connection-status';
    statusElement.innerHTML = `
      <div class="status-content ${isRealAPI ? 'connected' : 'test-mode'}">
        ${isRealAPI ? '🟢 Connected to API' : '🟡 Test Mode'}
      </div>
    `;

    this.messagesContainer.appendChild(statusElement);

    // Remove status after 3 seconds
    setTimeout(() => {
      statusElement.remove();
    }, 3000);
  }
}