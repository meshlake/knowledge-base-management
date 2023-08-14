import { KnowledgeBaseTagModel } from '@/pages/KnowledgeBase/types';
import request from '@/utils/request';

export function getKnowledgeBaseTags(id: number, parentId?: number) {
  return request<DEFAULT_API.Paginate<KnowledgeBaseTagModel>>(`/knowledge_bases/${id}/tags`, {
    method: 'GET',
    params: {
      parent_id: parentId,
    },
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export function createKnowledgeBaseTag(id: number, data: KnowledgeBaseTagModel) {
  return request<DEFAULT_API.Response<KnowledgeBaseTagModel>>(`/knowledge_bases/${id}/tags`, {
    method: 'POST',
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
    data,
  });
}

export function persistKnowledgeBaseTag(id: number, tagId: number, data: KnowledgeBaseTagModel) {
  if (!tagId) {
    return createKnowledgeBaseTag(id, data);
  }
  return request(`/knowledge_bases/${id}/tags/${tagId}`, {
    method: 'PATCH',
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
    data,
  }).then((res) => {
    return {
      ...data,
      id: tagId,
      knowledge_base_id: id,
      ...res,
    };
  });
}

export function deleteKnowledgeBaseTag(id: number, tagId: number) {
  return request(`/knowledge_bases/${id}/tags/${tagId}`, {
    method: 'DELETE',
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export function getKnowledgeBaseAllTags(knowledgeBaseId?: number) {
  return request<KnowledgeBaseTagModel[]>(`/knowledge_bases/tags/all`, {
    method: 'GET',
    params: {
      knowledge_base_id: knowledgeBaseId,
    },
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}
