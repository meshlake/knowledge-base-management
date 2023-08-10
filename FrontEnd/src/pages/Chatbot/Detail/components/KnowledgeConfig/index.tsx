import { Button, Form, Select } from 'antd';
import React, { useEffect, useState } from 'react';
import { MinusCircleOutlined, PlusOutlined } from '@ant-design/icons';
import { getKnowledgeBaseList } from '@/services/knowledgeBase';
import { history } from '@umijs/max';
import styles from './index.less';

type Props = {
  data?: Chatbot_API.Chatbot;
  multiple?: boolean;
  updateRequest: (id: string, data: Chatbot_API.ChatbotUpdate) => Promise<void>;
};

const KnowledgeConfig: React.FC<Props> = (props) => {
  const { data, multiple, updateRequest } = props;
  const [form] = Form.useForm();
  const [editable, setEditable] = useState(false);
  const [loading, setLoading] = useState(false);
  const [knowledgeList, setKnowledgeList] = useState<{ id: string; name: string }[]>([]);

  const selectedList = Form.useWatch('list', form) || [];

  const getKnowledgeList = async () => {
    try {
      const data = await getKnowledgeBaseList();
      setKnowledgeList(data.items);
    } catch (e) {
      console.log(e);
    }
  };

  const resetForm = () => {
    if (Array.isArray(data?.knowledge_bases) && data?.knowledge_bases.length) {
      form.setFieldsValue({ list: data.knowledge_bases.map((item) => ({ id: item.id })) });
    } else {
      form.setFieldsValue({ list: [{ id: undefined }] });
    }
  };

  const handleEdit = () => {
    setEditable(true);
    getKnowledgeList().then(() => {
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
        updateRequest(data.id, {
          knowledge_bases: values.list.map((item: any) => item.id),
        })
          .then(() => {
            setEditable(false);
          })
          .finally(() => {
            setLoading(false);
          });
      })
      .catch(() => {});
  };

  const getDisabledList = (index: number) => {
    const result: string[] = [];
    if (Array.isArray(selectedList)) {
      selectedList.forEach((item, i) => {
        if (item && item.id !== undefined && i !== index) {
          result.push(item.id);
        }
      });
    }
    return result;
  };

  useEffect(() => {
    if (data && data.knowledge_bases.length === 0) {
      form.setFieldsValue({ list: [{ id: '' }] });
      handleEdit();
    }
    resetForm();
  }, [data]);

  useEffect(() => {
    getKnowledgeList();
  }, []);

  const editForm = (
    <>
      <Form
        form={form}
        colon={false}
        autoComplete="off"
        requiredMark={false}
        labelAlign="left"
        style={{ maxWidth: '72%' }}
      >
        <Form.List name="list">
          {(fields, { add, remove }) => (
            <>
              {fields.map(({ key, name, ...restField }) => (
                <div
                  key={key}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    margin: '16px 0',
                  }}
                >
                  <span style={{ marginRight: '32px' }}>选择关联知识库</span>
                  <Form.Item
                    {...restField}
                    label=""
                    name={[name, 'id']}
                    rules={[{ required: true, message: '请选择' }]}
                    style={{ margin: '0 32px', flex: 1 }}
                  >
                    <Select placeholder="请选择">
                      {knowledgeList.map((item) => (
                        <Select.Option
                          key={item.id}
                          value={item.id}
                          disabled={getDisabledList(key).includes(item.id)}
                        >
                          {item.name}
                        </Select.Option>
                      ))}
                    </Select>
                  </Form.Item>
                  {multiple ? (
                    <MinusCircleOutlined style={{ color: 'red' }} onClick={() => remove(name)} />
                  ) : null}
                </div>
              ))}
              {multiple ? (
                <Form.Item style={{ marginTop: 24 }}>
                  <Button type="primary" ghost onClick={() => add()} block icon={<PlusOutlined />}>
                    添加关联知识库
                  </Button>
                </Form.Item>
              ) : null}
            </>
          )}
        </Form.List>
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

  const knowledgeBaseList = (
    <>
      <div className={styles.cardList}>
        {data?.knowledge_bases.map((item) => (
          <div
            className={styles.cardListItem}
            key={item.id}
            onClick={() => history.push(`/knowledgeBase/${item.id}`)}
          >
            <div className={styles.cardListItemTitle}>{item.name}</div>
            <div className={styles.cardListItemDes}>{item.description}</div>
          </div>
        ))}
      </div>
    </>
  );

  return (
    <div className={styles.comContainer}>
      <div className={styles.header}>
        <div className={styles.title}>
          <span>知识库设定</span>
          <span className={styles.subTitle}>选择对应的知识库，完成机器人训练</span>
        </div>
        {editable ? null : (
          <Button type="link" onClick={handleEdit}>
            编辑
          </Button>
        )}
      </div>
      <div style={{ opacity: data ? 1 : 0 }}>{editable ? editForm : knowledgeBaseList}</div>
    </div>
  );
};

export default KnowledgeConfig;
