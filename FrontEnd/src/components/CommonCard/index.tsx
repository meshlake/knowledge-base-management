import React, { useState } from 'react';
import styles from './index.less';
import { DeleteOutlined } from '@ant-design/icons';

type CommonData = {
  id: string;
  name: string;
  description: string;
  icon?: string;
};

type ComProps = {
  data: CommonData;
  icon?: string;
  iconSize?: number;
  iconBorderRadius?: number;
  deleteable?: boolean;
  handleDelete?: () => void;
};

const Card: React.FC<ComProps> = ({
  data,
  deleteable,
  icon,
  iconBorderRadius,
  iconSize,
  handleDelete,
}) => {
  const [active, setActive] = useState(false);

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
        {data.icon || icon ? (
          <img
            className={styles.icon}
            src={data.icon || icon}
            style={{ borderRadius: iconBorderRadius, width: iconSize ? iconSize : undefined }}
          />
        ) : null}
        <div className={styles.title}>{data.name}</div>
      </div>
      <div className={styles.description}>{data.description}</div>
      {active && deleteable ? (
        <div className={styles.actions}>
          <DeleteOutlined
            style={{ fontSize: 20, color: '#F40909' }}
            onClick={(e) => {
              e.stopPropagation();
              handleDelete?.();
            }}
          />
        </div>
      ) : null}
    </div>
  );
};

export default Card;
