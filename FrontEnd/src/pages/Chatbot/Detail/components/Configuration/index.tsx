import React from 'react';
import PromptConfig from '../PromptConfig';
import styles from './index.less';

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

      {/* <PromptList /> */}
    </div>
  );
};

export default Configuration;
