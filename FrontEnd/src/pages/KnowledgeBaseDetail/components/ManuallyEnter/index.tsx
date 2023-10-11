import { Button, Form, Input, Modal, Select, Tag, notification } from 'antd';
import React, { useEffect, useState } from 'react';
import Styles from './index.less';
import { CloseOutlined } from '@ant-design/icons';
import { createKnowledgeItem, updateKnowledgeItem } from '@/services/knowledgeItem';
import { useParams } from '@umijs/max';
import { getKnowledgeBaseAllTags } from '@/services/knowledgeBaseTags';
import { KnowledgeBaseTagModel } from '@/pages/KnowledgeBase/types';

type ManuallyEnterProps = {
  isModalOpen: boolean;
  onClose: (isNeedRefresh: boolean) => void;
  data: KNOWLEDGE_ITEM_API.KnowledgeItem;
};

const Textarea = Input.TextArea;

const App: React.FC<ManuallyEnterProps> = (props) => {
  const params = useParams();

  const { isModalOpen, onClose, data } = props;
  const [form] = Form.useForm();
  const [showTagsSelect, setShowTagsSelect] = useState<boolean>(false);
  const [tag, setTag] = useState<number | null>(null);
  const [tags, setTags] = useState<KnowledgeBaseTagModel[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  const handleSelect = (option: number) => {
    setShowTagsSelect(false);
    const selectTag = tags.find((item) => item.id === option);
    if (selectTag) {
      setTag(selectTag.id);
    }
  };

  const handleCreate = async (formValues: any) => {
    setLoading(true);
    try {
      let structure: 'NORMAL' | 'QA' = 'NORMAL';
      let content = formValues.content;
      if (!formValues.content) {
        content = JSON.stringify({
          question: formValues.question,
          answer: formValues.answer,
        });
        structure = 'QA';
      }
      const body: KNOWLEDGE_ITEM_API.KnowledgeItemCreate = {
        content: content,
        structure: structure,
      };
      if (tag) {
        body.tag = tag;
      }
      const res = await createKnowledgeItem(Number(params.id), body);
      if (res.data.isNeedReview) {
        notification.warning({ message: '新建知识点存在重复情况，请等待审核员处理' });
      } else {
        notification.success({ message: '创建成功' });
      }
      onClose(true);
      setLoading(false);
    } catch (error) {
      setLoading(false);
    }
  };

  const handleUpdate = async (formValues: any) => {
    setLoading(true);
    try {
      let structure: 'NORMAL' | 'QA' = 'NORMAL';
      let content = formValues.content;
      if (!formValues.content) {
        content = JSON.stringify({
          question: formValues.question,
          answer: formValues.answer,
        });
        structure = 'QA';
      }
      const body: KNOWLEDGE_ITEM_API.KnowledgeItemUpdate = {
        id: data.id,
        content: content,
        structure: structure,
      };
      if (tag) {
        body.tag = tag;
      }
      await updateKnowledgeItem(body);
      notification.success({ message: '更新成功' });
      onClose(true);
      setLoading(false);
    } catch (error) {
      setLoading(false);
    }
  };

  const handleSave = () => {
    form.validateFields().then((values) => {
      if (!data?.id) {
        handleCreate(values);
      } else {
        handleUpdate(values);
      }
    });
  };

  useEffect(() => {
    getKnowledgeBaseAllTags(Number(params.id)).then((res) => {
      setTags(res);
    });
    if (data.id) {
      if (data.metadata?.structure && data.metadata.structure === 'QA') {
        form.setFieldsValue(JSON.parse(data.content));
      } else {
        form.setFieldsValue({ content: data.content });
      }
      setTag(data.metadata.tag ? data.metadata.tag : null);
    } else {
      form.resetFields();
      setTag(null);
    }
  }, [data]);

  return (
    <Modal
      title="手动添加"
      open={isModalOpen}
      className={Styles.manuallyEnterModal}
      width={800}
      maskClosable={false}
      bodyStyle={{
        padding: '48px 8px',
        paddingBottom: '30px',
      }}
      footer={[
        <Button
          key="submit"
          type="primary"
          style={{ width: '140px' }}
          onClick={handleSave}
          loading={loading}
        >
          保存
        </Button>,
      ]}
      onCancel={() => onClose(false)}
    >
      {/* 新增知识和编辑问答知识时都为问答的格式 */}
      {!data.id || (data.metadata?.structure && data.metadata.structure === 'QA') ? (
        <Form form={form} name="control-hooks" colon={false} layout="vertical">
          <Form.Item name="question" label="问题" rules={[{ required: true }]}>
            <Textarea rows={2} placeholder="问题"></Textarea>
          </Form.Item>
          <Form.Item name="answer" label="答案" rules={[{ required: true }]}>
            <Textarea rows={5} placeholder="答案"></Textarea>
          </Form.Item>
        </Form>
      ) : (
        <Form form={form} name="control-hooks" colon={false} layout="vertical">
          <Form.Item name="content" label="知识点" rules={[{ required: true }]}>
            <Textarea rows={10} placeholder="录入知识点"></Textarea>
          </Form.Item>
        </Form>
      )}

      {/* 有标签 */}
      {tag && (
        <Tag
          color="#D9F0FD"
          className={Styles.normalTags}
          closable
          onClose={() => setTag(null)}
          closeIcon={<CloseOutlined style={{ color: '#3d3d3d' }} />}
        >
          {tags.find((item) => item.id === tag)?.name}
        </Tag>
      )}
      {/* 无标签显示下拉 */}
      {!tag && showTagsSelect && (
        <Select
          style={{ width: '200px' }}
          placeholder="查找并添加标签"
          showSearch
          notFoundContent={`对不起，未找到相关标签。
        创建/编辑标签请在"知识库管理->标签管理页面"操作。`}
          onSelect={handleSelect}
        >
          {tags.map((item) => (
            <Select.Option value={item.id} key={item.id}>
              {item.name}
            </Select.Option>
          ))}
        </Select>
      )}
      {/* 无标签显示添加 */}
      {!tag && !showTagsSelect && <div onClick={() => setShowTagsSelect(true)}>添加标签</div>}
    </Modal>
  );
};

export default App;
