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
  const [form] = Form.useForm();

  const handleCancel = () => {
    form.resetFields();
    setEditabled(false);
  };

  const handleFillFrom = () => {
    setEditabled(true);
    form.setFieldsValue(knowledgeBase);
  };

  const handleUpdateKnowledgeBase = () => {
    form.validateFields().then((values: { name: string; description: string }) => {
      console.log(values);
      const { name, description } = values;
      updateKnowledgeBase({ id: knowledgeBase.id, name, description }).then(() => {
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
          <Form
            form={form}
            name="control-hooks"
            style={{ maxWidth: 600 }}
            colon={false}
            onFinish={handleUpdateKnowledgeBase}
          >
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
            <div>{knowledgeBase?.name}</div>
          </div>
          <div className={Styles.infoItem}>
            <div className={Styles.label}>描述</div>
            <div>{knowledgeBase?.description}</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
