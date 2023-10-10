import { Button, Form, Modal, UploadProps, message } from 'antd';
import Dragger from 'antd/es/upload/Dragger';
import React, { useEffect, useState } from 'react';
import Styles from './index.less';
import { createFile } from '@/services/file';
import { useParams } from '@umijs/max';

type ImportFileProps = {
  isModalOpen: boolean;
  onClose: (isNeedRefresh: boolean) => void;
};

const App: React.FC<ImportFileProps> = (props) => {
  const { isModalOpen, onClose } = props;
  const params = useParams();
  const [loading, setLoading] = useState<boolean>(false);

  const [form] = Form.useForm();

  const normFile = (e: any) => {
    console.log('Upload event:', e);
    if (Array.isArray(e)) {
      return e;
    }
    return e?.fileList;
  };

  const draggerProps: UploadProps = {
    name: 'file',
    accept: '.doc,.docx,.txt,.xlsx,.csv,.pdf,.pptx,.md',
    action: `/api/files/upload`,
    headers: {
      Authorization: `Bearer ${localStorage.getItem('access_token')}`,
    },
    onChange(info) {
      const { status } = info.file;
      if (status !== 'uploading') {
        console.log(info.file, info.fileList);
      }
      if (status === 'done') {
        message.success(`${info.file.name}上传成功`);
      } else if (status === 'error') {
        message.error(`${info.file.response.detail}`);
      }
    },
    onDrop(e) {
      console.log('Dropped files', e.dataTransfer.files);
    },
    maxCount: 1,
  };

  const handleCreateFile = async () => {
    setLoading(true);
    try {
      const values = await form.validateFields();
      console.log('Success:', values);
      if (values.file[0]?.response?.data?.name && values.file[0]?.response?.data?.path) {
        await createFile({
          name: values.file[0]?.response?.data?.name,
          path: values.file[0]?.response?.data?.path,
          knowledge_base_id: Number(params.id),
        });
        onClose(true);
      }
      setLoading(false);
    } catch (errorInfo) {
      console.log('Failed:', errorInfo);
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!isModalOpen) {
      form.resetFields();
    }
  }, [isModalOpen]);

  return (
    <Modal
      title="文件导入"
      open={isModalOpen}
      className={Styles.importFileModal}
      width={800}
      maskClosable={false}
      bodyStyle={{
        padding: '86px 8px',
        paddingBottom: '66px',
      }}
      footer={[
        <Button
          key="submit"
          type="primary"
          style={{ width: '140px' }}
          onClick={handleCreateFile}
          loading={loading}
        >
          保存
        </Button>,
      ]}
      onCancel={() => onClose(false)}
    >
      <Form name="basic" autoComplete="off" form={form}>
        <Form.Item
          label=""
          name="file"
          rules={[{ required: true, message: '请上传文件' }]}
          valuePropName="fileList"
          getValueFromEvent={normFile}
        >
          <Dragger {...draggerProps} className={Styles.dragger}>
            <p className={Styles.importFileImg}>
              <img src="/imgs/importFile.png" alt="" style={{ width: '100px', height: '100px' }} />
            </p>
            <p className={Styles.title}>文件上传</p>
            <p className={Styles.hint}>
              将文件拖拽到此区域,支持.doc,.docx,.txt,.xlsx,.csv,.pdf,.pptx,.md
            </p>
          </Dragger>
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default App;
