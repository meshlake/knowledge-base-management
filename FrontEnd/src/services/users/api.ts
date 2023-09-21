// @ts-ignore
/* eslint-disable */
import request from '@/utils/request';

/** 登录接口 POST /users/login */
export async function login(body: USER_API.LoginParams, options?: { [key: string]: any }) {
  let formBody = [];
  formBody.push(encodeURIComponent('username') + '=' + encodeURIComponent(body.username as string));
  formBody.push(encodeURIComponent('password') + '=' + encodeURIComponent(body.password as string));
  let formBodyStr = formBody.join('&');
  return request<USER_API.LoginResult>('/users/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    },
    data: formBodyStr,
    ...(options || {}),
  });
}

/** 登录接口 POST /users/login */
export async function getCurrentUser() {
  return request<USER_API.CurrentUser>('/users/me', {
    method: 'GET',
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
  });
}

export async function updatePassword(data: USER_API.UpdatePasswordParams) {
  return request<USER_API.CurrentUser>('/users/me', {
    method: 'PUT',
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('access_token'),
    },
    data,
  });
}
