import React, { useEffect, useState } from 'react';
import KnowledgeBaseTabs from './components/Tabs';
import KnowledgeList from './components/KnowledgeList';
import KnowledgeManage from './components/KnowledgeManage';
import KnowledgeBaseInfo from './components/KnowledgeBaseInfo';
import Styles from './index.less';
import { KnowledgeBaseModel } from '@/pages/KnowledgeBase/types';
import { getKnowledgeBase } from '@/services/knowledgeBase';
import { useParams } from '@umijs/max';
import { Spin } from 'antd';
import TagManager from './components/TagManage';
import { getFiles } from '@/services/file';
import { CloseOutlined } from '@ant-design/icons';

type FilesStatus = {
  name: string;
  status: string;
};

let refreshTimer: any = null;

const App: React.FC = () => {
  const params = useParams();

  const tabs = ['知识点列表', '知识点管理', '基础信息'];

  const [activeTab, setActiveTab] = useState(0);
  const [knowledgeBase, setKnowledgeBase] = useState<KnowledgeBaseModel>({} as KnowledgeBaseModel); // 知识库基础信息
  const [loading, setLoading] = useState<boolean>(true);
  const [fileStatus, setFileStatus] = useState<FilesStatus>({} as FilesStatus); // 向量化中的文件

  const toggleLabelManage = () => {
    setActiveTab(3);
  };
  const handleTabChange = (index: number) => {
    console.log(index);
    setActiveTab(index);
  };

  const getKnowledgeBaseData = async () => {
    // setLoading(true);
    try {
      const { data: knowledgeBaseData } = await getKnowledgeBase(Number(params.id));
      setKnowledgeBase(knowledgeBaseData);
    } catch (error) {
      console.log(error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefreshStatus = () => {
    const knowledgeBaseId = Number(params.id);
    if (!knowledgeBaseId) {
      return;
    }
    if (refreshTimer) {
      clearTimeout(refreshTimer);
    }
    getFiles(knowledgeBaseId)
      .then((res) => {
        const embeddingFiles = res?.data.filter((v) => v.status === 'EMBEDDING');
        const failedFiles = res?.data.filter((v) => v.status === 'FAILED');
        if (embeddingFiles.length > 0) {
          setFileStatus({
            name: embeddingFiles[0].name,
            status: embeddingFiles[0].status,
          });
          refreshTimer = setTimeout(() => {
            handleRefreshStatus();
          }, 5000);
        } else if (failedFiles.length > 0) {
          setFileStatus({
            name: failedFiles[0].name,
            status: failedFiles[0].status,
          });
          clearTimeout(refreshTimer);
        } else {
          setFileStatus({} as FilesStatus);
          clearTimeout(refreshTimer);
        }
      })
      .catch((err) => {
        console.log(err);
      });
  };

  useEffect(() => {
    getKnowledgeBaseData();
    handleRefreshStatus();
  }, []);

  return (
    <div className={Styles.knowledgeBaseDetail}>
      {fileStatus?.name && (
        <div
          className={Styles.tips}
          style={{
            background:
              fileStatus.status === 'EMBEDDING'
                ? 'rgba(54, 143, 255, 0.7)'
                : 'rgba(244, 9, 9, 0.7)',
          }}
        >
          {fileStatus.status === 'EMBEDDING'
            ? `文件${fileStatus?.name}正在处理上传中`
            : '非常抱歉，文件处理出现问题，请重新上传'}
          {fileStatus.status === 'FAILED' && (
            <CloseOutlined
              className={Styles.close}
              onClick={() => setFileStatus({} as FilesStatus)}
            />
          )}
        </div>
      )}
      {activeTab <= 2 ? (
        <KnowledgeBaseTabs items={tabs} onChange={handleTabChange} activeIndex={activeTab} />
      ) : (
        <div className={Styles.tagTitleContainer}>
          <div
            className={Styles.TagManagerBack}
            onClick={() => {
              setActiveTab(1);
            }}
          >
            <img src="/imgs/backArrow.png" alt="" className={Styles.icon} />
            <div>返回</div>
          </div>
          <div className={Styles.tagTitleItem}>标签管理</div>
        </div>
      )}
      <Spin spinning={loading}>
        {activeTab === 0 && (
          <KnowledgeList
            knowledgeBase={knowledgeBase}
            isFileEmbedding={fileStatus?.name?.length > 0 && fileStatus?.status === 'EMBEDDING'}
            refresh={handleRefreshStatus}
          ></KnowledgeList>
        )}
        {activeTab === 1 && (
          <KnowledgeManage
            knowledgeBase={knowledgeBase}
            toggleLabelManage={toggleLabelManage}
          ></KnowledgeManage>
        )}
        {activeTab === 2 && <KnowledgeBaseInfo knowledgeBase={knowledgeBase}></KnowledgeBaseInfo>}
        {activeTab === 3 && <TagManager model={knowledgeBase}></TagManager>}
      </Spin>
    </div>
  );
};

export default App;
