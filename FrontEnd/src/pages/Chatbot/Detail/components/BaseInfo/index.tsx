import { Button, Form, Input } from 'antd';
import React, { useEffect, useState } from 'react';
import styles from './index.less';

type Props = {
  data?: Chatbot_API.Chatbot;
  updateRequest: (id: string, data: { name: string; description: string }) => Promise<void>;
};

const BaseInfo: React.FC<Props> = (props) => {
  const { data, updateRequest } = props;
  const [form] = Form.useForm();
  const [editable, setEditable] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleEdit = () => {
    setEditable(true);
  };

  const handleCancel = () => {
    form.setFieldsValue({
      name: data?.name,
      description: data?.description,
    });
    setEditable(false);
  };

  const handleSubmit = () => {
    if (!data) {
      return;
    }
    form
      .validateFields()
      .then((values) => {
        setLoading(true);
        updateRequest(data.id, values).finally(() => {
          setEditable(false);
          setLoading(false);
        });
      })
      .catch(() => {});
  };

  useEffect(() => {
    form.setFieldsValue({
      name: data?.name,
      description: data?.description,
    });
  }, [data]);

  return (
    <div className={styles.comContainer}>
      <div className={styles.header}>
        <div className={styles.title}>基础信息</div>
        {!editable && (
          <Button type="link" onClick={handleEdit}>
            编辑
          </Button>
        )}
      </div>
      <Form
        form={form}
        colon={false}
        autoComplete="off"
        requiredMark={false}
        labelCol={{ span: 2 }}
        labelAlign="left"
        className={editable ? styles.editableForm : styles.disabledForm}
      >
        <Form.Item label="名称" name="name" rules={[{ required: true, message: '请输入' }]}>
          <Input placeholder={editable ? '请输入' : ''} bordered={editable} />
        </Form.Item>
        <Form.Item label="描述" name="description" rules={[{ required: true, message: '请输入' }]}>
          <Input placeholder={editable ? '请输入' : ''} bordered={editable} />
        </Form.Item>
        {editable ? (
          <>
            <Form.Item style={{ textAlign: 'right', marginTop: 24 }}>
              <Button
                disabled={loading}
                onClick={handleCancel}
                style={{ marginLeft: 12, width: 120 }}
              >
                取消
              </Button>
              <Button
                loading={loading}
                onClick={handleSubmit}
                type="primary"
                style={{ marginLeft: 12, width: 120 }}
              >
                保存
              </Button>
            </Form.Item>
          </>
        ) : null}
      </Form>
    </div>
  );
};

export default BaseInfo;
