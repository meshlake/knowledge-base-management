import React, { useState } from 'react';
import Styles from './index.less';

type TabsProps = {
  items: string[];
  visible?: boolean;
  onChange?: (index: number) => void;
};

const App: React.FC<TabsProps> = (props) => {
  const { items, onChange, visible = true } = props;
  const [activeIndex, setActiveIndex] = useState(0);

  return (
    <div className={Styles.tabsWrapper} style={{ display: visible ? 'flex' : 'none' }}>
      {items.map((item, index) => {
        return (
          <div
            key={item}
            onClick={() => {
              if (onChange) {
                onChange(index);
              }
              setActiveIndex(index);
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
