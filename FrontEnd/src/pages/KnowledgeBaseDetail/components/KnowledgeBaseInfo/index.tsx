import { Button, Form, Input } from 'antd';
import React, { useState } from 'react';
import Styles from './index.less';

type KnowledgeBaseInfoProps = {
  name: string;
  description: string;
};

const App: React.FC<KnowledgeBaseInfoProps> = (props) => {
  const { name, description } = props;
  const [editabled, setEditabled] = useState(false);
  const [form] = Form.useForm();

  const handleCancel = () => {
    form.resetFields();
    setEditabled(false);
  };

  return (
    <div className={Styles.knowledgeBaseInfo}>
      <div className={Styles.header}>
        <div>基础信息</div>
        {!editabled && (
          <Button type="text" style={{ color: '#3D73EC' }} onClick={() => setEditabled(true)}>
            编辑
          </Button>
        )}
      </div>
      {editabled ? (
        <div>
          <Form form={form} name="control-hooks" style={{ maxWidth: 600 }} colon={false}>
            <Form.Item name="name" label="名称" rules={[{ required: true }]}>
              <Input />
            </Form.Item>
            <Form.Item name="description" label="描述" rules={[{ required: true }]}>
              <Input />
            </Form.Item>
            <Form.Item>
              <Button htmlType="button" onClick={handleCancel}>
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                保存
              </Button>
            </Form.Item>
          </Form>
        </div>
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
