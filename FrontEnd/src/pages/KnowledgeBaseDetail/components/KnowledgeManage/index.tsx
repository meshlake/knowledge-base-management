import React, { useEffect, useState } from 'react';
import Styles from './index.less';
import { Button, Pagination, Tree } from 'antd';
import { FileOutlined } from '@ant-design/icons';
import type { DataNode } from 'antd/es/tree';
import KnowledgeItem from '../KnowledgeItem';

type TPagination = Omit<DEFAULT_API.Paginate<any>, 'items'>;

type KnowledgeManageProps = {
  toggleLabelManage?: () => void;
};

const treeData: DataNode[] = [
  {
    title: '标签分类',
    key: '0-0',
    children: [
      {
        title: '申报业务',
        key: '0-0-0',
        children: [
          { title: 'leaf', key: '0-0-0-0', icon: null },
          {
            title: '印花税',
            key: '0-0-0-1',
          },
          { title: 'leaf', key: '0-0-0-2' },
        ],
      },
    ],
  },
  {
    title: '文件筛选',
    key: '0-1',
    children: [
      {
        title: (
          <div>
            <FileOutlined /> aaa.xlsx
          </div>
        ),
        key: '0-1-0',
      },
    ],
  },
];

const App: React.FC<KnowledgeManageProps> = (props) => {
  const { toggleLabelManage } = props;
  const [knowledgeBase, setKnowledgeBase] = useState<any>({
    name: 'lalal',
    count: 0,
  });

  const [pagination, setPagination] = React.useState<TPagination>({
    page: 1,
    pages: 0,
    total: 0,
    size: 10,
  });

  const onSelect = (selectedKeys: React.Key[], info: any) => {
    console.log('selected', selectedKeys, info);
  };

  useEffect(() => {
    setKnowledgeBase({
      name: 'lalal',
    });
    setPagination({
      page: 1,
      pages: 0,
      total: 0,
      size: 10,
    } as TPagination);
  }, []);

  return (
    <div className={Styles.KnowledgeManage}>
      <div className={Styles.header}>
        <div>
          {knowledgeBase.name}：{knowledgeBase.count}条知识
        </div>
        <div>
          <Button type="primary" ghost onClick={toggleLabelManage ? toggleLabelManage : () => {}}>
            标签管理
          </Button>
        </div>
      </div>
      <div className={Styles.content}>
        <div className={Styles.tree}>
          <div>目录</div>
          <Tree
            showLine={true}
            showIcon={false}
            defaultExpandedKeys={['0-0-0']}
            onSelect={onSelect}
            treeData={treeData}
          />
        </div>
        <div className={Styles.knowledgeList}>
          <div style={{ width: '100%' }}>
            <KnowledgeItem
              data={{ id: 1, source: '手动添加', tags: ['税务登记'], content: '我是内容' }}
            ></KnowledgeItem>
          </div>
          <div className={Styles.paginationWrapper}>
            <Pagination
              total={pagination.total}
              showTotal={(total) => `共${pagination.pages}页/${total}条`}
              defaultPageSize={pagination.size}
              defaultCurrent={1}
              showSizeChanger={false}
              size="small"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
