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

const App: React.FC = () => {
  const params = useParams();

  const tabs = ['知识点列表', '知识点管理', '基础信息'];
  const [activeTab, setActiveTab] = React.useState(0);
  const [knowledgeBase, setKnowledgeBase] = React.useState<KnowledgeBaseModel>(
    {} as KnowledgeBaseModel,
  ); // 知识库基础信息
  const [loading, setLoading] = React.useState<boolean>(false);

  const handleTabChange = (index: number) => {
    console.log(index);
    setActiveTab(index);
  };

  const handleBack = () => {
    history.back();
  };

  const getKnowledgeBaseData = async () => {
    setLoading(true);
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
      <KnowledgeBaseTabs items={tabs} onChange={handleTabChange} />
      <Spin spinning={loading}>
        {activeTab === 0 && <KnowledgeList knowledgeBase={knowledgeBase}></KnowledgeList>}
        {activeTab === 1 && <KnowledgeManage knowledgeBase={knowledgeBase}></KnowledgeManage>}
        {activeTab === 2 && <KnowledgeBaseInfo knowledgeBase={knowledgeBase}></KnowledgeBaseInfo>}
      </Spin>
    </div>
  );
};

export default App;
