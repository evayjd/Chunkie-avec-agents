import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ChatMessage } from '@/types'
import { sendChat } from '@/utils/api'

export const useChatStore = defineStore('chat', () => {
  const messages = ref<ChatMessage[]>([])
  const conversationId = ref<string | undefined>()
  const thinking = ref(false)
  const error = ref<string | null>(null)

  async function send(query: string, documentIds?: string[], language?: string) {
    thinking.value = true
    error.value = null
    const userMsg: ChatMessage = {
      role: 'user',
      content: query,
      timestamp: new Date().toISOString(),
    }
    messages.value.push(userMsg)

    try {
      const res = await sendChat(query, conversationId.value, documentIds, language)
      conversationId.value = res.conversation_id
      const assistantMsg: ChatMessage = {
        id: res.message_id,
        role: 'assistant',
        content: res.answer,
        citations: res.citations,
        is_grounded: res.is_grounded,
        timestamp: new Date().toISOString(),
      }
      messages.value.push(assistantMsg)
      return assistantMsg
    } catch (e: any) {
      error.value = e.message
    } finally {
      thinking.value = false
    }
  }

  function clearConversation() {
    messages.value = []
    conversationId.value = undefined
    error.value = null
  }

  return { messages, conversationId, thinking, error, send, clearConversation }
})
