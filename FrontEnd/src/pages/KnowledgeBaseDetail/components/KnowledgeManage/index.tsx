import React, { useEffect, useState } from 'react';
import Styles from './index.less';
import { Button, Col, Pagination, Row, Spin, Tree } from 'antd';
import { FileOutlined } from '@ant-design/icons';
import type { DataNode } from 'antd/es/tree';
import KnowledgeItem from '../KnowledgeItem';
import { KnowledgeBaseModel, KnowledgeBaseTagModel } from '@/pages/KnowledgeBase/types';
import { getFiles } from '@/services/file';
import { useModel, useParams } from '@umijs/max';
import { getKnowledgeItems } from '@/services/knowledgeItem';
import { getKnowledgeBaseAllTags } from '@/services/knowledgeBaseTags';
import { HierarchyTagModel } from '../../types';

type TPagination = Omit<DEFAULT_API.Paginate<any>, 'items'>;

type KnowledgeManageProps = {
  knowledgeBase: KnowledgeBaseModel;
  toggleLabelManage?: () => void;
};

const App: React.FC<KnowledgeManageProps> = (props) => {
  const { knowledgeBase, toggleLabelManage = () => {} } = props;

  //标签管理权限
  const { initialState } = useModel('@@initialState');
  const { permissions } = initialState ?? {};
  const pagePermissions = permissions?.filter((p) => p[1] === 'page').map((p) => p[2]);
  const [isCanManageTag, setIsCanManageTag] = useState<boolean>(
    pagePermissions?.includes('/tag') || false,
  );

  const [expandKeys, setExpandKeys] = useState<React.Key[]>([]);

  const params = useParams();

  const [tree, setTree] = useState<DataNode[]>([]);
  const [pagination, setPagination] = useState<TPagination>({
    page: 1,
    pages: 0,
    total: 0,
    size: 10,
  });
  const [files, setFiles] = useState<FILE_API.File[]>([]);
  const [knowledgeList, setKnowledgeList] = useState<KNOWLEDGE_ITEM_API.KnowledgeItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [currentKey, setCurrentKey] = useState<string>('');
  const [total, setTotal] = useState<number>(0);
  const [tags, setTags] = useState<KnowledgeBaseTagModel[]>([]);

  const getAllKnowledgeItems = async () => {
    setLoading(true);
    try {
      const data = await getKnowledgeItems(Number(params.id), 1, {}, 1);
      setTotal(data.total);
      setLoading(false);
    } catch (error) {
      console.log(error);
      setLoading(false);
    }
  };

  const getKnowledgeItemsByFile = async (key: string, page: number) => {
    const id = key.split('-')[2];
    const filepath = files.find((v) => v.id === Number(id))?.path;
    if (filepath) {
      setLoading(true);
      try {
        const data = await getKnowledgeItems(Number(params.id), page, { filepath }, 10);
        setKnowledgeList(data.items);
        setPagination({
          page: data.page,
          pages: data.pages,
          total: data.total,
          size: data.size,
        });
        setLoading(false);
      } catch (error) {
        setLoading(false);
      }
    }
  };

  const getKnowledgeItemsByTag = async (key: string, page: number) => {
    const tag_id = key.split('-')[2];
    if (tag_id) {
      setLoading(true);
      try {
        const data = await getKnowledgeItems(
          Number(params.id),
          page,
          { tag_id: Number(tag_id) },
          10,
        );
        setKnowledgeList(data.items);
        setPagination({
          page: data.page,
          pages: data.pages,
          total: data.total,
          size: data.size,
        });
        setLoading(false);
      } catch (error) {
        setLoading(false);
      }
    }
  };

  const onSelect = (selectedKeys: React.Key[]) => {
    console.log('selected', selectedKeys);
    if (selectedKeys.length === 0) {
      setKnowledgeList([]);
      setCurrentKey('');
      return;
    }
    const key = selectedKeys[0];
    setCurrentKey(`${key}`);
    if (`${key}`.startsWith('0-1')) {
      getKnowledgeItemsByFile(`${key}`, 1);
    } else if (`${key}`.startsWith('0-0')) {
      getKnowledgeItemsByTag(`${key}`, 1);
    }
  };

  const handleChangePage = (page: number) => {
    if (currentKey.startsWith('0-1')) {
      getKnowledgeItemsByFile(currentKey, page);
    } else if (currentKey.startsWith('0-0')) {
      getKnowledgeItemsByTag(currentKey, page);
    }
  };

  const getFileList = async () => {
    const { data: files } = await getFiles(Number(params.id));
    //只显示状态为向量化成功的文件
    const filterFiles = files.filter((v) => v.status === 'SUCCESS');
    setFiles(filterFiles);

    const fileData = {
      title: '文件筛选',
      key: '0-1',
      selectable: false,
      children: filterFiles.map((v) => {
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
    return fileData;
  };

  const transformToTagHierarchy = (tags: KnowledgeBaseTagModel[]): HierarchyTagModel[] => {
    const result: HierarchyTagModel[] = [];
    const tagMap: Map<string, HierarchyTagModel> = new Map<string, HierarchyTagModel>();
    tags.forEach((tag) => {
      if (tag.parent_id === null || tag.parent_id <= 0) {
        const hierarchyTag: HierarchyTagModel = {
          ...tag,
          selectable: false,
          children: [],
        };
        result.push(hierarchyTag);
        tagMap.set(tag.id, hierarchyTag);
      } else {
        const parentTag = tagMap.get(tag.parent_id);
        if (parentTag) {
          parentTag.children.push({
            ...tag,
            selectable: true,
            children: [],
          } as HierarchyTagModel);
        }
      }
    });
    return result;
  };

  const transformToDataNode = (tag: HierarchyTagModel): DataNode => {
    return {
      title: tag.name,
      key: `0-0-${tag.id}`,
    } as DataNode;
  };

  const transformToDataNodes = (tags: HierarchyTagModel[]): DataNode[] => {
    if (!tags) {
      return [];
    }
    return tags.map((tag) => {
      return {
        ...transformToDataNode(tag),
        selectable: tag.selectable,
        children: transformToDataNodes(tag.children),
      };
    });
  };

  const fetchKnowledgeTags = async () => {
    return getKnowledgeBaseAllTags(knowledgeBase.id)
      .then((res) => {
        setTags(res);
        return res;
      })
      .then((tags) => transformToTagHierarchy(tags))
      .then((tags) => {
        return {
          title: '标签分类',
          key: '0-0',
          selectable: false,
          children: transformToDataNodes(tags),
        };
      });
  };

  const setTreeData = async () => {
    const files = await getFileList();
    const tags = await fetchKnowledgeTags();
    setTree([tags, files]);
    if (tags.children.length > 0) {
      for (let i = 0; i < tags.children.length; i++) {
        const tag = tags.children[i];
        if (tag.children && tag.children.length > 0) {
          onSelect([`${tag.children[0].key}`]);
          setExpandKeys([`0-0`, `${tags.children[i].key}`]);
          break;
        }
      }
    }
  };

  const onExpand = (expandedKeys: React.Key[]) => {
    setExpandKeys(expandedKeys);
  };

  useEffect(() => {
    setTreeData();
    getAllKnowledgeItems();
  }, []);

  //标签管理权限
  useEffect(() => {
    if (initialState) {
      const { permissions } = initialState ?? {};
      const pagePermissions = permissions?.filter((p) => p[1] === 'page').map((p) => p[2]);
      setIsCanManageTag(pagePermissions?.includes('/tag') || false);
    }
  }, [initialState]);

  return (
    <div className={Styles.KnowledgeManage}>
      <Spin spinning={loading}>
        <div className={Styles.header}>
          <div>
            {knowledgeBase?.name}：{total}条知识
          </div>
          <div>
            {isCanManageTag && (
              <Button type="primary" ghost onClick={toggleLabelManage}>
                标签管理
              </Button>
            )}
          </div>
        </div>
        <div className={Styles.content}>
          <div
            className={Styles.tree}
            style={{
              maxHeight: 'calc(100vh - 56px - 24px - 34px - 32px - 50px - 100px)',
              overflow: 'scroll',
            }}
          >
            <div>目录</div>
            <Tree
              showLine={true}
              showIcon={false}
              expandedKeys={expandKeys}
              onSelect={onSelect}
              treeData={tree}
              onExpand={onExpand}
              selectedKeys={[currentKey]}
            />
          </div>

          <div className={Styles.knowledgeList}>
            <div
              style={{
                width: '100%',
                maxHeight: 'calc(100vh - 56px - 24px - 34px - 32px - 50px - 100px)',
                overflow: 'scroll',
                padding: '10px',
              }}
            >
              <Row gutter={[16, 16]}>
                {knowledgeList.map((item) => {
                  return (
                    <Col span={12} key={item.id}>
                      <KnowledgeItem key={item.id} data={item} tags={tags}></KnowledgeItem>
                    </Col>
                  );
                })}
              </Row>
            </div>
            {knowledgeList.length > 0 && (
              <div className={Styles.paginationWrapper}>
                <Pagination
                  total={pagination.total}
                  showTotal={(total) => `共${pagination.pages}页/${total}条`}
                  defaultPageSize={pagination.size}
                  defaultCurrent={1}
                  showSizeChanger={false}
                  size="small"
                  disabled={loading}
                  onChange={(page) => handleChangePage(page)}
                />
              </div>
            )}
          </div>
        </div>
      </Spin>
    </div>
  );
};

export default App;
