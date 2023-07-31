// @ts-ignore
/* eslint-disable */
import request from '@/utils/request';

export async function getAllRoles() {
  return request<DEFAULT_API.Response<ROLE_API.Role[]>>('/roles/all', {
    method: 'GET',
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export async function getRoles(params: { page: number; size: number }) {
  return request<DEFAULT_API.Paginate<ROLE_API.Role>>('/roles', {
    method: 'GET',
    params,
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export async function createRole(data: ROLE_API.RoleCreate) {
  return request<DEFAULT_API.Response<ROLE_API.Role>>('/roles', {
    method: 'POST',
    data,
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}
