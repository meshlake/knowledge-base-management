import { Button, Form, Input, Modal, Select, Tag } from 'antd';
import React, { useEffect } from 'react';
import Styles from './index.less';
import { CloseOutlined } from '@ant-design/icons';

type ManuallyEnterProps = {
  isModalOpen: boolean;
  onClose: () => void;
  data: any;
};

const Textarea = Input.TextArea;
const mockTags = [
  { id: 1, content: '税务登记' },
  { id: 2, content: '税务注销' },
  { id: 3, content: '税务变更' },
];

const App: React.FC<ManuallyEnterProps> = (props) => {
  const { isModalOpen, onClose, data } = props;
  const [form] = Form.useForm();
  const [showTagsSelect, setShowTagsSelect] = React.useState<boolean>(false);
  const [tag, setTag] = React.useState<{ id: number; content: string } | null>(data?.tags[0]);
  const [tags, setTags] = React.useState<{ id: number; content: string }[]>(mockTags);

  const handleSelect = (option: any) => {
    setShowTagsSelect(false);
    const selectTag = tags.find((item) => item.id === option);
    if (selectTag) {
      setTag(selectTag);
    }
  };

  useEffect(() => {
    setTags(mockTags);
  }, []);

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
        <Button key="submit" type="primary" style={{ width: '140px' }}>
          保存
        </Button>,
      ]}
      onCancel={onClose}
    >
      <Form form={form} name="control-hooks" colon={false} layout="vertical">
        <Form.Item name="knowledge_item" label="知识点" rules={[{ required: true }]}>
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
