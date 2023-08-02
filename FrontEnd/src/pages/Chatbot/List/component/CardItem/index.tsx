import React, { useState } from 'react';
import styles from './index.less';
import { DeleteOutlined } from '@ant-design/icons';

const CardItem: React.FC<{ data: Chatbot_API.Chatbot; handleDelete: () => void }> = ({
  data,
  handleDelete,
}) => {
  const [active, setActive] = useState(false);

  console.log(active);
  return (
    <div
      className={styles.cardItem}
      onMouseEnter={() => {
        setActive(true);
      }}
      onMouseLeave={() => {
        setActive(false);
      }}
    >
      <div className={styles.cardItemTop}>
        <img className={styles.icon} src="/images/chatbot_icon.png" alt="" />
        <div className={styles.title}>{data.name}</div>
      </div>
      <div className={styles.description}>{data.description}</div>
      {active ? (
        <div className={styles.actions}>
          <DeleteOutlined style={{ fontSize: 20, color: '#F40909' }} onClick={handleDelete} />
        </div>
      ) : null}
    </div>
  );
};

export default CardItem;
