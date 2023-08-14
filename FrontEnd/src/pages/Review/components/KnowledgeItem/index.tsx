import { Card, Tag } from 'antd';
import React from 'react';
import Styles from './index.less';
import { KnowledgeBaseTagModel } from '@/pages/KnowledgeBase/types';

type KnowledgeItemProps = {
  data: any;
  tags: KnowledgeBaseTagModel[];
};

const App: React.FC<KnowledgeItemProps> = (props) => {
  const {
    data: { content, metadata },
    tags,
  } = props;

  return (
    <Card
      hoverable
      className={Styles.knowledgeItem}
      bodyStyle={{ height: '100%', padding: '15px' }}
    >
      <div className={Styles.knowledgeItemContent}>
        <p>{content}</p>
        <div className={Styles.footer}>
          <div>上传者：{metadata.user.nickname}</div>
          {metadata.tag ? (
            <Tag color="#D9F0FD" className={Styles.normalTags}>
              {tags.find((item) => item.id === metadata.tag)?.name}
            </Tag>
          ) : null}
        </div>
      </div>
    </Card>
  );
};

export default App;
