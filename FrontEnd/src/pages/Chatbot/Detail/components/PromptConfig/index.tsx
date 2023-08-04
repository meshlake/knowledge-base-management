import { Button, Form, Input } from 'antd';
import React, { useEffect, useState } from 'react';
import styles from './index.less';

type Props = {
  data?: Chatbot_API.Chatbot;
  updateRequest: (id: string, data: Chatbot_API.ChatbotUpdate) => Promise<void>;
};

const promptFormItems = [
  {
    key: 'role',
    label: '角色',
    description: '输入你想要机器人扮演的角色，比如客服，助理，法律咨询等等',
  },
  {
    key: 'name',
    label: '称呼',
    description: '输入你机器人介绍时给到自己的称号，比如 小马老师，教练小王等等',
  },
  {
    key: 'work',
    label: '行动',
    description: '设定你想让机器人做的事情，比如分享财税知识，回答客户问题等等',
  },
  {
    key: 'style',
    label: '风格',
    description: '设定机器人回答问题的风格和语气，比如风趣、活泼、严肃、正式等等',
  },
];

const BaseInfo: React.FC<Props> = (props) => {
  const { data, updateRequest } = props;
  const [form] = Form.useForm();
  const [editable, setEditable] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleEdit = () => {
    setEditable(true);
  };

  const handleCancel = () => {
    setEditable(false);
    if (data?.prompt_config) {
      form.setFieldsValue(data.prompt_config);
    }
  };

  const handleSubmit = () => {
    if (!data) {
      return;
    }
    form
      .validateFields()
      .then((values) => {
        console.log(values);
        setLoading(true);
        updateRequest(data.id, { prompt_config: values }).finally(() => {
          setEditable(false);
          setLoading(false);
        });
      })
      .catch(() => {});
  };

  useEffect(() => {
    if (data?.prompt_config) {
      form.setFieldsValue(data.prompt_config);
    }
  }, [data]);

  return (
    <div className={styles.comContainer}>
      <div className={styles.header}>
        <div className={styles.title}>
          <span>提示词设定</span>
          <span className={styles.subTitle}>通过一些提示设定，让机器人更好的完成你的任务</span>
        </div>
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
        {promptFormItems.map((item) => (
          <>
            <Form.Item
              label={item.label}
              name={item.key}
              key={item.key}
              rules={[{ required: true, message: '请输入' }]}
            >
              <Input placeholder={editable ? item.description : ''} bordered={editable} />
            </Form.Item>
          </>
        ))}
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
