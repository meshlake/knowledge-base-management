import React, { useEffect } from 'react';
import { useParams } from '@umijs/max';
import { Spin, notification } from 'antd';
import { getApplication, updateApplication } from '@/services/application';
import styles from './index.less';

const ApplicationDetail: React.FC = () => {
  const params = useParams();

  const [loading, setLoading] = React.useState<boolean>(false);
  const [application, setApplication] = React.useState<Application_API.Application>();

  const handleBack = () => {
    history.back();
  };

  const getChatbotDetail = async () => {
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

  console.log(application, handleUpdate);

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
      <div className={styles.pageContent}>
        <Spin spinning={loading}></Spin>
      </div>
    </div>
  );
};

export default ApplicationDetail;
