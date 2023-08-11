import React from 'react';
import Styles from './index.less';
import { history } from '@umijs/max';

type TabsProps = {
  items: string[];
  visible?: boolean;
  onChange?: (index: number) => void;
  activeIndex: number;
};

const App: React.FC<TabsProps> = (props) => {
  const { items, onChange, activeIndex } = props;

  const handleBack = () => {
    history.push('/knowledgeBase');
  };

  return (
    <div className={Styles.tabsWrapper}>
      <div className={Styles.backBtn} onClick={handleBack}>
        <img src="/imgs/backArrow.png" alt="" className={Styles.icon} />
        <div>返回</div>
      </div>
      {items.map((item, index) => {
        return (
          <div
            key={item}
            onClick={() => {
              if (onChange) {
                onChange(index);
              }
            }}
            className={Styles.tab}
            style={activeIndex === index ? { background: '#3d73ec', color: '#fff' } : {}}
          >
            {item}
          </div>
        );
      })}
    </div>
  );
};

export default App;
