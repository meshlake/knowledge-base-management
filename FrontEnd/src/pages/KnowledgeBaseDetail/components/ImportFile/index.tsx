import { Button, Modal, UploadProps, message } from 'antd';
import Dragger from 'antd/es/upload/Dragger';
import React from 'react';
import Styles from './index.less';

type ImportFileProps = {
  isModalOpen: boolean;
  onClose: (isNeedRefresh: boolean) => void;
};

const App: React.FC<ImportFileProps> = (props) => {
  const { isModalOpen, onClose } = props;

  const draggerProps: UploadProps = {
    name: 'file',
    multiple: true,
    action: 'https://www.mocky.io/v2/5cc8019d300000980a055e76',
    onChange(info) {
      const { status } = info.file;
      if (status !== 'uploading') {
        console.log(info.file, info.fileList);
      }
      if (status === 'done') {
        message.success(`${info.file.name} file uploaded successfully.`);
      } else if (status === 'error') {
        message.error(`${info.file.name} file upload failed.`);
      }
    },
    onDrop(e) {
      console.log('Dropped files', e.dataTransfer.files);
    },
    maxCount: 1,
  };

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
        <Button key="submit" type="primary" style={{ width: '140px' }}>
          保存
        </Button>,
      ]}
      onCancel={() => onClose(false)}
    >
      <Dragger {...draggerProps} className={Styles.dragger}>
        <p className={Styles.importFileImg}>
          <img src="/imgs/importFile.png" alt="" style={{ width: '100px', height: '100px' }} />
        </p>
        <p className={Styles.title}>文件上传</p>
        <p className={Styles.hint}>将文件拖拽到此区域,支持.doc,.docx,.txt,.xlsx,.csv,.pdf,.pptx</p>
      </Dragger>
    </Modal>
  );
};

export default App;
