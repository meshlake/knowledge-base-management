import { Card, Tag, Typography } from 'antd';
import React from 'react';
import Styles from './index.less';

const { Paragraph } = Typography;

type KnowledgeItemProps = {
  data: {
    id: number;
    content: string;
    metadata: {
      tag: {
        id: number;
        name: string;
      };
      user: {
        id: number;
        nickname: string;
      };
      knowledgeBase: {
        id: number;
        name: string;
      };
      structure: 'NORMAL' | 'QA';
    };
  };
};

const App: React.FC<KnowledgeItemProps> = (props) => {
  const {
    data: { content, metadata },
  } = props;

  return (
    <Card className={Styles.knowledgeItem} bodyStyle={{ height: '100%', padding: '15px' }}>
      <div className={Styles.knowledgeItemContent}>
        <Paragraph ellipsis>知识库：{metadata.knowledgeBase.name}</Paragraph>
        {metadata.structure && metadata.structure === 'QA' ? (
          <div>
            <Paragraph ellipsis={{ rows: 2 }}>{`${JSON.parse(content).question}`}</Paragraph>
            <Paragraph ellipsis={{ rows: 3 }}>{`${JSON.parse(content).answer}`}</Paragraph>
          </div>
        ) : (
          <Paragraph ellipsis={{ rows: 5 }}>{content}</Paragraph>
        )}
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
