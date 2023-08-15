import { Button, Form, Select } from 'antd';
import React, { useEffect, useState } from 'react';
import { getChatbotList } from '@/services/chatbot';
import { history } from '@umijs/max';
import { OptionProps } from 'antd/es/select';
import styles from './index.less';

type Props = {
  data?: Application_API.Application;
  updateRequest: (id: string, data: Application_API.ApplicationUpdate) => Promise<void>;
};

const ChatbotConfig: React.FC<Props> = (props) => {
  const { data, updateRequest } = props;
  const [form] = Form.useForm();
  const [editable, setEditable] = useState(false);
  const [loading, setLoading] = useState(false);
  const [chatbotList, setChatbotList] = useState<OptionProps[]>([]);

  const getList = async () => {
    try {
      const data = await getChatbotList();
      const list = data
        .map((item) => {
          return {
            value: item.id,
            label: item.name,
            disabled: item.knowledge_bases.length === 0,
            children: [],
          };
        })
        .sort((a, b) => (a.disabled ? 1 : 0) - (b.disabled ? 1 : 0));
      setChatbotList(list);
    } catch (e) {
      console.log(e);
    }
  };

  const resetForm = () => {
    if (data?.chatbot) {
      form.setFieldsValue({ chatbot_id: data.chatbot.id });
    } else {
      form.setFieldsValue({ chatbot_id: undefined });
    }
  };

  const handleEdit = () => {
    setEditable(true);
    getList().then(() => {
      resetForm();
    });
  };

  const handleCancel = () => {
    setEditable(false);
    resetForm();
  };

  const handleSubmit = () => {
    if (!data) {
      return;
    }
    form
      .validateFields()
      .then((values) => {
        setLoading(true);
        updateRequest(data.id, values)
          .then(() => {
            setEditable(false);
          })
          .finally(() => {
            setLoading(false);
          });
      })
      .catch(() => {});
  };

  useEffect(() => {
    if (data && !data.chatbot) {
      handleEdit();
    }
    resetForm();
  }, [data]);

  useEffect(() => {
    getList();
  }, []);

  const editForm = (
    <>
      <Form
        form={form}
        colon={false}
        autoComplete="off"
        requiredMark={false}
        labelAlign="left"
        labelCol={{ span: 5 }}
        style={{ maxWidth: '72%' }}
      >
        <Form.Item
          label="请选择绑定的机器人"
          name="chatbot_id"
          rules={[{ required: true, message: '请选择' }]}
        >
          <Select options={chatbotList} placeholder="请选择"></Select>
        </Form.Item>
      </Form>
      <div className={styles.formBottom}>
        <Button disabled={loading} onClick={handleCancel} style={{ marginLeft: 12, width: 120 }}>
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
      </div>
    </>
  );

  const chatbotCard = (
    <>
      <div className={styles.cardList}>
        <div
          className={styles.cardListItem}
          onClick={() => history.push(`/chatbot/${data?.chatbot?.id}`)}
        >
          <div className={styles.cardListItemTitle}>{data?.chatbot?.name}</div>
          <div className={styles.cardListItemDes}>{data?.chatbot?.description}</div>
        </div>
      </div>
    </>
  );

  return (
    <div className={styles.comContainer}>
      <div className={styles.header}>
        <div className={styles.title}>
          <span>机器人绑定</span>
          <span className={styles.subTitle}></span>
        </div>
        {editable ? null : (
          <Button type="link" onClick={handleEdit}>
            编辑
          </Button>
        )}
      </div>
      <div style={{ opacity: data ? 1 : 0 }}>{editable ? editForm : chatbotCard}</div>
    </div>
  );
};

export default ChatbotConfig;
