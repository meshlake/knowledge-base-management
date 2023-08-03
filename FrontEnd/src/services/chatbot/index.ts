import request from '@/utils/request';

export function getChatbotList() {
  return request<Chatbot_API.Chatbot[]>('/chatbots/all', {
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export function getChatbot(params: { id: string }) {
  return request<DEFAULT_API.Response<Chatbot_API.Chatbot>>(`/chatbots/${params.id}`, {
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export function createChatbot(data: Chatbot_API.ChatbotCreate) {
  return request<DEFAULT_API.Response<Chatbot_API.Chatbot>>('/chatbots', {
    method: 'POST',
    data,
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export function deleteChatbot(id: string) {
  return request(`/chatbots/${id}`, {
    method: 'DELETE',
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}
