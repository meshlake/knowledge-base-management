import { Card, Tag, Typography } from 'antd';
import React, { MouseEvent } from 'react';
import Styles from './index.less';
import { DeleteOutlined } from '@ant-design/icons';
import { KnowledgeBaseTagModel } from '@/pages/KnowledgeBase/types';

const { Paragraph } = Typography;

type KnowledgeItemProps = {
  data: KNOWLEDGE_ITEM_API.KnowledgeItem;
  onDelete?: () => void;
  tags: KnowledgeBaseTagModel[];
};

const App: React.FC<KnowledgeItemProps> = (props) => {
  const {
    data: { content, metadata },
    onDelete,
    tags,
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
        {metadata.structure && metadata.structure === 'QA' ? (
          <div>
            <Paragraph ellipsis={{ rows: 2 }}>{`问题：${JSON.parse(content).question}`}</Paragraph>
            <Paragraph ellipsis={{ rows: 3 }}>{`答案：${JSON.parse(content).answer}`}</Paragraph>
          </div>
        ) : (
          <Paragraph ellipsis={{ rows: 5 }}>{content}</Paragraph>
        )}
        <div>
          <div className={Styles.uploader}>上传人：{metadata.user.nickname}</div>
          <div className={Styles.footer}>
            <div>来自：{fromDisplay}</div>
            {onDelete ? (
              <div>
                {metadata.tag && (
                  <Tag color="#D9F0FD" className={Styles.tags}>
                    {tags.find((item) => item.id === metadata.tag)?.name}
                  </Tag>
                )}
                <DeleteOutlined className={Styles.deleteBtn} onClick={handleDelete} />
              </div>
            ) : metadata?.tag ? (
              <div>
                <Tag color="#D9F0FD" className={Styles.normalTags}>
                  {tags.find((item) => item.id === metadata.tag)?.name}
                </Tag>
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </Card>
  );
};

export default App;
