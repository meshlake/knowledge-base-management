import { ProList } from '@ant-design/pro-components';
import KnowledgeBase from '@/components/ContentLayout/types';
import { KnowledgeBaseTagModel } from '@/pages/KnowledgeBase/types';
import { ActionType } from '@ant-design/pro-components';
import React, { useEffect } from 'react';
import styles from './index.less';
import ManageableSecondaryTag from '@/components/ManagableSecondaryTag';
import { getKnowledgeBaseTags } from '@/services/knowledgeBaseTags';

type SecondaryTagManagerProps = {
  model: KnowledgeBaseTagModel;
};

export default function SecondaryTagManager(props: SecondaryTagManagerProps) {
  const { model } = props;
  const actionRef = React.useRef<ActionType>(null);

  const render: KnowledgeBase.ContentItemRender<KnowledgeBaseTagModel> = {
    fetch: async () => {
      const data =
        (await getKnowledgeBaseTags(model.knowledge_base_id, model.id).then((res) => res.items)) ||
        [];
      data.push({
        id: '',
        name: '',
        parent_id: model.id,
        knowledge_base_id: model.knowledge_base_id,
      } as KnowledgeBaseTagModel);
      return {
        data: data,
      };
    },
    display: (dom: React.ReactNode, item: KnowledgeBaseTagModel) => {
      return (
        <ManageableSecondaryTag
          model={item}
          mode={item.id ? 'view' : 'create'}
          onDeleted={() => actionRef.current?.reload()}
          onCreated={() => actionRef.current?.reload()}
        />
      );
    },
    events: (item: KnowledgeBaseTagModel) => {
      return {
        onClick: () => {},
        onDoubleClick: () => {
          if (item.id) {
            console.info(`Edit mode activated, item => ${item.id}`);
          }
        },
      };
    },
  };

  useEffect(() => {
    actionRef.current?.reload();
  }, [model.id]);
  return (
    <>
      <ProList
        pagination={false}
        bordered={false}
        ghost
        actionRef={actionRef}
        request={render.fetch}
        metas={{ content: { render: render.display } }}
        onItem={render.events}
        rowKey={'id'}
        grid={{ gutter: 16, column: 5, lg: 3, md: 3, sm: 2, xs: 1 }}
        rowClassName={styles.TagRow}
        itemCardProps={{
          className: styles.TagItemCard,
          bodyStyle: { padding: 0 },
        }}
      ></ProList>
    </>
  );
}
