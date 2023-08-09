import React from 'react';
import styles from './index.less';

const AddCard: React.FC = () => {
  return (
    <div className={styles.cardItem}>
      <div className={styles.cardItemTop}>
        <img className={styles.icon} src="/images/add_icon.png" alt="" />
        <div className={styles.title}>添加机器人</div>
      </div>
      <div className={styles.description}>
        基于业务需要创建机器人，选择对应知识库，进行训练与调试。
      </div>
    </div>
  );
};

export default AddCard;
