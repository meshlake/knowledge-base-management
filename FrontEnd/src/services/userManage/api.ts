// @ts-ignore
/* eslint-disable */
import request from '@/utils/request';

export async function getAllUsers(params: { page: number; size: number }) {
  return request<USER_MANAGE_API.AllUserRes>('/users', {
    method: 'GET',
    params,
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export async function updateUser(data: USER_MANAGE_API.UserUpdate) {
  return request<USER_MANAGE_API.User>(`/users/${data.id}`, {
    method: 'PUT',
    data,
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export async function createUser(data: USER_MANAGE_API.UserCreate) {
  return request<USER_MANAGE_API.User>(`/users`, {
    method: 'POST',
    data,
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}
