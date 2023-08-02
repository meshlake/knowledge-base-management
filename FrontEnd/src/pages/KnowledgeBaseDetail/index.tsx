import React from 'react';
import KnowledgeBaseTabs from './components/Tabs';
import KnowledgeList from './components/KnowledgeList';
import KnowledgeManage from './components/KnowledgeManage';
import KnowledgeBaseInfo from './components/KnowledgeBaseInfo';
import Styles from './index.less';

const App: React.FC = () => {
  const tabs = ['知识点列表', '知识点管理', '基础信息'];
  const [activeTab, setActiveTab] = React.useState(0);

  const handleTabChange = (index: number) => {
    console.log(index);
    setActiveTab(index);
  };

  const handleBack = () => {
    console.log('back');
  };

  return (
    <div className={Styles.knowledgeBaseDetail}>
      <div className={Styles.backBtn} onClick={handleBack}>
        <img src="/imgs/backArrow.png" alt="" className={Styles.icon} />
        <div>返回</div>
      </div>
      <KnowledgeBaseTabs items={tabs} onChange={handleTabChange} />
      {activeTab === 0 && <KnowledgeList></KnowledgeList>}
      {activeTab === 1 && <KnowledgeManage></KnowledgeManage>}
      {activeTab === 2 && <KnowledgeBaseInfo name="名字" description="描述"></KnowledgeBaseInfo>}
    </div>
  );
};

export default App;
