import { Modal, Tag, Typography } from 'antd';
import React from 'react';
import Styles from './index.less';

const { Paragraph } = Typography;

type ReviewKnowledgeItemProps = {
  isModalOpen: boolean;
  onClose: (isNeedRefresh: boolean) => void;
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

const App: React.FC<ReviewKnowledgeItemProps> = (props) => {
  const { isModalOpen, onClose, data } = props;

  return (
    <Modal
      title="知识点详情"
      open={isModalOpen}
      className={Styles.manuallyEnterModal}
      width={800}
      maskClosable={false}
      bodyStyle={{
        padding: '48px 8px',
        paddingBottom: '30px',
      }}
      footer={[]}
      onCancel={() => onClose(false)}
    >
      <Paragraph ellipsis>知识库：{data?.metadata?.knowledgeBase.name}</Paragraph>
      {data?.metadata?.structure && data?.metadata?.structure === 'QA' ? (
        <div>
          <Paragraph ellipsis={{ rows: 2 }}>{`${JSON.parse(data?.content).question}`}</Paragraph>
          <Paragraph ellipsis={{ rows: 3 }}>{`${JSON.parse(data?.content).answer}`}</Paragraph>
        </div>
      ) : (
        <Paragraph ellipsis={{ rows: 5 }}>{data?.content}</Paragraph>
      )}
      <div className={Styles.footer}>
        <div>上传者：{data?.metadata?.user.nickname}</div>
        {data?.metadata?.tag ? (
          <Tag color="#D9F0FD" className={Styles.normalTags}>
            {data?.metadata?.tag.name}
          </Tag>
        ) : null}
      </div>
    </Modal>
  );
};

export default App;
