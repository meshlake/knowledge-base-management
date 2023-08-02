import React, { useEffect } from 'react';
import { Modal, Form, Input, notification } from 'antd';
import { createKnowledgeBase } from '@/services/knowledgeBase';
import TrimInput from '@/components/TrimInput';
import { KnowledgeBaseModel } from '../../types';

const { TextArea } = Input;

type AddKnowledgeBaseItemFormProps = {
  visible: boolean;
  toggleVisible: (visible: boolean) => void;
  refetchItems: () => void;
};

const AddKnowledgeBaseItemForm = (props: AddKnowledgeBaseItemFormProps) => {
  const { visible, toggleVisible, refetchItems } = props;

  const [form] = Form.useForm();

  const handleAdd = async () => {
    form
      .validateFields()
      .then((formData) => {
        createKnowledgeBase(formData as KnowledgeBaseModel)
          .then(() => {
            refetchItems();
            form.resetFields();
            notification.success({ message: '添加成功' });
          })
          .catch(() => {
            notification.error({ message: '添加失败' });
          });
      })
      .catch(() => {});
  };

  // 初始化数据
  useEffect(() => {
    form.resetFields();
  }, [form]);

  return (
    <Modal
      title="创建知识库"
      width={640}
      bodyStyle={{ marginTop: '24px' }}
      open={visible}
      okText="保存"
      cancelText="取消"
      onCancel={() => toggleVisible(false)}
      onOk={() => handleAdd()}
    >
      <Form form={form} layout="vertical" requiredMark={false}>
        <Form.Item name="name" label="知识库名称" rules={[{ required: true, message: '请输入' }]}>
          <TrimInput placeholder="输入知识库名称" maxLength={50} />
        </Form.Item>
        <Form.Item
          name="description"
          label="知识库描述"
          rules={[{ required: true, message: '请输入' }]}
        >
          <TextArea rows={4} placeholder="输入知识库描述" maxLength={200} />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default AddKnowledgeBaseItemForm;
