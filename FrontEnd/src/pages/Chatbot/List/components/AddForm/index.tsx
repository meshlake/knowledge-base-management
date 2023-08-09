import React, { useEffect } from 'react';
import { Modal, Form, Input, notification } from 'antd';
import { createChatbot } from '@/services/chatbot';
import TrimInput from '@/components/TrimInput';

const { TextArea } = Input;

type OrgFormProps = {
  visible: boolean;
  refresh: (needRefresh: boolean) => void;
};

const OrgForm = (props: OrgFormProps) => {
  const { visible, refresh } = props;

  const [form] = Form.useForm();

  const handleAdd = async () => {
    form
      .validateFields()
      .then((formData) => {
        console.log(formData);
        createChatbot(formData)
          .then(() => {
            form.resetFields();
            refresh(true);
            notification.success({
              message: '创建成功',
            });
          })
          .catch(() => {
            notification.error({
              message: '创建失败',
            });
          });
      })
      .catch(() => {});
  };

  // 处理表单提交
  const handleSubmit = () => {
    handleAdd();
  };

  // 初始化数据
  useEffect(() => {
    form.resetFields();
  }, [visible]);

  return (
    <Modal
      title="创建机器人"
      width={640}
      bodyStyle={{ marginTop: '24px' }}
      open={visible}
      onCancel={() => refresh(false)}
      onOk={handleSubmit}
    >
      <Form form={form} layout="vertical" requiredMark={false}>
        <Form.Item name="name" label="机器人名称" rules={[{ required: true, message: '请输入' }]}>
          <TrimInput placeholder="请输入" maxLength={255} />
        </Form.Item>
        <Form.Item
          name="description"
          label="机器人描述"
          rules={[{ required: true, message: '请输入' }]}
        >
          <TextArea autoSize={{ minRows: 2, maxRows: 6 }} placeholder="请输入" maxLength={255} />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default OrgForm;
