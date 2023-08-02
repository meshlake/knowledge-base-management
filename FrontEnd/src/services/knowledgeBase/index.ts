import { KnowledgeBaseModel } from '@/pages/KnowledgeBase/types';
import request from '@/utils/request';

export function getKnowledgeBaseList() {
  return request<DEFAULT_API.Paginate<KnowledgeBaseModel>>('/knowledge_bases', {
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export function createKnowledgeBase(data: KnowledgeBaseModel) {
  return request<DEFAULT_API.Response<KnowledgeBaseModel>>('/knowledge_bases', {
    method: 'POST',
    data,
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export function deleteKnowledgeBase(id: number) {
  return request(`/knowledge_bases/${id}`, {
    method: 'DELETE',
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export function getKnowledgeBase(id: number) {
  return request(`/knowledge_bases/${id}`, {
    method: 'GET',
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export function updateKnowledgeBase(data: Omit<KnowledgeBaseModel, 'userId'>) {
  return request<DEFAULT_API.Response<KnowledgeBaseModel>>(`/knowledge_bases/${data.id}`, {
    method: 'PUT',
    data,
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}