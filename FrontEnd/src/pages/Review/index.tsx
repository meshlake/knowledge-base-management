import { Button, Col, Divider, List, Row, Spin } from 'antd';
import React, { useEffect, useState } from 'react';
import Styles from './index.less';
import InfiniteScroll from 'react-infinite-scroll-component';
import KnowledgeItem from './components/KnowledgeItem';
import { get_review_items, review } from '@/services/review/api';
import { CheckOutlined } from '@ant-design/icons';

const App: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<REVIEW_API.SimilarKnowledge[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);

  const loadMoreData = async () => {
    if (loading) {
      return;
    }
    setLoading(true);
    try {
      const { items, total } = await get_review_items({ page: page, size: 10 });
      setData([...data, ...items]);
      setTotal(total);
      setPage(page + 1);
    } catch (error) {
      console.log(error);
    }
    setLoading(false);
  };

  const handleReview = async (id: number, action: 'ADD' | 'NEGLECT' | 'REPLACE' | 'FUSION') => {
    setLoading(true);
    try {
      const res = await review({ id, action });
      if (res.data) {
        const newData = data.map((item) => {
          if (item.id === id) {
            item.status = 'PROCESSED';
          }
          return item;
        });
        setData(newData);
      }
    } catch (error) {
      console.log(error);
    }
    setLoading(false);
  };

  useEffect(() => {
    loadMoreData();
  }, []);

  return (
    <div className={Styles.review}>
      <div className={Styles.title}>相似知识审核</div>
      <div className={Styles.description}>发现{total}条新增知识与原有知识相似</div>
      <div className={Styles.content}>
        <InfiniteScroll
          dataLength={data.length}
          next={loadMoreData}
          hasMore={data.length < 50}
          loader={<Spin spinning={loading} />}
          endMessage={<Divider plain>没有更多了</Divider>}
          scrollableTarget="scrollableDiv"
        >
          <List
            itemLayout="horizontal"
            dataSource={data}
            split={false}
            loading={loading}
            header={
              <List.Item>
                <Row style={{ width: '100%' }} gutter={32}>
                  <Col span={4} className={Styles.listTitle}>
                    任务序号
                  </Col>
                  <Col span={9} className={Styles.listTitle}>
                    新增知识
                  </Col>
                  <Col span={9} className={Styles.listTitle}>
                    原有知识
                  </Col>
                  <Col span={2} className={Styles.listTitle}>
                    操作
                  </Col>
                </Row>
              </List.Item>
            }
            renderItem={(item, index) => (
              <List.Item>
                <Row style={{ width: '100%' }} gutter={32}>
                  <Col
                    span={4}
                    className={Styles.listContent}
                    style={{ fontSize: '30px', fontWeight: 'bold' }}
                  >
                    {index + 1}
                  </Col>
                  <Col span={9}>
                    <KnowledgeItem
                      data={{
                        id: item.new_knowledge_id,
                        content: item.new_knowledge,
                        metadata: {
                          tag: item.new_knowledge_tag,
                          user: item.new_knowledge_user,
                        },
                      }}
                    ></KnowledgeItem>
                  </Col>
                  <Col span={9}>
                    <KnowledgeItem
                      data={{
                        id: item.old_knowledge_id,
                        content: item.old_knowledge,
                        metadata: {
                          tag: item.old_knowledge_tag,
                          user: item.old_knowledge_user,
                        },
                      }}
                    ></KnowledgeItem>
                  </Col>
                  <Col span={2} className={Styles.listContent}>
                    {item.status === 'PENDING' && (
                      <>
                        <Button type="link" onClick={() => handleReview(item.id, 'ADD')}>
                          新增
                        </Button>
                        <Button type="link" onClick={() => handleReview(item.id, 'REPLACE')}>
                          替换
                        </Button>
                        <Button type="link">合并</Button>
                        <Button type="link" onClick={() => handleReview(item.id, 'NEGLECT')}>
                          放弃
                        </Button>
                      </>
                    )}
                    {item.status === 'PROCESSED' && (
                      <div className={Styles.processed}>
                        <CheckOutlined style={{ color: '#00B240', marginRight: '10px' }} />
                        已处理
                      </div>
                    )}
                  </Col>
                </Row>
              </List.Item>
            )}
          />
        </InfiniteScroll>
      </div>
    </div>
  );
};

export default App;
