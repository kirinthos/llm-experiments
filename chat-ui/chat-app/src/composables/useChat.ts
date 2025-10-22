import { ref, computed, readonly } from 'vue'
import type { AIProvider, Model, Message, Conversation } from '../types'
import { APIProvider } from '../providers/apiProvider'
import type { Tool } from '../providers/apiProvider'
import { ConversationStorage, generateMessageId } from '../utils/storage'

export function useChat() {
  const provider = ref<AIProvider>()
  const conversation = ref<Conversation>()
  const isLoading = ref(false)
  const connectionError = ref<string>('')
  const isConnected = ref(false)
  const availableTools = ref<Tool[]>([])
  const toolsEnabled = ref(true)

  // Computed properties
  const messages = computed(() => conversation.value?.messages || [])
  const currentModel = computed(() => conversation.value?.model)
  const availableModels = computed(() => provider.value?.getAvailableModels() || [])

  async function initializeProvider() {
    try {
      connectionError.value = ''
      isConnected.value = false
      
      const apiProvider = new APIProvider()
      await apiProvider.initialize()
      
      // Check if API is healthy
      const isHealthy = await apiProvider.healthCheck()
      if (!isHealthy) {
        throw new Error('API server health check failed')
      }
      
      provider.value = apiProvider
      availableTools.value = apiProvider.getAvailableTools()
      isConnected.value = true
      console.log('✅ Connected to API server')
      
    } catch (error) {
      console.error('Failed to initialize provider:', error)
      const errorMessage = error instanceof Error ? error.message : 'Unknown connection error'
      connectionError.value = `Failed to connect to API server: ${errorMessage}`
      isConnected.value = false
      provider.value = undefined
      availableTools.value = []
    }
  }

  function loadOrCreateConversation() {
    const stored = ConversationStorage.loadConversation()
    if (stored) {
      conversation.value = stored
    } else {
      const defaultModel = availableModels.value[0]
      conversation.value = ConversationStorage.createNewConversation(defaultModel)
    }
  }

  async function sendMessage(content: string): Promise<void> {
    if (isLoading.value || !content.trim() || !provider.value || !conversation.value || !isConnected.value) {
      return
    }

    isLoading.value = true

    try {
      // Add user message
      const userMessage: Message = {
        id: generateMessageId(),
        role: 'user',
        content: content.trim(),
        timestamp: new Date().toISOString()
      }

      conversation.value.messages.push(userMessage)
      ConversationStorage.saveConversation(conversation.value)

      // Get AI response
      const allMessages = [...conversation.value.messages]
      const response = await provider.value.sendMessage(
        allMessages,
        conversation.value.model,
        {
          temperature: 0.7,
          maxTokens: 1000,
          toolsEnabled: toolsEnabled.value
        }
      )

      // Add assistant message
      const assistantMessage: Message = {
        id: generateMessageId(),
        role: 'assistant',
        content: response.content,
        timestamp: new Date().toISOString(),
        thinkingSteps: response.thinkingSteps
      }

      conversation.value.messages.push(assistantMessage)
      ConversationStorage.saveConversation(conversation.value)

    } catch (error) {
      console.error('Error sending message:', error)
      
      // Add error message
      const errorMessage: Message = {
        id: generateMessageId(),
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date().toISOString()
      }

      conversation.value.messages.push(errorMessage)
      ConversationStorage.saveConversation(conversation.value)
    } finally {
      isLoading.value = false
    }
  }

  function changeModel(newModel: Model) {
    if (!conversation.value) return

    conversation.value.model = newModel
    ConversationStorage.saveConversation(conversation.value)

    // Add model change notification
    const notification: Message = {
      id: generateMessageId(),
      role: 'system',
      content: `Switched to ${newModel.name} (${newModel.provider})`,
      timestamp: new Date().toISOString()
    }

    conversation.value.messages.push(notification)
    ConversationStorage.saveConversation(conversation.value)
  }

  function clearChat() {
    if (!conversation.value) return

    conversation.value.messages = []
    ConversationStorage.saveConversation(conversation.value)
  }

  function toggleTools() {
    toolsEnabled.value = !toolsEnabled.value
  }

  async function initialize() {
    await initializeProvider()
    loadOrCreateConversation()
  }

  return {
    // State
    conversation: readonly(conversation),
    isLoading: readonly(isLoading),
    connectionError: readonly(connectionError),
    isConnected: readonly(isConnected),
    availableTools: readonly(availableTools),
    toolsEnabled: readonly(toolsEnabled),
    
    // Computed
    messages,
    currentModel,
    availableModels,
    
    // Methods
    initialize,
    sendMessage,
    changeModel,
    clearChat,
    toggleTools
  }
}