import request from '@/utils/request';

export function getConversationList(params: DEFAULT_API.PageParams) {
  return request<DEFAULT_API.Paginate<Conversation_API.Conversation>>('/conversations', {
    params,
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export function getConversation(id: string) {
  return request<Conversation_API.Conversation>(`/conversations/${id}`, {
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export function createConversation(data: Conversation_API.ConversationCteate) {
  return request<Conversation_API.Conversation>('/conversations', {
    method: 'POST',
    data,
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export function sendMessage(id: string, data: Conversation_API.MessageCreate) {
  return request<DEFAULT_API.Paginate<Conversation_API.Message>>(`/conversations/${id}/messages`, {
    method: 'POST',
    data,
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export function deleteConversation(id: string) {
  return request(`/conversations/${id}`, {
    method: 'DELETE',
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}
