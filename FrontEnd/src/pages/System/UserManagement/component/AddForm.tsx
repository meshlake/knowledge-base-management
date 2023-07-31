import React, { useState, useEffect } from 'react';
import { Modal, Form, Input, Select, notification } from 'antd';
import { getAllRoles } from '@/services/role/api';
import { getAllOrganizations } from '@/services/organization/api';
import { createUser } from '@/services/userManage/api';

type UserFormProps = {
  visible: boolean;
  refresh: (needRefresh: boolean) => void;
};

const UserForm = (props: UserFormProps) => {
  const { visible, refresh } = props;

  const [form] = Form.useForm();
  const [roles, setRoles] = useState<ROLE_API.Role[]>([]);
  const [organizations, setOrganizations] = useState<ORGANIZATION_API.Organization[]>([]);

  const handleAdd = async () => {
    try {
      const formData = await form.validateFields();
      await createUser(formData);
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
    form.resetFields();
  }, []);

  return (
    <Modal title="新增账号" open={visible} onCancel={() => refresh(false)} onOk={handleSubmit}>
      <Form form={form}>
        <Form.Item
          name="username"
          label="用户名"
          rules={[{ required: true, message: '请输入用户名' }]}
        >
          <Input />
        </Form.Item>
        <Form.Item name="nickname" label="昵称" rules={[{ required: true, message: '请输入名称' }]}>
          <Input />
        </Form.Item>
        <Form.Item name="password" label="密码" rules={[{ required: true, message: '请输入名称' }]}>
          <Input type="password" />
        </Form.Item>
        <Form.Item
          name="repeatPassword"
          label="重复密码"
          rules={[{ required: true, message: '请输入名称' }]}
        >
          <Input type="password" />
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
        <Form.Item name="email" label="邮箱" rules={[{ required: false, message: '请输入名称' }]}>
          <Input />
        </Form.Item>
        <Form.Item
          name="phone_number"
          label="手机号"
          rules={[{ required: false, message: '请输入名称' }]}
        >
          <Input />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default UserForm;
