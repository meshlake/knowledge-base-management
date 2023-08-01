import React from 'react';
import KnowledgeBaseTabs from './components/Tabs';
import KnowledgeList from './components/KnowledgeList';
// import Styles from './index.less';

const App: React.FC = () => {
  const tabs = ['知识点列表', '知识点管理', '基础信息'];
  const handleTabChange = (index: number) => {
    console.log(index);
  };
  return (
    <div>
      <KnowledgeBaseTabs items={tabs} onChange={handleTabChange} />
      <KnowledgeList></KnowledgeList>
    </div>
  );
};

export default App;
