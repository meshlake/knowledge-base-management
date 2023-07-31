import React, { useState, useRef } from 'react';
import { Button } from 'antd';
import { getOrganizations } from '@/services/organization/api';
import { ActionType, PageContainer, ProColumns, ProTable } from '@ant-design/pro-components';
import AddOrgForm from './component/AddForm';
import EditOrgForm from './component/EditForm';
import styles from './index.less';

const OrgManagement = () => {
  const ref = useRef<ActionType>();

  const handleRefresh = () => ref?.current?.reload();

  const [addVisible, setAddVisible] = useState(false);
  const [curOrg, setCurOrg] = useState<ORGANIZATION_API.Organization>(
    {} as ORGANIZATION_API.Organization,
  );
  const [editVisible, setEditVisible] = useState(false);

  const handleEdit = (editedOrg: ORGANIZATION_API.Organization) => {
    setCurOrg(editedOrg);
    setEditVisible(true);
  };

  const handleAdd = () => {
    setAddVisible(true);
  };

  const refresh = (needRefresh: boolean) => {
    setAddVisible(false);
    setEditVisible(false);
    if (needRefresh) {
      handleRefresh();
    }
  };

  // 表格列配置
  const columns: ProColumns<ORGANIZATION_API.Organization>[] = [
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
      title: '操作',
      render: (dom, entity) => (
        <>
          <Button type="link" onClick={() => handleEdit(entity)}>
            编辑
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
      <ProTable<ORGANIZATION_API.Organization, API.PageParams>
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
          let data: ORGANIZATION_API.Organization[] = [];
          let total = 0;
          try {
            const response = await getOrganizations({
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
      <AddOrgForm visible={addVisible} refresh={refresh}></AddOrgForm>
      <EditOrgForm visible={editVisible} data={curOrg} refresh={refresh}></EditOrgForm>
    </PageContainer>
  );
};

export default OrgManagement;
