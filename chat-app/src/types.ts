/**
 * Core types for the chat application
 */

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
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
  createdAt: Date;
  updatedAt: Date;
}

export interface ChatResponse {
  content: string;
  error?: string;
}

/**
 * Abstract interface for communicating with AI models
 */
export interface AIProvider {
  sendMessage(messages: Message[], model: Model): Promise<ChatResponse>;
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