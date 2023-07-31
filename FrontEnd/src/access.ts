/**
 * @see https://umijs.org/zh-CN/plugins/plugin-access
 * */
export default function access(initialState: { permissions?: any[] } | undefined) {
  const { permissions } = initialState ?? {};
  const pagePermissions = permissions?.filter((p) => p[1] === 'page').map((p) => p[2]);
  return {
    system: pagePermissions?.includes('/system'),
  };
}
