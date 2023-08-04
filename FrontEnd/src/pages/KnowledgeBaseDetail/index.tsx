import React, { useEffect } from 'react';
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

const App: React.FC = () => {
  const params = useParams();

  const tabs = ['知识点列表', '知识点管理', '基础信息'];
  const [activeTab, setActiveTab] = React.useState(0);
  const toggleLabelManage = () => {
    setActiveTab(3);
  };
  const [knowledgeBase, setKnowledgeBase] = React.useState<KnowledgeBaseModel>(
    {} as KnowledgeBaseModel,
  ); // 知识库基础信息
  const [loading, setLoading] = React.useState<boolean>(true);

  const handleTabChange = (index: number) => {
    console.log(index);
    setActiveTab(index);
  };

  const handleBack = () => {
    if (activeTab === 3) {
      setActiveTab(1);
    } else {
      history.back();
    }
  };

  const getKnowledgeBaseData = async () => {
    // setLoading(true);
    try {
      const { data: knowledgeBaseData } = await getKnowledgeBase(Number(params.id));
      setKnowledgeBase(knowledgeBaseData);
      setLoading(false);
    } catch (error) {
      console.log(error);
      setLoading(false);
    }
  };

  useEffect(() => {
    getKnowledgeBaseData();
  }, []);

  return (
    <div className={Styles.knowledgeBaseDetail}>
      <div className={Styles.backBtn} onClick={handleBack}>
        <img src="/imgs/backArrow.png" alt="" className={Styles.icon} />
        <div>返回</div>
      </div>
      {activeTab <= 2 ? (
        <KnowledgeBaseTabs items={tabs} onChange={handleTabChange} />
      ) : (
        <div className={Styles.tagTitleContainer}>
          <div className={Styles.tagTitleItem}>标签管理</div>
        </div>
      )}
      <Spin spinning={loading}>
        {activeTab === 0 && <KnowledgeList knowledgeBase={knowledgeBase}></KnowledgeList>}
        {activeTab === 1 && (
          <KnowledgeManage toggleLabelManage={toggleLabelManage}></KnowledgeManage>
        )}
        {activeTab === 2 && <KnowledgeBaseInfo knowledgeBase={knowledgeBase}></KnowledgeBaseInfo>}
        {activeTab === 3 && <TagManager model={knowledgeBase}></TagManager>}
      </Spin>
    </div>
  );
};

export default App;
