import { Button } from 'antd';
import React, { useState } from 'react';
import Styles from './index.less';

type KnowledgeBaseInfoProps = {
  name: string;
  description: string;
};

const App: React.FC<KnowledgeBaseInfoProps> = (props) => {
  const { name, description } = props;
  const [editabled, setEditabled] = useState(false);

  return (
    <div className={Styles.knowledgeBaseInfo}>
      <div className={Styles.header}>
        <div>基础信息</div>
        <Button type="text" style={{ color: '#3D73EC' }} onClick={() => setEditabled(true)}>
          编辑
        </Button>
      </div>
      {editabled ? (
        <div></div>
      ) : (
        <div className={Styles.infoWrapper}>
          <div className={Styles.infoItem}>
            <div className={Styles.label}>名称</div>
            <div>{name}</div>
          </div>
          <div className={Styles.infoItem}>
            <div className={Styles.label}>描述</div>
            <div>{description}</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
