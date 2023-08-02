import request from '@/utils/request';

export function getChatbotList() {
  return request<DEFAULT_API.Paginate<Chatbot_API.Chatbot>>('/chatbot/list', {
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export function getChatbot(params: { id: string }) {
  return request<DEFAULT_API.Response<Chatbot_API.Chatbot>>(`/chatbot/${params.id}`, {
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export function createChatbot(data: Chatbot_API.ChatbotCreate) {
  return request<DEFAULT_API.Response<Chatbot_API.Chatbot>>('/chatbot', {
    method: 'POST',
    data,
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}
