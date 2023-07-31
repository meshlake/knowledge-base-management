import React, { useEffect } from 'react';
import { Modal, Form, Input, notification } from 'antd';
import { createRole } from '@/services/role/api';

type UserFormProps = {
  visible: boolean;
  refresh: (needRefresh: boolean) => void;
};

const UserForm = (props: UserFormProps) => {
  const { visible, refresh } = props;

  const [form] = Form.useForm();

  const handleAdd = async () => {
    try {
      const formData = await form.validateFields();
      await createRole(formData);
      notification.success({
        message: '添加成功',
      });
      form.resetFields();
      refresh(true);
    } catch (error) {
      console.log('表单校验失败', error);
      notification.error({
        message: '添加失败',
      });
    }
  };

  // 处理表单提交
  const handleSubmit = async () => {
    handleAdd();
  };

  // 初始化数据
  useEffect(() => {
    form.resetFields();
  }, []);

  return (
    <Modal title="新增角色" open={visible} onCancel={() => refresh(false)} onOk={handleSubmit}>
      <Form form={form}>
        <Form.Item name="name" label="名称" rules={[{ required: true, message: '请输入名称' }]}>
          <Input />
        </Form.Item>
        <Form.Item name="code" label="编码" rules={[{ required: true, message: '请输入编码' }]}>
          <Input />
        </Form.Item>
        <Form.Item
          name="description"
          label="描述"
          rules={[{ required: false, message: '请输入描述' }]}
        >
          <Input />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default UserForm;
