import request from '@/utils/request';

export function getKnowledgeItems(
  knowledge_base_id: number,
  page: number,
  search?: {
    filepath?: string;
    tag_id?: number;
    content?: string;
  },
  size: number = 15,
) {
  return request<DEFAULT_API.Paginate<KNOWLEDGE_ITEM_API.KnowledgeItem>>(
    `/knowledge_bases/${knowledge_base_id}/item`,
    {
      headers: {
        authorization: 'Bearer ' + localStorage.getItem('access_token'),
      },
      params: {
        page,
        size,
        filepath: search?.filepath,
        tag_id: search?.tag_id,
        search: search?.content,
      },
    },
  );
}

export function createKnowledgeItem(
  knowledge_base_id: number,
  data: KNOWLEDGE_ITEM_API.KnowledgeItemCreate,
) {
  return request<
    DEFAULT_API.Response<KNOWLEDGE_ITEM_API.KnowledgeItemCreate & { isNeedReview: boolean }>
  >(`/knowledge_bases/${knowledge_base_id}/item`, {
    method: 'POST',
    data,
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export function deleteKnowledgeItem(id: number) {
  return request(`/knowledge_bases/item/${id}`, {
    method: 'DELETE',
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export function updateKnowledgeItem(data: KNOWLEDGE_ITEM_API.KnowledgeItemUpdate) {
  return request<DEFAULT_API.Response<KNOWLEDGE_ITEM_API.KnowledgeItemUpdate>>(
    `/knowledge_bases/item/${data.id}`,
    {
      method: 'PUT',
      data,
      headers: {
        authorization: 'Bearer ' + localStorage.getItem('access_token'),
      },
    },
  );
}
