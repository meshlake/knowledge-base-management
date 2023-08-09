import { Card, Tag } from 'antd';
import React from 'react';
import Styles from './index.less';

type KnowledgeItemProps = {
  data: any;
};

const App: React.FC<KnowledgeItemProps> = (props) => {
  const {
    data: { content, metadata },
  } = props;

  const fromDisplay = metadata.type === 'MANUALLY' ? '手动录入' : metadata.source;

  return (
    <Card
      hoverable
      className={Styles.knowledgeItem}
      bodyStyle={{ height: '100%', padding: '15px' }}
    >
      <div className={Styles.knowledgeItemContent}>
        <p>{content}</p>
        <div className={Styles.footer}>
          <div>上传者：{fromDisplay}</div>
          {metadata.tags?.length && metadata.tags?.length > 0 ? (
            <Tag color="#D9F0FD" className={Styles.normalTags}>
              {metadata.tags[0]}
            </Tag>
          ) : null}
        </div>
      </div>
    </Card>
  );
};

export default App;
