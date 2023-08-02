import { Button, Pagination } from 'antd';
import React, { useEffect } from 'react';
import Styles from './index.less';
import KnowledgeItem from '../KnowledgeItem';

type TPagination = Omit<DEFAULT_API.Paginate<any>, 'items'>;

const App: React.FC = () => {
  const [knowledgeBase, setKnowledgeBase] = React.useState<any>({
    name: 'lalal',
  });

  const [knowledgeList, setKnowledgeList] = React.useState<any[]>([]);

  const [pagination, setPagination] = React.useState<TPagination>({
    page: 1,
    pages: 0,
    total: 0,
    size: 10,
  });

  const handleDeleteKnowledgeItem = (id: number) => {
    console.log(id);
  };

  useEffect(() => {
    setKnowledgeBase({
      name: 'lalal',
    });
    setKnowledgeList([]);
    setPagination({
      page: 1,
      pages: 0,
      total: 0,
      size: 10,
    } as TPagination);
  }, []);

  return (
    <div className={Styles.knowledgeList}>
      <div className={Styles.header}>
        <div>
          {knowledgeBase.name}：{knowledgeList.length}条知识
        </div>
        {/* <div>搜索</div> */}
        <div>
          <Button>文件导入</Button>
          <Button type="primary" ghost>
            手动添加
          </Button>
        </div>
      </div>
      {knowledgeList?.length > 0 ? (
        <div>
          <div>
            <KnowledgeItem
              data={{ id: 1, source: '手动添加', tags: ['税务登记'], content: '我是内容' }}
              onDelete={() => handleDeleteKnowledgeItem(1)}
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
      ) : (
        <div className={Styles.emptyTips}>
          <div className={Styles.tipWrapper}>
            <div className={Styles.title}>还没有知识点</div>
            <div className={Styles.content}>
              您还没有添加任何知识点，可以通过手动输入或者文件导入完成知识点录入～
            </div>
            <div className={Styles.btns}>
              <Button style={{ width: '140px' }}>文件导入</Button>
              <Button style={{ width: '140px' }} type="primary" ghost>
                手动添加
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
