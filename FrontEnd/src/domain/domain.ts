// @ts-ignore
let domain = (window && window.AUTHORITY) || '/api';

if (!(domain.startsWith('http://') || domain.startsWith('https://') || domain.startsWith('/'))) {
  domain = `http://${domain}`;
}

export const baseUrl = `${domain}`;
