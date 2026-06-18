import { nextTick } from "vue"
import { ChatMessage } from "../type"

export function getHistoryChat(list: any, chatArr: ChatMessage[]) {
  for (let i = 0; i < list.data.data.length; i += 2) {
    const chatMsg: ChatMessage = {
      personMessage: { content: '' },
      aiMessage: { content: '' }
    }
    if (list.data.data[i].role === 'user') {
      chatMsg.personMessage.content = list.data.data[i].content
    }
    if (list.data.data[i + 1].role === 'user') {
      chatMsg.personMessage.content = list.data.data[i + 1].content
    }
    if (list.data.data[i].role === 'assistant') {
      chatMsg.aiMessage.content = list.data.data[i].content
    }
    if (list.data.data[i + 1].role === 'assistant') {
      chatMsg.aiMessage.content = list.data.data[i + 1].content
    }
    chatArr.push(chatMsg)
    scrollBottom()
  }
}

export function scrollBottom(container?: HTMLElement | null) {
  nextTick(() => {
    if (container) {
      container.scrollTop = container.scrollHeight
    }
  })
}
