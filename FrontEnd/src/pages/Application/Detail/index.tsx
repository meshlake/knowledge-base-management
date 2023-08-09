import React, { useEffect } from 'react';
import { useParams } from '@umijs/max';
import { Spin, notification } from 'antd';
import { getApplication, updateApplication } from '@/services/application';
import BaseInfo from '@/pages/Chatbot/Detail/components/BaseInfo';
import ChatbotConfig from './components/ChatbotConfig';
import LoginInfo from './components/LoginInfo';
import ExtraConfig from './components/ExtraConfig';
import styles from './index.less';

const ApplicationDetail: React.FC = () => {
  const params = useParams();

  const [loading, setLoading] = React.useState<boolean>(false);
  const [application, setApplication] = React.useState<Application_API.Application>();

  const handleBack = () => {
    history.back();
  };

  const getApplicationDetail = async () => {
    if (!params.id) {
      return;
    }
    try {
      const data = await getApplication(params.id);
      setApplication(data);
    } catch (error) {
      console.log(error);
    }
  };

  const handleUpdate = async (id: string, data: Application_API.ApplicationUpdate) => {
    try {
      const newDate = await updateApplication(id, data);
      setApplication(newDate);
      notification.success({
        message: '更新成功',
      });
    } catch (error) {
      notification.error({
        message: '更新失败',
      });
      throw error;
    }
  };

  useEffect(() => {
    setLoading(true);
    getApplicationDetail().finally(() => {
      setLoading(false);
    });
  }, []);

  return (
    <div className={styles.pageContainer}>
      <div className={styles.backBtn} onClick={handleBack}>
        <img src="/imgs/backArrow.png" alt="" className={styles.backIcon} />
        <div>返回</div>
      </div>
      <div className={styles.pageTitle}>
        {application ? (application?.category === 'WX_PUBLIC' ? '公众号配置' : '企业微信配置') : ''}
      </div>
      <div className={styles.pageContent}>
        <Spin spinning={loading}>
          <BaseInfo data={application} updateRequest={handleUpdate} />
          <ChatbotConfig data={application} updateRequest={handleUpdate} />
          {application && application.category === 'WX_CHATBOT' ? (
            <>
              <LoginInfo data={application} />
              <ExtraConfig data={application} updateRequest={handleUpdate} />
            </>
          ) : null}
        </Spin>
      </div>
    </div>
  );
};

export default ApplicationDetail;
