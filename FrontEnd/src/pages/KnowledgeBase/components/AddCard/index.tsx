import React from 'react';
import styles from '../../../Chatbot/List/component/AddCard/index.less';

const AddKnowledgeBaseItemCard: React.FC = () => {
  return (
    <div className={styles.cardItem}>
      <div className={styles.cardItemTop}>
        <img className={styles.icon} src="/images/add_icon.png" alt="" />
        <div className={styles.title}>创建知识库</div>
      </div>
      <div className={styles.description}>
        基于业务需要创建知识库，导入对应知识点，用于训练AI机器人。
      </div>
    </div>
  );
};

export default AddKnowledgeBaseItemCard;
