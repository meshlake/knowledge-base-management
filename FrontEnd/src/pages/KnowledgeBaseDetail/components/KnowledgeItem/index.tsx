import { Card, Tag } from 'antd';
import React from 'react';
import Styles from './index.less';
import { DeleteOutlined } from '@ant-design/icons';

type KnowledgeItemProps = {
  data: any;
  onDelete: () => void;
};

const App: React.FC<KnowledgeItemProps> = (props) => {
  const {
    data: { source, tags, content },
    onDelete,
  } = props;

  return (
    <Card hoverable className={Styles.knowledgeItem}>
      <p>{content}</p>
      <div className={Styles.footer}>
        <div>来自：{source}</div>
        <div>
          <Tag color="#D9F0FD" className={Styles.tags}>
            {tags[0]}
          </Tag>
          <DeleteOutlined className={Styles.deleteBtn} onClick={() => onDelete()} />
        </div>
      </div>
    </Card>
  );
};

export default App;
