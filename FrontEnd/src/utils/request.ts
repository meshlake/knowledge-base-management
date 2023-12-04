import { notification } from 'antd';
import { extend } from 'umi-request';
import { history, getIntl } from 'umi';

const loginPath = '/user/login';

interface RequestError extends Error {
  data?: any;
  response: Response;
}

const errorHandler = (error: RequestError): Response => {
  const { response, message } = error;
  // server returned errors
  if (message.startsWith('ErrorCode')) {
    throw new Error(message.substring(10));
  }
  // http error or network error
  if (response && response.status) {
    const { status, statusText } = response;
    switch (status) {
      case 401:
        history.push(loginPath);
        break;
      case 403:
        notification.error({
          message: '无权限',
        });
        history.push('/');
        break;
      case 499:
        notification.error({
          message: '该标签被知识点引用，无法删除',
        });
        break;
      default:
        notification.error({
          message: 'Request error!',
          description: `${status}: ${statusText}`,
        });
    }
    throw error;
  } else {
    notification.error({
      message: 'Network error!',
    });
    throw error;
  }
};

const request = extend({
  prefix: '/api',
  errorHandler,
  retry: 3,
  retryDelay: 1000,
});

request.interceptors.response.use(async (response) => {
  const { status } = response;
  if (status >= 200 && status < 300) {
    let res;
    try {
      res = await response.clone().json();
    } catch (err) {
      console.warn(err);
    }
    if (res?.errors?.length) {
      const intlMessages = getIntl().messages;
      notification.error({
        message: intlMessages[res.errors[0].code] || 'Error',
      });
      throw new Error(`ErrorCode:${res.errors[0].code}`);
    } else if (res?.data !== undefined) {
      return res;
    }
  }
  return response;
});

export default request;
