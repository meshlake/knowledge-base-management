import React, { useState, useRef } from 'react';
import { Button } from 'antd';
import { getRoles } from '@/services/role/api';
import { ActionType, PageContainer, ProColumns, ProTable } from '@ant-design/pro-components';
import AddRoleForm from './component/AddForm';
import AuthForm from './component/AuthForm';
import styles from './index.less';

const RoleManagement = () => {
  const ref = useRef<ActionType>();

  const handleRefresh = () => ref?.current?.reload();

  const [addVisible, setAddVisible] = useState(false);
  const [authVisible, setAuthVisible] = useState(false);
  const [curRole, setCurRole] = useState<string>('');

  const handleAdd = () => {
    setAddVisible(true);
  };

  const refresh = (needRefresh: boolean) => {
    setAddVisible(false);
    if (needRefresh) {
      handleRefresh();
    }
  };

  // 表格列配置
  const columns: ProColumns<ROLE_API.Role>[] = [
    {
      title: 'ID',
      dataIndex: 'id',
    },
    {
      title: '名称',
      dataIndex: 'name',
    },
    {
      title: '编码',
      dataIndex: 'code',
    },
    {
      title: '描述',
      dataIndex: 'description',
    },
    {
      title: '操作',
      render: (dom, entity) => (
        <>
          <Button
            type="link"
            onClick={() => {
              setCurRole(entity.code);
              setAuthVisible(true);
            }}
          >
            授权
          </Button>
        </>
      ),
    },
  ];

  return (
    <PageContainer className={styles.userManage}>
      <div className={styles.userManageHeader}>
        <Button type="primary" onClick={handleAdd}>
          新增
        </Button>
      </div>
      <ProTable<ROLE_API.Role, API.PageParams>
        actionRef={ref}
        rowKey="id"
        columns={columns}
        search={false}
        request={async (
          // 第一个参数 params 查询表单和 params 参数的结合
          // 第一个参数中一定会有 pageSize 和  current ，这两个参数是 antd 的规范
          //@ts-ignore
          params: T & {
            pageSize: number;
            current: number;
          },
        ) => {
          // 这里需要返回一个 Promise,在返回之前你可以进行数据转化
          // 如果需要转化参数可以在这里进行修改
          let success = true;
          let data: ROLE_API.Role[] = [];
          let total = 0;
          try {
            const response = await getRoles({
              page: params.current,
              size: params.pageSize,
            });
            data = response.items;
            total = response.total;
          } catch (error) {
            success = false;
          }
          return {
            data,
            // success 请返回 true，
            // 不然 table 会停止解析数据，即使有数据
            success,
            // 不传会使用 data 的长度，如果是分页一定要传
            total,
          };
        }}
      />
      <AddRoleForm visible={addVisible} refresh={refresh}></AddRoleForm>
      <AuthForm
        visible={authVisible}
        onClose={() => setAuthVisible(false)}
        role={curRole}
      ></AuthForm>
    </PageContainer>
  );
};

export default RoleManagement;
