// @ts-ignore
/* eslint-disable */
import request from '@/utils/request';

export async function get_review_items(params: { page: number; size: number }) {
  return request<DEFAULT_API.Paginate<REVIEW_API.SimilarKnowledge>>('/review', {
    method: 'GET',
    params,
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export async function review(data: REVIEW_API.Review) {
  return request<DEFAULT_API.Response<string>>(`/review/${data.id}`, {
    method: 'PUT',
    params: {
      action: data.action,
    },
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}
