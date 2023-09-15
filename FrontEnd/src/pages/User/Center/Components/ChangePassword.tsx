import { Form, Input, Modal } from 'antd';
import React, { useState } from 'react';
//request
import { updatePassword } from '@/services/users/api';
import { history } from '@umijs/max';

type ChangePasswordFormProps = {
  visible: boolean;
  closeModal: () => void;
};

const ChangePasswordForm: React.FC<ChangePasswordFormProps> = (props) => {
  const { visible, closeModal } = props;
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  function isValidPassword(password: string) {
    // 校验密码长度
    if (password.length < 8 || password.length > 20) {
      return false;
    }
    // 校验密码是否包含数字和字母
    if (!/[0-9]/.test(password) || !/[a-zA-Z]/.test(password)) {
      return false;
    }
    return true;
  }

  const handleOk = () => {
    form.validateFields().then((values) => {
      setLoading(true);
      const params = {
        oldPassword: values.oldPassword,
        newPassword: values.newPassword,
      };
      updatePassword(params)
        .then(() => {
          closeModal();
          history.push('/user/login');
        })
        .catch((err) => {
          console.log(err);
        })
        .finally(() => {
          setLoading(false);
        });
    });
  };

  return (
    <Modal
      title="修改密码"
      open={visible}
      onOk={handleOk}
      onCancel={closeModal}
      width={480}
      okButtonProps={{ loading }}
    >
      <div style={{ marginBottom: '24px' }}>修改密码</div>
      <Form form={form} name="dynamic_form_nest_item" autoComplete="off" colon={false}>
        <Form.Item label="旧密码" name="oldPassword" validateFirst>
          <Input.Password placeholder="请输入" />
        </Form.Item>
        <Form.Item
          label="新密码"
          name="newPassword"
          validateFirst
          rules={[
            { required: true, message: '请输入8-20位，至少包含数字和字母的新密码' },
            {
              validator: (rules, value, callback) => {
                const loginpass = form.getFieldValue('repeatPassword');
                if (loginpass && loginpass !== value) {
                  callback('两次密码不一致');
                } else {
                  callback();
                }
              },
            },
            {
              validator(rule, value, callback) {
                if (!isValidPassword(value)) {
                  callback('密码格式不正确');
                }
                callback();
              },
            },
          ]}
        >
          <Input.Password placeholder="请输入8-20位，至少包含数字和字母的新密码" />
        </Form.Item>
        <Form.Item
          label="确认密码"
          name="repeatPassword"
          validateFirst
          rules={[
            { required: true, message: '请重复输入新密码' },
            {
              validator: (rules, value, callback) => {
                const loginpass = form.getFieldValue('newPassword');
                if (loginpass && loginpass !== value) {
                  callback('两次密码不一致');
                } else {
                  callback();
                }
              },
            },
            {
              validator(rule, value, callback) {
                if (!isValidPassword(value)) {
                  callback('密码格式不正确');
                }
                callback();
              },
            },
          ]}
        >
          <Input.Password placeholder="请重复输入新密码" />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default ChangePasswordForm;
