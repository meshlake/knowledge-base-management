import React from 'react';
import KnowledgeBaseTabs from './components/Tabs';
import KnowledgeList from './components/KnowledgeList';
import KnowledgeManage from './components/KnowledgeManage';
// import Styles from './index.less';

const App: React.FC = () => {
  const tabs = ['知识点列表', '知识点管理', '基础信息'];
  const [activeTab, setActiveTab] = React.useState(0);

  const handleTabChange = (index: number) => {
    console.log(index);
    setActiveTab(index);
  };

  return (
    <div>
      <KnowledgeBaseTabs items={tabs} onChange={handleTabChange} />
      {activeTab === 0 && <KnowledgeList></KnowledgeList>}
      {activeTab === 1 && <KnowledgeManage></KnowledgeManage>}
    </div>
  );
};

export default App;
