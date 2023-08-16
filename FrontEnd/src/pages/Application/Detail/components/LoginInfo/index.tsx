import React, { useEffect, useState } from 'react';
import { Avatar, Button, QRCode, Modal, notification, Badge } from 'antd';
import { ExclamationCircleOutlined } from '@ant-design/icons';
import { getWechatBotInfo, wechatBotLogout } from '@/services/application';
import styles from './index.less';

type Props = {
  data?: Application_API.Application;
};

let timer: any = null;

const LoginInfo: React.FC<Props> = ({ data }) => {
  const [loginInfo, setLoginInfo] = useState<Application_API.ApplicationLoginInfo>();

  const getBotStatus = async () => {
    if (!data) {
      return;
    }
    try {
      const response = await getWechatBotInfo(data.id);
      clearTimeout(timer);
      if (response.code === 200) {
        setLoginInfo(response.data);
        if (response.data.qrcode) {
          timer = setTimeout(getBotStatus, 3 * 1000);
        } else {
          timer = setTimeout(getBotStatus, 30 * 1000);
        }
      } else {
        setLoginInfo(undefined);
        timer = setTimeout(getBotStatus, 30 * 1000);
      }
    } catch (error) {}
  };

  const handleLogout = async () => {
    Modal.confirm({
      title: '确定要退出登录吗？',
      icon: <ExclamationCircleOutlined />,
      content: '退出登录当前账号，机器人将暂停工作',
      onOk: () => {
        if (!data) {
          return;
        }
        return wechatBotLogout(data.id).then((res) => {
          if (res.code === 200) {
            return new Promise((resolve) => {
              setTimeout(() => {
                notification.success({
                  message: '退出登录成功',
                  description: '',
                });
                getBotStatus();
                resolve(0);
              }, 3 * 1000);
            });
          }
        });
      },
      onCancel: () => {},
    });
  };

  useEffect(() => {
    if (data?.login_info) {
      setLoginInfo(data.login_info);
    }
    getBotStatus();
    return () => {
      // eslint-disable-next-line @typescript-eslint/no-unused-expressions
      timer && clearTimeout(timer);
    };
  }, [data]);

  return (
    <>
      <div className={styles.comContainer}>
        <div className={styles.header}>
          <div className={styles.title}>运行状态</div>
        </div>
        <div className={styles.content}>
          {data && !loginInfo ? (
            <Badge status="error" text="异常" />
          ) : loginInfo?.qrcode ? (
            <Badge status="warning" text="未登录" />
          ) : (
            <Badge status="processing" text="运行中" />
          )}
        </div>
      </div>
      <div className={styles.comContainer}>
        <div className={styles.header}>
          <div className={styles.title}>企业微信绑定</div>
        </div>
        <div className={styles.content}>
          {loginInfo?.qrcode ? (
            <div className={styles.qrcode}>
              <QRCode value={loginInfo?.qrcode} bordered={false} size={180} />
              <div className={styles.qrcodeDes}>请使用企业微信扫码登录</div>
            </div>
          ) : null}
          {loginInfo?.avatar ? (
            <div className={styles.userInfo}>
              <Avatar size={64} src={'data:image/png;base64,' + loginInfo?.avatar} />
              <span style={{ margin: '0 18px' }}>{loginInfo?.name}</span>
              <Button ghost type="primary" onClick={handleLogout}>
                退出登录
              </Button>
            </div>
          ) : null}
        </div>
      </div>
    </>
  );
};

export default LoginInfo;
