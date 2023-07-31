import React, { useState, useEffect } from 'react';
import { Modal, Form, Input, Select, notification, Switch } from 'antd';
import { getAllRoles } from '@/services/role/api';
import { getAllOrganizations } from '@/services/organization/api';
import { updateUser } from '@/services/userManage/api';

type UserFormProps = {
  visible: boolean;
  data: USER_MANAGE_API.User;
  refresh: (needRefresh: boolean) => void;
};

const UserForm = (props: UserFormProps) => {
  const { visible, data, refresh } = props;

  const [form] = Form.useForm();
  const [roles, setRoles] = useState<ROLE_API.Role[]>([]);
  const [organizations, setOrganizations] = useState<ORGANIZATION_API.Organization[]>([]);

  const handleEdit = async () => {
    try {
      const formData = await form.validateFields();
      await updateUser({
        ...formData,
        disabled: !formData.disabled,
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

  const getRoles = async () => {
    const res = await getAllRoles();
    setRoles(res.data);
  };

  const getOrganizations = async () => {
    const res = await getAllOrganizations();
    setOrganizations(res.data);
  };

  // 初始化数据
  useEffect(() => {
    getRoles();
    getOrganizations();
    if (data && data.id) {
      form.setFieldsValue({
        ...data,
        role_id: data.role?.id,
        organization_id: data.organization?.id,
        disabled: !data.disabled,
      });
    } else {
      form.resetFields();
    }
  }, [data]);

  return (
    <Modal title="编辑账号" open={visible} onCancel={() => refresh(false)} onOk={handleSubmit}>
      <Form form={form}>
        <Form.Item name="nickname" label="昵称" rules={[{ required: true, message: '请输入名称' }]}>
          <Input />
        </Form.Item>
        <Form.Item name="role_id" label="角色" rules={[{ required: true, message: '请选择角色' }]}>
          <Select>
            {roles.map((item) => {
              return (
                <Select.Option key={item.id} value={item.id}>
                  {item.name}
                </Select.Option>
              );
            })}
          </Select>
        </Form.Item>
        <Form.Item
          name="organization_id"
          label="组织"
          rules={[{ required: true, message: '请选择组织' }]}
        >
          <Select>
            {organizations.map((item) => {
              return (
                <Select.Option key={item.id} value={item.id}>
                  {item.name}
                </Select.Option>
              );
            })}
          </Select>
        </Form.Item>
        <Form.Item
          name="disabled"
          label="状态"
          valuePropName="checked"
          rules={[{ required: true, message: '请选择状态' }]}
        >
          <Switch checkedChildren="启用" unCheckedChildren="停用" />
        </Form.Item>
        <Form.Item name="email" label="邮箱" rules={[{ required: false, message: '请输入邮箱' }]}>
          <Input />
        </Form.Item>
        <Form.Item
          name="phone_number"
          label="手机号"
          rules={[{ required: false, message: '请输入手机号' }]}
        >
          <Input />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default UserForm;
