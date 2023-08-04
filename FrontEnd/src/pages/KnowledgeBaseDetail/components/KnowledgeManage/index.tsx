import React, { useEffect, useState } from 'react';
import Styles from './index.less';
import { Button, Col, Pagination, Row, Tree } from 'antd';
import { FileOutlined } from '@ant-design/icons';
import type { DataNode } from 'antd/es/tree';
import KnowledgeItem from '../KnowledgeItem';
import { KnowledgeBaseModel } from '@/pages/KnowledgeBase/types';
import { getFiles } from '@/services/file';
import { useParams } from '@umijs/max';

type TPagination = Omit<DEFAULT_API.Paginate<any>, 'items'>;
type KnowledgeMansgeProps = {
  knowledgeBase: KnowledgeBaseModel;
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
];

const App: React.FC<KnowledgeMansgeProps> = (props) => {
  const { knowledgeBase } = props;
  const params = useParams();

  const [tree, setTree] = useState<DataNode[]>(treeData);

  const [pagination, setPagination] = useState<TPagination>({
    page: 1,
    pages: 0,
    total: 0,
    size: 10,
  });

  const onSelect = (selectedKeys: React.Key[], info: any) => {
    console.log('selected', selectedKeys, info);
  };

  const getFileList = async () => {
    const { data: files } = await getFiles(Number(params.id));
    const fileData = {
      title: '文件筛选',
      key: '0-1',
      children: files.map((v) => {
        return {
          title: (
            <div>
              <FileOutlined /> {v.name}
            </div>
          ),
          key: `0-1-${v.id}`,
        };
      }),
    };
    if (tree.find((v) => v.key === '0-1')) {
      const newTree = tree.map((v) => {
        if (v.key === '0-1') {
          return fileData;
        }
        return v;
      });
      setTree(newTree);
    } else {
      setTree([...tree, fileData]);
    }
  };

  useEffect(() => {
    setPagination({
      page: 1,
      pages: 0,
      total: 0,
      size: 10,
    } as TPagination);
    getFileList();
  }, []);

  return (
    <div className={Styles.KnowledgeManage}>
      <div className={Styles.header}>
        <div>{knowledgeBase?.name}：条知识</div>
        <div>
          <Button type="primary" ghost>
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
            treeData={tree}
          />
        </div>
        <div className={Styles.knowledgeList}>
          <div style={{ width: '100%' }}>
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <KnowledgeItem
                  data={{
                    id: 1,
                    content: '我是内容',
                    metadata: { type: 'MANUALLY', knowledge_item_id: '1', source: '', user_id: 1 },
                  }}
                ></KnowledgeItem>
              </Col>
            </Row>
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
