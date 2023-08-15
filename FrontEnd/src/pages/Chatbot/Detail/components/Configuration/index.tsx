import React from 'react';
import { history } from '@umijs/max';
import PromptConfig from '../PromptConfig';
import KnowledgeConfig from '../KnowledgeConfig';
import styles from './index.less';
import { Button } from 'antd';

type Props = {
  data?: Chatbot_API.Chatbot;
  updateRequest: (id: string, data: Chatbot_API.ChatbotUpdate) => Promise<void>;
};

const Configuration: React.FC<Props> = (props) => {
  const { data, updateRequest } = props;

  return (
    <div className={styles.comContainer}>
      <div className={styles.title}>{data?.name}</div>
      <PromptConfig data={data} updateRequest={updateRequest} />
      <KnowledgeConfig data={data} updateRequest={updateRequest} />
      {data?.knowledge_bases?.length ? (
        <>
          <div className={styles.buttonContainer}>
            <Button
              type="primary"
              onClick={() => {
                history.push(`/chat?botId=${data?.id}`);
              }}
              style={{ padding: '0 32px' }}
            >
              对话调试
            </Button>
          </div>
        </>
      ) : null}
    </div>
  );
};

export default Configuration;
