import React, { MouseEvent, useState } from 'react';
import styles from '../../../Chatbot/List/components/CardItem/index.less';
import { DeleteOutlined } from '@ant-design/icons';
import { KnowledgeBaseModel } from '../../types';

export default function KnowledgeBaseItem({
  data,
  onItemDelete,
}: {
  data: KnowledgeBaseModel;
  onItemDelete: () => void;
}) {
  const [active, setActive] = useState(false);
  const onDelete = (e: MouseEvent<HTMLSpanElement>) => {
    e.stopPropagation();
    e.preventDefault();
    onItemDelete();
  };
  return (
    <div
      style={{ width: '100%' }}
      onMouseOver={() => {
        setActive(true);
      }}
      onMouseLeave={() => {
        setActive(false);
      }}
      className={styles.cardItem}
    >
      <div className={styles.cardItemTop}>
        <div className={styles.title}>{data.name}</div>
      </div>
      <div className={styles.description}>{data.description}</div>
      {active ? (
        <div onClick={onDelete} className={styles.actions}>
          <DeleteOutlined style={{ fontSize: 20, color: '#F40909' }} />
        </div>
      ) : null}
    </div>
  );
}
