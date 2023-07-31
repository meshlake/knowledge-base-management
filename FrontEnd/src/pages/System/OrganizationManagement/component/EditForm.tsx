import React, { useEffect } from 'react';
import { Modal, Form, Input, notification } from 'antd';
import { updateOrganization } from '@/services/organization/api';

type OrgFormProps = {
  visible: boolean;
  data: ORGANIZATION_API.Organization;
  refresh: (needRefresh: boolean) => void;
};

const OrgForm = (props: OrgFormProps) => {
  const { visible, data, refresh } = props;

  const [form] = Form.useForm();

  const handleEdit = async () => {
    try {
      const formData = await form.validateFields();
      await updateOrganization({
        ...formData,
        id: data.id,
      });
      notification.success({
        message: '编辑成功',
      });
      form.resetFields();
      refresh(true);
    } catch (error) {
      console.log('表单校验失败', error);
      notification.error({
        message: '编辑失败',
      });
    }
  };

  // 处理表单提交
  const handleSubmit = async () => {
    if (data && data.id) {
      // 编辑
      handleEdit();
    }
  };

  // 初始化数据
  useEffect(() => {
    if (data && data.id) {
      form.setFieldsValue({
        ...data,
      });
    } else {
      form.resetFields();
    }
  }, [data]);

  return (
    <Modal title="编辑组织" open={visible} onCancel={() => refresh(false)} onOk={handleSubmit}>
      <Form form={form}>
        <Form.Item name="name" label="组织名称" rules={[{ required: true, message: '请输入名称' }]}>
          <Input />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default OrgForm;
