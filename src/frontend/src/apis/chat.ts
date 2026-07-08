import { fetchEventSource } from '@microsoft/fetch-event-source';

export interface Chat {
  dialogId: string
  userInput: string
  fileUrl?: string
}

export function sendMessage(data: Chat, onmessage: any, onclose: any) {
  const ctrl = new AbortController();

  fetchEventSource('/api/v1/completion', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
    },
    body: JSON.stringify({
      ...(data.fileUrl
        ? {
            dialog_id: data.dialogId,
            user_input: data.userInput,
            file_url: data.fileUrl,
          }
        : {
            dialog_id: data.dialogId,
            user_input: data.userInput,
          }),
    }),
    signal: ctrl.signal,
    openWhenHidden: true,
    async onopen(response: any) {
      if (response.status !== 200) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    },
    onmessage(msg: any) {
      try {
        onmessage(msg);
      } catch (error) {
        console.error('处理消息时出错:', error);
      }
    },
    onclose() {
      onclose();
    },
    onerror(err: any) {
      console.error('聊天连接错误:', err);
      ctrl.abort();
      throw err;
    }
  });

  return ctrl;
}


