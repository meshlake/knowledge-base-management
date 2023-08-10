import { PageContainer, ProList } from '@ant-design/pro-components';
import styles from '@/components/CommonCard/index.less';
import KnowledgeBase from './types';

export default function ContentLayout({
  title,
  actionRef,
  render,
  children,
}: {
  title: string;
  actionRef: React.MutableRefObject<any>;
  children?: React.ReactNode;
  render: KnowledgeBase.ContentItemRender<any>;
}) {
  return (
    <PageContainer
      className={styles.pageContainer}
      header={{
        title: title,
      }}
    >
      <ProList
        pagination={false}
        bordered={false}
        ghost
        actionRef={actionRef}
        request={render.fetch}
        metas={{ content: { render: render.display } }}
        onItem={render.events}
        rowKey={'id'}
        grid={{ gutter: 16, column: 3 }}
        rowClassName={styles.cardItem}
      ></ProList>
      {children}
    </PageContainer>
  );
}
