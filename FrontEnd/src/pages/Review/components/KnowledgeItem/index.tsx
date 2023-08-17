import { Card, Tag, Typography } from 'antd';
import React from 'react';
import Styles from './index.less';

const { Paragraph } = Typography;

type KnowledgeItemProps = {
  data: any;
};

const App: React.FC<KnowledgeItemProps> = (props) => {
  const {
    data: { content, metadata },
  } = props;

  return (
    <Card
      hoverable
      className={Styles.knowledgeItem}
      bodyStyle={{ height: '100%', padding: '15px' }}
    >
      <div className={Styles.knowledgeItemContent}>
        <Paragraph ellipsis={{ rows: 5 }}>{content}</Paragraph>
        <div className={Styles.footer}>
          <div>上传者：{metadata.user.nickname}</div>
          {metadata.tag ? (
            <Tag color="#D9F0FD" className={Styles.normalTags}>
              {metadata.tag.name}
            </Tag>
          ) : null}
        </div>
      </div>
    </Card>
  );
};

export default App;
