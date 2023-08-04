import React, { useEffect } from 'react';
import { useParams } from '@umijs/max';
import { Spin, notification } from 'antd';
import ComTabs from '@/components/Tabs';
import { getChatbot, updateChatbot } from '@/services/chatbot';
import BaseInfo from './components/BaseInfo';
import Configuration from './components/Configuration';
import styles from './index.less';

const App: React.FC = () => {
  const params = useParams();

  const tabs = ['模型配置', '基础信息'];
  const [activeTab, setActiveTab] = React.useState(0);
  const [loading, setLoading] = React.useState<boolean>(false);
  const [chatbot, setChatbot] = React.useState<Chatbot_API.Chatbot>();

  const handleTabChange = (index: number) => {
    setActiveTab(index);
  };

  const handleBack = () => {
    history.back();
  };

  const getChatbotDetail = async () => {
    if (!params.id) {
      return;
    }
    try {
      const data = await getChatbot(params.id);
      setChatbot(data);
    } catch (error) {
      console.log(error);
    }
  };

  const handleUpdate = async (id: string, data: Chatbot_API.ChatbotUpdate) => {
    try {
      const newDate = await updateChatbot(id, data);
      setChatbot(newDate);
      notification.success({
        message: '更新成功',
      });
    } catch (error) {
      notification.error({
        message: '更新失败',
      });
      console.log(error);
    }
  };

  useEffect(() => {
    setLoading(true);
    getChatbotDetail().finally(() => {
      setLoading(false);
    });
  }, []);

  return (
    <div className={styles.pageContainer}>
      <div className={styles.backBtn} onClick={handleBack}>
        <img src="/imgs/backArrow.png" alt="" className={styles.backIcon} />
        <div>返回</div>
      </div>
      <ComTabs items={tabs} onChange={handleTabChange} />
      <div className={styles.pageContent}>
        <Spin spinning={loading}>
          {activeTab === 0 && <Configuration data={chatbot} updateRequest={handleUpdate} />}
          {activeTab === 1 && <BaseInfo data={chatbot} updateRequest={handleUpdate} />}
        </Spin>
      </div>
    </div>
  );
};

export default App;
