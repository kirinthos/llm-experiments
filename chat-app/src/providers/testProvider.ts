/**
 * Test provider for development - simulates AI responses
 */

import type { AIProvider, Model, Message, ChatResponse } from '../types';

export class TestAIProvider implements AIProvider {
  private delay: number;

  constructor(delay: number = 1000) {
    this.delay = delay;
  }

  async sendMessage(messages: Message[], model: Model): Promise<ChatResponse> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, this.delay));

    const lastMessage = messages[messages.length - 1];
    
    // Generate different responses based on the model
    const responses = {
      openai: this.generateOpenAIResponse(lastMessage.content),
      gemini: this.generateGeminiResponse(lastMessage.content),
      claude: this.generateClaudeResponse(lastMessage.content)
    };

    const response = responses[model.provider] || "I'm a test AI assistant. How can I help you?";

    return {
      content: response
    };
  }

  getAvailableModels(): Model[] {
    return [
      {
        id: 'gpt-4o-mini',
        name: 'GPT-4o Mini',
        provider: 'openai',
        description: 'Fast and efficient OpenAI model'
      },
      {
        id: 'gpt-4',
        name: 'GPT-4',
        provider: 'openai',
        description: 'Most capable OpenAI model'
      },
      {
        id: 'gemini-1.5-flash',
        name: 'Gemini 1.5 Flash',
        provider: 'gemini',
        description: 'Fast Google Gemini model'
      },
      {
        id: 'gemini-1.5-pro',
        name: 'Gemini 1.5 Pro',
        provider: 'gemini',
        description: 'Advanced Google Gemini model'
      },
      {
        id: 'claude-3-sonnet',
        name: 'Claude 3 Sonnet',
        provider: 'claude',
        description: 'Anthropic Claude model'
      }
    ];
  }

  private generateOpenAIResponse(userMessage: string): string {
    const responses = [
      `As an OpenAI model, I'd say: ${userMessage.toLowerCase().includes('hello') ? 'Hello! How can I assist you today?' : 'That\'s an interesting question. Let me think about that...'}`,
      `From an OpenAI perspective: I can help you with various tasks including writing, analysis, math, and more.`,
      `OpenAI response: I understand you're asking about "${userMessage.substring(0, 30)}${userMessage.length > 30 ? '...' : ''}". How can I help?`
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  }

  private generateGeminiResponse(userMessage: string): string {
    const responses = [
      `Gemini here! ${userMessage.toLowerCase().includes('hello') ? 'Greetings! I\'m ready to help.' : 'I can assist with that request.'}`,
      `As Google's Gemini: I'm designed to be helpful, harmless, and honest in my responses.`,
      `Gemini response: That's a great question about "${userMessage.substring(0, 30)}${userMessage.length > 30 ? '...' : ''}". Let me help you with that.`
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  }

  private generateClaudeResponse(userMessage: string): string {
    const responses = [
      `Claude speaking: ${userMessage.toLowerCase().includes('hello') ? 'Hello there! I\'m Claude, happy to chat.' : 'I\'d be glad to help you with that.'}`,
      `From Claude: I aim to be helpful, harmless, and honest in all my interactions.`,
      `Claude's response: You've asked about "${userMessage.substring(0, 30)}${userMessage.length > 30 ? '...' : ''}". I'll do my best to provide a helpful answer.`
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  }
}