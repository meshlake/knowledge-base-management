import request from '@/utils/request';

export function getFiles(knowledge_base_id: number) {
  return request<DEFAULT_API.Response<FILE_API.File[]>>(`/files`, {
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
    params: {
      knowledge_base_id,
    },
  });
}

export function createFile(data: FILE_API.FileCreate) {
  return request<DEFAULT_API.Response<FILE_API.FileCreate>>(`/files`, {
    method: 'POST',
    data,
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}
