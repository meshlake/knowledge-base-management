// @ts-ignore
/* eslint-disable */
import request from '@/utils/request';

export async function getAllOrganizations() {
  return request<DEFAULT_API.Response<ORGANIZATION_API.Organization[]>>('/organizations/all', {
    method: 'GET',
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export async function getOrganizations(params: { page: number; size: number }) {
  return request<DEFAULT_API.Paginate<ORGANIZATION_API.Organization>>('/organizations', {
    method: 'GET',
    params,
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export async function createOrganization(data: ORGANIZATION_API.OrganizationCreate) {
  return request<DEFAULT_API.Response<ORGANIZATION_API.Organization>>('/organizations', {
    method: 'POST',
    data,
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export async function updateOrganization(data: ORGANIZATION_API.OrganizationUpdate) {
  return request<DEFAULT_API.Response<ORGANIZATION_API.Organization>>(`/organizations/${data.id}`, {
    method: 'PUT',
    data,
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}
