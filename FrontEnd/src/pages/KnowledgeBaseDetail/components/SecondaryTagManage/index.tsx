import { ProList } from '@ant-design/pro-components';
import InfiniteScroll from 'react-infinite-scroll-component';
import { KnowledgeBaseTagModel } from '@/pages/KnowledgeBase/types';
import { ActionType } from '@ant-design/pro-components';
import React, { useEffect, useState } from 'react';
import styles from './index.less';
import ManageableSecondaryTag from '@/components/ManagableSecondaryTag';
import { getKnowledgeBaseTags } from '@/services/knowledgeBaseTags';

type SecondaryTagManagerProps = {
  model: KnowledgeBaseTagModel;
};

export default function SecondaryTagManager(props: SecondaryTagManagerProps) {
  const { model } = props;
  const actionRef = React.useRef<ActionType>(null);
  const [loading, setLoading] = useState(false);
  const [listData, setListData] = useState<KnowledgeBaseTagModel[]>([]);
  const [page, setPage] = useState(1);
  const [totalPage, setTotalPage] = useState(1);

  const loadMoreData = async (currentPage: number) => {
    if (loading) {
      return;
    }
    setLoading(true);
    try {
      const result = await getKnowledgeBaseTags(
        model.knowledge_base_id,
        model.id,
        currentPage + 1,
        50,
      );
      setLoading(false);
      if (result) {
        const oldList = currentPage === 0 ? [] : listData;
        if (result.page < result.pages) {
          setListData([...oldList, ...result.items]);
        } else {
          const newTag = {
            id: '',
            name: '',
            parent_id: model.id,
            knowledge_base_id: model.knowledge_base_id,
          } as KnowledgeBaseTagModel;
          setListData([...oldList, ...result.items, newTag]);
        }
        setPage(result.page);
        setTotalPage(result.pages);
      }
    } catch (error: any) {
      console.log(error.message);
      setLoading(false);
    }
  };

  useEffect(() => {
    setPage(0);
    setTotalPage(0);
    setListData([]);
    loadMoreData(0);
  }, [model.id]);

  const render = {
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

  return (
    <>
      <InfiniteScroll
        dataLength={listData.length}
        next={() => {
          loadMoreData(page);
        }}
        hasMore={page < totalPage}
        loader={null}
        scrollableTarget="scrollableDiv"
      >
        <ProList
          bordered={false}
          ghost
          loading={loading}
          style={{ height: '100%', overflow: 'auto' }}
          actionRef={actionRef}
          dataSource={listData}
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
      </InfiniteScroll>
    </>
  );
}
