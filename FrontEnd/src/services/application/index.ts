import request from '@/utils/request';

export function getApplicationList() {
  return request<Application_API.Application[]>('/applications/all', {
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export function getApplication(id: string) {
  return request<Application_API.Application>(`/applications/${id}`, {
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export function createApplication(data: Application_API.ApplicationCreate) {
  return request<Application_API.Application>('/applications', {
    method: 'POST',
    data,
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export function updateApplication(id: string, data: Application_API.ApplicationUpdate) {
  return request<Application_API.Application>(`/applications/${id}`, {
    method: 'PUT',
    data,
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export function deleteApplication(id: string) {
  return request(`/applications/${id}`, {
    method: 'DELETE',
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export async function getWechatBotInfo(id: string) {
  return request<DEFAULT_API.Response<Application_API.ApplicationLoginInfo>>(`/api/bot/${id}`, {
    method: 'GET',
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export async function wechatBotLogout(id: string) {
  return request<DEFAULT_API.Response<any>>(`/api/bot/${id}/logout`, {
    method: 'POST',
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}
