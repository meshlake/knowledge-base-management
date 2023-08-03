import { Button, Form, Input, Modal, Select, Tag, notification } from 'antd';
import React, { useEffect, useState } from 'react';
import Styles from './index.less';
import { CloseOutlined } from '@ant-design/icons';
import { createKnowledgeItem, updateKnowledgeItem } from '@/services/knowledgeItem';
import { useParams } from '@umijs/max';

type ManuallyEnterProps = {
  isModalOpen: boolean;
  onClose: (isNeedRefresh: boolean) => void;
  data: KNOWLEDGE_ITEM_API.KnowledgeItem;
};

const Textarea = Input.TextArea;
const mockTags = [
  { id: 1, content: '税务登记' },
  { id: 2, content: '税务注销' },
  { id: 3, content: '税务变更' },
];

const App: React.FC<ManuallyEnterProps> = (props) => {
  const params = useParams();

  const { isModalOpen, onClose, data } = props;
  const [form] = Form.useForm();
  const [showTagsSelect, setShowTagsSelect] = useState<boolean>(false);
  const [tag, setTag] = useState<{ id: number; content: string } | null>(null);
  const [tags, setTags] = useState<{ id: number; content: string }[]>(mockTags);
  const [loading, setLoading] = useState<boolean>(false);

  const handleSelect = (option: any) => {
    setShowTagsSelect(false);
    const selectTag = tags.find((item) => item.id === option);
    if (selectTag) {
      setTag(selectTag);
    }
  };

  const handleCreate = async (formValues: any) => {
    setLoading(true);
    try {
      await createKnowledgeItem(Number(params.id), { content: formValues.content });
      notification.success({ message: '创建成功' });
      onClose(true);
      setLoading(false);
    } catch (error) {
      setLoading(false);
    }
  };

  const handleUpdate = async (formValues: any) => {
    setLoading(true);
    try {
      await updateKnowledgeItem({ id: data.id, content: formValues.content });
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
    setTags(mockTags);
    if (data.id) {
      form.setFieldsValue({ content: data.content });
    } else {
      form.resetFields();
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
      <Form form={form} name="control-hooks" colon={false} layout="vertical">
        <Form.Item name="content" label="知识点" rules={[{ required: true }]}>
          <Textarea rows={10} placeholder="录入知识点"></Textarea>
        </Form.Item>
      </Form>
      {/* 有标签 */}
      {tag && (
        <Tag
          color="#D9F0FD"
          className={Styles.normalTags}
          closable
          onClose={() => setTag(null)}
          closeIcon={<CloseOutlined style={{ color: '#3d3d3d' }} />}
        >
          {tag.content}
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
              {item.content}
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
