/**
 * Utilities for managing conversation storage in localStorage
 */

import type { Conversation, Message, Model } from '../types';

const STORAGE_KEY = 'chat-app-conversation';

export class ConversationStorage {
  static saveConversation(conversation: Conversation): void {
    try {
      const serialized = JSON.stringify(conversation);
      localStorage.setItem(STORAGE_KEY, serialized);
    } catch (error) {
      console.error('Failed to save conversation:', error);
    }
  }

  static loadConversation(): Conversation | null {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (!stored) return null;

      const parsed = JSON.parse(stored);
      return parsed as Conversation;
    } catch (error) {
      console.error('Failed to load conversation:', error);
      return null;
    }
  }

  static clearConversation(): void {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (error) {
      console.error('Failed to clear conversation:', error);
    }
  }

  static createNewConversation(model: Model): Conversation {
    const now = new Date().toISOString();
    return {
      id: this.generateId(),
      messages: [],
      model,
      createdAt: now,
      updatedAt: now
    };
  }

  static addMessage(conversation: Conversation, message: Message): Conversation {
    const updated = {
      ...conversation,
      messages: [...conversation.messages, message],
      updatedAt: new Date().toISOString()
    };
    this.saveConversation(updated);
    return updated;
  }

  static updateModel(conversation: Conversation, model: Model): Conversation {
    const updated = {
      ...conversation,
      model,
      updatedAt: new Date().toISOString()
    };
    this.saveConversation(updated);
    return updated;
  }

  private static generateId(): string {
    return `conv_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
  }
}

export const generateMessageId = (): string => {
  return `msg_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
};