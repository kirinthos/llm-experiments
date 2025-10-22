/**
 * Real API provider that connects to the chat-api backend
 */

import type { AIProvider, Model, Message, ChatResponse } from '../types';
import { getApiUrl } from '../config';

export interface Tool {
  id: string;
  name: string;
  description: string;
  category: string;
  icon: string;
  schema: any;
}

export class APIProvider implements AIProvider {
  private baseUrl: string;
  private availableModels: Model[] = [];
  private availableTools: Tool[] = [];

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl || getApiUrl();
  }

  async initialize(): Promise<void> {
    try {
      // Load models and tools from API
      await Promise.all([
        this.loadModels(),
        this.loadTools()
      ]);
    } catch (error) {
      console.error('Failed to initialize API provider:', error);
      throw error;
    }
  }

  private async loadModels(): Promise<void> {
    const response = await fetch(`${this.baseUrl}/models`);
    if (!response.ok) {
      throw new Error(`Failed to load models: ${response.statusText}`);
    }
    
    const data = await response.json();
    this.availableModels = data.models.map((model: any) => ({
      id: model.id,
      name: model.name,
      provider: model.provider as 'openai' | 'gemini' | 'claude',
      description: model.description
    }));
  }

  private async loadTools(): Promise<void> {
    const response = await fetch(`${this.baseUrl}/tools`);
    if (!response.ok) {
      throw new Error(`Failed to load tools: ${response.statusText}`);
    }
    
    const data = await response.json();
    this.availableTools = data.tools;
  }

  async sendMessage(messages: Message[], model: Model): Promise<ChatResponse> {
    try {
      // For single user message, use the simple endpoint
      if (messages.length === 1 && messages[0].role === 'user') {
        return this.sendSimpleMessage(messages[0].content, model);
      }

      // For conversation history, use the full chat endpoint
      const response = await fetch(`${this.baseUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: messages.map(msg => ({
            role: msg.role,
            content: msg.content
          })),
          model: model.id,
          provider: model.provider,
          tools_enabled: true
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      return {
        content: data.response.content || 'No response generated',
        thinkingSteps: data.thinking_steps || []
      };

    } catch (error) {
      console.error('API request failed:', error);
      
      return {
        content: 'Sorry, I encountered an error connecting to the AI service. Please try again.',
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  private async sendSimpleMessage(message: string, model: Model): Promise<ChatResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/chat/simple`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          model: model.id,
          provider: model.provider,
          use_tools: true,
          temperature: 0.7,
          max_tokens: 1000
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      return {
        content: data.response || 'No response generated',
        thinkingSteps: data.thinking_steps || []
      };

    } catch (error) {
      throw error; // Re-throw to be handled by sendMessage
    }
  }

  getAvailableModels(): Model[] {
    return this.availableModels;
  }

  getAvailableTools(): Tool[] {
    return this.availableTools;
  }

  async getToolsByCategory(): Promise<Record<string, Tool[]>> {
    try {
      const response = await fetch(`${this.baseUrl}/tools/categories`);
      if (!response.ok) {
        throw new Error(`Failed to load tool categories: ${response.statusText}`);
      }
      
      const data = await response.json();
      return data.categories;
    } catch (error) {
      console.error('Error loading tool categories:', error);
      return {};
    }
  }

  async executeToolDirectly(toolName: string, args: any): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/tools/${toolName}/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          arguments: args
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Tool execution failed:', error);
      throw error;
    }
  }

  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      return response.ok;
    } catch (error) {
      return false;
    }
  }
}