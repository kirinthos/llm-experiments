/**
 * Core types for the chat application
 */

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant' | 'system';
  timestamp: string;
}

export interface Model {
  id: string;
  name: string;
  provider: 'openai' | 'gemini' | 'claude';
  description?: string;
}

export interface Conversation {
  id: string;
  messages: Message[];
  model: Model;
  createdAt: string;
  updatedAt: string;
}

export interface ChatResponse {
  content: string;
  error?: string;
}

/**
 * Abstract interface for communicating with AI models
 */
export interface ChatOptions {
  temperature?: number;
  maxTokens?: number;
  toolsEnabled?: boolean;
}

export interface AIProvider {
  sendMessage(messages: Message[], model: Model, options?: ChatOptions): Promise<ChatResponse>;
  getAvailableModels(): Model[];
}

/**
 * Configuration for the chat application
 */
export interface ChatConfig {
  maxMessages?: number;
  autoSave?: boolean;
  theme?: 'light' | 'dark';
}