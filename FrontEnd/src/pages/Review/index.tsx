import { Col, Divider, List, Row, Spin } from 'antd';
import React, { useEffect, useState } from 'react';
import Styles from './index.less';
import InfiniteScroll from 'react-infinite-scroll-component';
import KnowledgeItem from './components/KnowledgeItem';

const App: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<any[]>([]);

  const loadMoreData = () => {
    if (loading) {
      return;
    }
    setLoading(true);
    fetch('https://randomuser.me/api/?results=10&inc=name,gender,email,nat,picture&noinfo')
      .then((res) => res.json())
      .then((body) => {
        setData([...data, ...body.results]);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    loadMoreData();
  }, []);

  return (
    <div className={Styles.review}>
      <div className={Styles.title}>相似知识审核</div>
      <div className={Styles.description}>发现2条新增知识与原有知识相似</div>
      <div className={Styles.content}>
        <InfiniteScroll
          dataLength={data.length}
          next={loadMoreData}
          hasMore={data.length < 50}
          loader={<Spin spinning />}
          endMessage={<Divider plain>没有更多</Divider>}
          scrollableTarget="scrollableDiv"
        >
          <List
            itemLayout="horizontal"
            dataSource={data}
            split={false}
            header={
              <List.Item>
                <Row style={{ width: '100%' }} gutter={32}>
                  <Col span={4}>任务序号</Col>
                  <Col span={9}>新增知识</Col>
                  <Col span={9}>原有知识</Col>
                  <Col span={2}>操作</Col>
                </Row>
              </List.Item>
            }
            renderItem={() => (
              <List.Item>
                <Row style={{ width: '100%' }} gutter={32}>
                  <Col span={4}>1</Col>
                  <Col span={9}>
                    <KnowledgeItem data={{ id: 1, content: '1', metadata: {} }}></KnowledgeItem>
                  </Col>
                  <Col span={9}>
                    <KnowledgeItem data={{ id: 1, content: '1', metadata: {} }}></KnowledgeItem>
                  </Col>
                  <Col span={2}>
                    {' '}
                    <div>忽略</div>
                    <div>替换</div>
                    <div>合并</div>
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
