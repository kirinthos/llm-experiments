/**
 * Main Chat Application class
 */

import type { AIProvider, Model, Message, Conversation } from '../types';
import { TestAIProvider } from '../providers/testProvider';
import { APIProvider } from '../providers/apiProvider';
import type { Tool } from '../providers/apiProvider';
import { ConversationStorage, generateMessageId } from '../utils/storage';
import { ThemeManager } from '../utils/themeManager';
import { ThemeSelector } from '../components/ThemeSelector';
import { ChatUI } from './ChatUI';

export class ChatApp {
  private provider!: AIProvider;
  private conversation!: Conversation;
  private ui!: ChatUI;
  private themeManager!: ThemeManager;
  private themeSelector!: ThemeSelector;
  private isLoading: boolean = false;
  private useRealAPI: boolean = true; // Toggle between real API and test provider

  constructor() {
    // Provider and conversation will be initialized in mount()
  }

  private async initializeProvider(): Promise<void> {
    try {
      if (this.useRealAPI) {
        const apiProvider = new APIProvider();
        await apiProvider.initialize();
        
        // Check if API is healthy
        const isHealthy = await apiProvider.healthCheck();
        if (isHealthy) {
          this.provider = apiProvider;
          console.log('✅ Connected to real API backend');
        } else {
          throw new Error('API health check failed');
        }
      } else {
        throw new Error('Using test provider');
      }
    } catch (error) {
      console.warn('⚠️ Falling back to test provider:', error);
      this.provider = new TestAIProvider(1500);
      this.useRealAPI = false;
    }
  }

  async mount(selector: string): Promise<void> {
    const container = document.querySelector(selector);
    if (!container) {
      throw new Error(`Container not found: ${selector}`);
    }

    // Initialize theme system
    this.themeManager = new ThemeManager();
    this.themeSelector = new ThemeSelector(this.themeManager);

    // Wait for provider initialization
    await this.initializeProvider();

    // Load or create conversation
    const stored = ConversationStorage.loadConversation();
    if (stored) {
      this.conversation = stored;
    } else {
      const defaultModel = this.provider.getAvailableModels()[0];
      this.conversation = ConversationStorage.createNewConversation(defaultModel);
    }

    // Get available tools if using API provider
    let availableTools: Tool[] = [];
    if (this.provider instanceof APIProvider) {
      availableTools = this.provider.getAvailableTools();
    }

    // Initialize UI
    this.ui = new ChatUI(
      this.provider.getAvailableModels(),
      this.conversation.model,
      this.onSendMessage.bind(this),
      this.onModelChange.bind(this),
      this.onClearChat.bind(this),
      availableTools,
      this.onToolsToggle.bind(this)
    );

    this.ui.render(container as HTMLElement);
    
    // Mount theme selector
    this.themeSelector.mount(document.body);
    
    // Display existing messages
    this.conversation.messages.forEach(message => {
      this.ui.addMessage(message);
    });

    // Show connection status
    this.ui.showConnectionStatus(this.useRealAPI);
  }

  private async onSendMessage(content: string): Promise<void> {
    if (this.isLoading || !content.trim()) return;

    this.isLoading = true;
    this.ui.setLoading(true);

    // Add user message
    const userMessage: Message = {
      id: generateMessageId(),
      content: content.trim(),
      role: 'user',
      timestamp: new Date()
    };

    this.conversation = ConversationStorage.addMessage(this.conversation, userMessage);
    this.ui.addMessage(userMessage);

    try {
      // Get AI response
      const response = await this.provider.sendMessage(
        this.conversation.messages,
        this.conversation.model
      );

      if (response.error) {
        throw new Error(response.error);
      }

      // Add assistant message
      const assistantMessage: Message = {
        id: generateMessageId(),
        content: response.content,
        role: 'assistant',
        timestamp: new Date()
      };

      this.conversation = ConversationStorage.addMessage(this.conversation, assistantMessage);
      this.ui.addMessage(assistantMessage);

    } catch (error) {
      console.error('Failed to get AI response:', error);
      
      // Add error message
      const errorMessage: Message = {
        id: generateMessageId(),
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        role: 'assistant',
        timestamp: new Date()
      };

      this.conversation = ConversationStorage.addMessage(this.conversation, errorMessage);
      this.ui.addMessage(errorMessage);
    } finally {
      this.isLoading = false;
      this.ui.setLoading(false);
    }
  }

  private onModelChange(model: Model): void {
    this.conversation = ConversationStorage.updateModel(this.conversation, model);
    this.ui.showModelChanged(model);
  }

  private onClearChat(): void {
    const defaultModel = this.provider.getAvailableModels()[0];
    this.conversation = ConversationStorage.createNewConversation(defaultModel);
    ConversationStorage.saveConversation(this.conversation);
    this.ui.clearMessages();
  }

  private onToolsToggle(enabled: boolean): void {
    // Handle tools toggle - could be used to enable/disable tools in requests
    console.log(`Tools ${enabled ? 'enabled' : 'disabled'}`);
  }

  cleanup(): void {
    // Save any pending state
    ConversationStorage.saveConversation(this.conversation);
  }
}