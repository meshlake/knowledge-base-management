import { Card, Tag } from 'antd';
import React, { MouseEvent } from 'react';
import Styles from './index.less';
import { DeleteOutlined } from '@ant-design/icons';

type KnowledgeItemProps = {
  data: KNOWLEDGE_ITEM_API.KnowledgeItem;
  onDelete?: () => void;
};

const App: React.FC<KnowledgeItemProps> = (props) => {
  const {
    data: { content, metadata },
    onDelete,
  } = props;

  const fromDisplay = metadata.type === 'MANUALLY' ? '手动录入' : metadata.source;

  const handleDelete = (e: MouseEvent<HTMLSpanElement>) => {
    e.stopPropagation();
    if (onDelete) {
      onDelete();
    }
  };

  return (
    <Card
      hoverable
      className={Styles.knowledgeItem}
      bodyStyle={{ height: '100%', padding: '15px' }}
    >
      <div className={Styles.knowledgeItemContent}>
        <p>{content}</p>
        <div className={Styles.footer}>
          <div>来自：{fromDisplay}</div>
          {onDelete ? (
            <div>
              {metadata.tags && (
                <Tag color="#D9F0FD" className={Styles.tags}>
                  {metadata.tags[0]}
                </Tag>
              )}
              <DeleteOutlined className={Styles.deleteBtn} onClick={handleDelete} />
            </div>
          ) : (
            metadata.tags && (
              <Tag color="#D9F0FD" className={Styles.normalTags}>
                {metadata.tags[0]}
              </Tag>
            )
          )}
        </div>
      </div>
    </Card>
  );
};

export default App;
