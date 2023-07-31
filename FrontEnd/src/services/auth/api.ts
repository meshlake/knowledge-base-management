// @ts-ignore
/* eslint-disable */
import request from '@/utils/request';

export async function getAllPermissions() {
  return request<DEFAULT_API.Response<AUTH_API.Permission[]>>('/auth/permissions', {
    method: 'GET',
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export async function getRolePermissions(role: string) {
  return request<DEFAULT_API.Response<string[][]>>(`/auth/roles/${role}/permissions`, {
    method: 'GET',
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export async function updateRolePermissions(role: string, permissions: AUTH_API.Permission[]) {
  return request<DEFAULT_API.Response<AUTH_API.Permission[]>>(`/auth/roles/${role}/permissions`, {
    method: 'PUT',
    data: permissions,
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}
