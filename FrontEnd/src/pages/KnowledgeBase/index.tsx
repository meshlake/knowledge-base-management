import React from 'react';
import { Modal } from 'antd';
import ContentLayout from '../../components/ContentLayout';
import { deleteKnowledgeBase, getKnowledgeBaseList } from '@/services/knowledgeBase';
import { KnowledgeBaseModel } from './types';
import KnowledgeBase from '@/components/ContentLayout/types';
import CommonCard from '@/components/CommonCard';
import { ExclamationCircleOutlined } from '@ant-design/icons';
import { ActionType } from '@ant-design/pro-components';
import AddKnowledgeBaseItemForm from './components/AddForm';
import { history } from '@umijs/max';

const { confirm } = Modal;

export default function KnowledgeBaseList() {
  const actionRef = React.useRef<ActionType>();
  const [creation, toggleCreation] = React.useState(false); // 控制创建知识库的弹窗
  const handleRefresh = () => {
    toggleCreation(false);
    actionRef?.current?.reload();
  };

  const handleDelete = (item: KnowledgeBaseModel) => {
    confirm({
      title: '请谨慎操作',
      icon: <ExclamationCircleOutlined style={{ color: '#F40909' }} />,
      content: `确定删除知识库【${item.name}】吗？删除不可恢复，并会影响相关机器人模型与应用。`,
      okText: '确定删除',
      cancelText: '取消',
      onOk() {
        return deleteKnowledgeBase(item.id).then(() => handleRefresh());
      },
      onCancel() {},
    });
  };
  const knowledgeBaseContentItemRender: KnowledgeBase.ContentItemRender<KnowledgeBaseModel> = {
    fetch: async () => {
      const data = await getKnowledgeBaseList();
      return {
        data: [...data?.items, { id: -1, name: '', description: '' } as KnowledgeBaseModel],
      };
    },
    display: (dom: React.ReactNode, item: KnowledgeBaseModel) => {
      return item.id !== -1 ? (
        <CommonCard key={item.id} data={item} deleteable handleDelete={() => handleDelete(item)} />
      ) : (
        <CommonCard
          key={item.id}
          data={{
            id: item.id,
            name: '创建知识库',
            description: '基于业务需要创建知识库，导入对应知识点，用于训练AI机器人。',
          }}
          icon="/images/add_icon.png"
          iconSize={30}
          iconBorderRadius={0}
        />
      );
    },
    events: (item: KnowledgeBaseModel) => {
      return {
        onClick: () => {
          if (item.id === -1) {
            toggleCreation(true);
          } else {
            history.push(`/knowledgeBase/${item.id}`);
          }
        },
      };
    },
  };
  return (
    <ContentLayout
      title={'知识库列表'}
      actionRef={actionRef}
      render={knowledgeBaseContentItemRender}
    >
      <AddKnowledgeBaseItemForm
        visible={creation}
        toggleVisible={toggleCreation}
        refetchItems={handleRefresh}
      />
    </ContentLayout>
  );
}
