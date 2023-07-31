// @ts-ignore
/* eslint-disable */

declare namespace DEFAULT_API {
  type Response<T> = {
    data: T;
  };

  type Paginate<T> = {
    items: T[];
    total: number;
    page: number;
    size: number;
    pages: number;
  };
}
