import React, { useEffect, useState } from 'react';
import { Modal, Form, notification, Checkbox, Row, Col } from 'antd';
import { getAllPermissions, getRolePermissions, updateRolePermissions } from '@/services/auth/api';

type UserFormProps = {
  visible: boolean;
  onClose: () => void;
  role: string;
};

const UserForm = (props: UserFormProps) => {
  const { visible, onClose, role } = props;

  const [permissions, setPermissions] = useState<AUTH_API.Permission[]>([]); // 权限列表
  const [form] = Form.useForm();

  const getPermissions = async () => {
    const res = await getAllPermissions();
    setPermissions(res.data);
  };

  const handleGetRolePermissions = async () => {
    const res = await getRolePermissions(role);
    const permissions = res.data.map((permission: string[]) => {
      return `${permission[1]}.${permission[2]}.${permission[3]}`;
    });
    form.setFieldsValue({
      permissions,
    });
  };

  const handleAdd = async () => {
    try {
      const formData = await form.validateFields();
      const postPermissions = formData.permissions.map((permission: string) => {
        const [type, route, method] = permission.split('.');
        return {
          type,
          route,
          method,
        };
      });
      await updateRolePermissions(role, postPermissions);
      notification.success({
        message: '修改成功',
      });
      form.resetFields();
      onClose();
    } catch (error) {
      console.log('表单校验失败', error);
      notification.error({
        message: '修改失败',
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
    getPermissions();
    if (role) {
      handleGetRolePermissions();
    }
  }, [role]);

  return (
    <Modal
      title="授权"
      open={visible}
      onCancel={() => onClose()}
      onOk={handleSubmit}
      bodyStyle={{ maxHeight: '500px', overflow: 'scroll' }}
    >
      <Form form={form}>
        <Form.Item
          name="permissions"
          label="权限"
          rules={[{ required: true, message: '请选择权限' }]}
        >
          <Checkbox.Group>
            <Row>
              {permissions.map((permission) => (
                <Col span={24} key={permission.route + permission.method + permission.type}>
                  <Checkbox
                    key={`inner_${permission.route + permission.method + permission.type}`}
                    value={`${permission.type}.${permission.route}.${permission.method}`}
                  >{`${permission.type} ${permission.route} ${permission.method}`}</Checkbox>
                </Col>
              ))}
            </Row>
          </Checkbox.Group>
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default UserForm;
