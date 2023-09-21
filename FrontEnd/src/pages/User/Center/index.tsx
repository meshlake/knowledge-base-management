import React, { useEffect, useState } from 'react';
import styles from './index.less';
import { Button } from 'antd';
import ChangePassword from './Components/ChangePassword';
import classNames from 'classnames';
import { useModel } from '@umijs/max';

const MyAccount: React.FC = () => {
  const [visible, setVisible] = useState(false);
  const { initialState } = useModel('@@initialState');

  useEffect(() => {}, []);

  return (
    <div>
      <div className={styles.title}>个人中心</div>
      <div className={styles.content}>
        <div className={classNames(styles.item, styles.avatarSection)}>
          <img
            src={initialState?.currentUser?.avatar || '/default-avatar.png'}
            className={styles.avatar}
          />
          <div>
            <div className={styles.nameBox}>
              <div className={styles.name}>{initialState?.currentUser?.nickname}</div>
            </div>
            <div className={styles.role}>{initialState?.currentUser?.role?.name}</div>
          </div>
        </div>
        <div className={classNames(styles.item, styles.defaultSection)}>
          <div className={styles.sectionTitle}>账号安全</div>
          <div className={styles.sectionContent}>
            <div className={styles.contentTitle}>密码</div>
            <Button
              type="link"
              onClick={() => {
                setVisible(true);
              }}
              className={styles.contentBtn}
            >
              修改密码
            </Button>
          </div>
        </div>
      </div>
      <ChangePassword visible={visible} closeModal={() => setVisible(false)}></ChangePassword>
    </div>
  );
};

export default MyAccount;
