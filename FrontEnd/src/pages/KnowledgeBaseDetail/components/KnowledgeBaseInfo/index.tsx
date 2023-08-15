import { Button, Form, Input, notification } from 'antd';
import React, { useState } from 'react';
import Styles from './index.less';
import { updateKnowledgeBase } from '@/services/knowledgeBase';
import { KnowledgeBaseModel } from '@/pages/KnowledgeBase/types';

type KnowledgeBaseInfoProps = {
  knowledgeBase: KnowledgeBaseModel;
};

const App: React.FC<KnowledgeBaseInfoProps> = (props) => {
  const { knowledgeBase } = props;
  const [editabled, setEditabled] = useState(false);
  const [info, setInfo] = useState<{ name: string; description: string }>({
    name: knowledgeBase.name,
    description: knowledgeBase.description,
  });
  const [form] = Form.useForm();

  const handleCancel = () => {
    form.resetFields();
    setEditabled(false);
  };

  const handleFillFrom = () => {
    setEditabled(true);
    form.setFieldsValue(info);
  };

  const handleUpdateKnowledgeBase = () => {
    form.validateFields().then((values: { name: string; description: string }) => {
      const { name, description } = values;
      updateKnowledgeBase({ id: knowledgeBase.id, name, description }).then((data) => {
        const { name, description } = data.data;
        setInfo({ name, description });
        setEditabled(false);
        notification.success({
          message: '更新成功',
        });
      });
    });
  };

  return (
    <div className={Styles.knowledgeBaseInfo}>
      <div className={Styles.header}>
        <div>基础信息</div>
        {!editabled && (
          <Button type="text" style={{ color: '#3D73EC' }} onClick={handleFillFrom}>
            编辑
          </Button>
        )}
      </div>
      {editabled ? (
        <div>
          <Form form={form} colon={false} onFinish={handleUpdateKnowledgeBase}>
            <Form.Item name="name" label="名称" rules={[{ required: true }]}>
              <Input />
            </Form.Item>
            <Form.Item name="description" label="描述" rules={[{ required: true }]}>
              <Input />
            </Form.Item>
            <Form.Item style={{ display: 'flex', flexDirection: 'row-reverse' }}>
              <Button
                htmlType="button"
                onClick={handleCancel}
                style={{ width: '140px', marginRight: '20px' }}
              >
                取消
              </Button>
              <Button type="primary" htmlType="submit" style={{ width: '140px' }}>
                保存
              </Button>
            </Form.Item>
          </Form>
        </div>
      ) : (
        <div className={Styles.infoWrapper}>
          <div className={Styles.infoItem}>
            <div className={Styles.label}>名称</div>
            <div>{info.name}</div>
          </div>
          <div className={Styles.infoItem}>
            <div className={Styles.label}>描述</div>
            <div>{info.description}</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
