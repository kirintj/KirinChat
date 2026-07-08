import { request } from "../utils/request"
import { DialogCreateType } from '../type'

// 主要创建对话窗口的信息  json 格式
export function createDialogAPI(data: DialogCreateType) {
  return request({
    url: '/api/v1/dialog',
    method: 'POST',
    data: {
      name: data.name,
      agent_id: data.agent_id,
      agent_type: data.agent_type
    }
  })
}

// 主要删除对话窗口的信息  json 格式
export function deleteDialogAPI(dialogId:string) {
  return request({
    url: '/api/v1/dialog',
    method: 'DELETE',
    data: {
      dialog_id: dialogId
    }
  })
}

// 主要获得对话列表的功能
export function getDialogListAPI() {
  return request({
    url: '/api/v1/dialog/list',
    method: 'GET',
  })
}

// 获取历史消息记录 - 根据对话ID
export function getHistoryMsgAPI(dialogId: string) {
  return request({
    url: '/api/v1/history',
    method: 'GET',
    params: {
      dialog_id: dialogId
    }
  })
}
