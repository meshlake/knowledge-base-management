// @ts-nocheck
// This file is generated by Umi automatically
// DO NOT CHANGE IT MANUALLY!
import React from 'react';

export async function getRoutes() {
  const routes = {"1":{"path":"/user","layout":false,"id":"1"},"2":{"name":"login","path":"/user/login","parentId":"1","id":"2"},"3":{"path":"/welcome","name":"欢迎","icon":"smile","parentId":"ant-design-pro-layout","id":"3"},"4":{"path":"/","redirect":"/welcome","parentId":"ant-design-pro-layout","id":"4"},"5":{"path":"*","layout":false,"id":"5"},"6":{"name":"应用管理","path":"/application","access":"application","parentId":"ant-design-pro-layout","id":"6"},"7":{"name":"知识库模型","path":"/knowledgeModel","access":"knowledgeModel","parentId":"ant-design-pro-layout","id":"7"},"8":{"name":"知识库模型调试","path":"/chat","access":"chat","parentId":"ant-design-pro-layout","id":"8"},"9":{"name":"系统设置","path":"/system","access":"system","parentId":"ant-design-pro-layout","id":"9"},"10":{"name":"账号管理","path":"/system/users","parentId":"9","id":"10"},"11":{"name":"角色管理","path":"/system/roles","parentId":"9","id":"11"},"12":{"name":"组织管理","path":"/system/organizations","parentId":"9","id":"12"},"ant-design-pro-layout":{"id":"ant-design-pro-layout","path":"/","isLayout":true}} as const;
  return {
    routes,
    routeComponents: {
'1': require( './EmptyRoute').default,
'2': require('@/pages/User/Login/index.tsx').default,
'3': require('@/pages/Welcome.tsx').default,
'4': require( './EmptyRoute').default,
'5': require('@/pages/404.tsx').default,
'6': require('@/pages/Application/index.tsx').default,
'7': require('@/pages/KnowledgeModel/index.tsx').default,
'8': require('@/pages/Chat/index.tsx').default,
'9': require( './EmptyRoute').default,
'10': require('@/pages/System/UserManagement/index.tsx').default,
'11': require('@/pages/System/RoleManagement/index.tsx').default,
'12': require('@/pages/System/OrganizationManagement/index.tsx').default,
'ant-design-pro-layout': require('/Users/zhaofengnian/Desktop/meshlake-workspace/doc-search-management/FrontEnd/src/.umi-test/plugin-layout/Layout.tsx').default,
},
  };
}
