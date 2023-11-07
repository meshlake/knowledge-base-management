import React, { useEffect, useState } from 'react';
import Styles from './index.less';
import { Spin, Tree } from 'antd';
import type { DataNode } from 'antd/es/tree';
import { KnowledgeBaseModel, KnowledgeBaseTagModel } from '@/pages/KnowledgeBase/types';
import { HierarchyTagModel } from '@/pages/KnowledgeBaseDetail/types';
import { getKnowledgeBaseNoParentTags } from '@/services/knowledgeBaseTags';
import ManagableTagItem from '@/components/ManagableTagItem';
import { PlusOutlined } from '@ant-design/icons';
import SecondaryTagManager from '../SecondaryTagManage';
import InfiniteScroll from 'react-infinite-scroll-component';

type TagManagerProps = {
  model: KnowledgeBaseModel;
};

const transformToTagHierarchy = (tags: KnowledgeBaseTagModel[]): HierarchyTagModel[] => {
  const result: HierarchyTagModel[] = [];
  const tagMap: Map<string, HierarchyTagModel> = new Map<string, HierarchyTagModel>();
  tags.forEach((tag) => {
    if (tag.parent_id === null || tag.parent_id <= 0) {
      const hierarchyTag: HierarchyTagModel = {
        ...tag,
        children: [],
      };
      result.push(hierarchyTag);
      tagMap.set(tag.id, hierarchyTag);
    } else {
      const parentTag = tagMap.get(tag.parent_id);
      if (parentTag) {
        parentTag.children.push({
          ...tag,
          key: tag.id,
          children: [],
        } as HierarchyTagModel);
      }
    }
  });
  return result;
};

export default function TagManager(props: TagManagerProps) {
  const { model } = props;
  const [loading, setLoading] = useState<boolean>(false);
  const [needRefresh, setNeedRefresh] = useState<boolean>(false);
  const [tags, setTags] = useState<HierarchyTagModel[]>([]);
  const [tagHierarchyNodes, setTagHierarchyNodes] = useState<DataNode[]>([]);
  const [selectedTag, setSelectedTag] = useState<HierarchyTagModel | null>(null);
  const [page, setPage] = useState(1);
  const [totalPage, setTotalPage] = useState(1);

  const transformToDataNode = (tag: HierarchyTagModel, editMode?: boolean): DataNode => {
    const onTagBlur = (tag: KnowledgeBaseTagModel) => {
      if (tag.id === 0 && tag.name === '') {
        // Cancel creation
        const nodes = [];
        for (let i = 0; i < tagHierarchyNodes.length; i++) {
          if (tagHierarchyNodes[i].key !== 0) {
            nodes.push(tagHierarchyNodes[i]);
          }
        }
        setTagHierarchyNodes(nodes);
      }
    };
    return {
      title: (
        <ManagableTagItem
          model={tag}
          editMode={editMode}
          onCreated={() => {
            setNeedRefresh(true);
          }}
          onDeleted={() => {
            setNeedRefresh(true);
          }}
          onBlur={onTagBlur}
        />
      ),
      key: tag.id,
    } as DataNode;
  };

  const loadMoreData = async (currentPage: number) => {
    if (loading) {
      return;
    }
    setLoading(true);
    try {
      const result = await getKnowledgeBaseNoParentTags(model.id, currentPage + 1, 50);

      if (result) {
        const oldList = currentPage === 0 ? [] : tagHierarchyNodes;

        const newTagHierarchy = transformToTagHierarchy(result.items);
        setTags([...tags, ...newTagHierarchy]);
        const newTagNodes = newTagHierarchy.map((tag) => transformToDataNode(tag));

        setTagHierarchyNodes([...oldList, ...newTagNodes]);
        setPage(result.page);
        setTotalPage(result.pages);
      }
      setLoading(false);
    } catch (error: any) {
      console.log(error.message);
      setLoading(false);
    }
  };

  const onSelect = (selectedKeys: React.Key[]) => {
    if (selectedKeys.length === 0) {
      console.debug('Ignoring unselect event');
      return;
    }
    const selectedNode = tags.find((node) => node.id === (selectedKeys?.[0] as number));
    if (selectedNode) {
      setSelectedTag(selectedNode);
    }
  };

  const onTagCreationTriggered = () => {
    if (
      tagHierarchyNodes.length > 0 &&
      tagHierarchyNodes.findIndex((node) => node.key === 0) >= 0
    ) {
      // Already in creation mode
      console.log('Already in creation mode');
      return;
    }
    const nodes = [...tagHierarchyNodes];
    nodes.unshift(
      transformToDataNode(
        {
          id: 0,
          name: '',
          knowledge_base_id: model.id,
          parent_id: 0,
          children: [],
        },
        true,
      ),
    );
    setTagHierarchyNodes(nodes);
  };

  useEffect(() => {
    setSelectedTag(null);
    setPage(0);
    setTotalPage(0);
    loadMoreData(0);
  }, [model.id]);

  useEffect(() => {
    if (needRefresh) {
      setNeedRefresh(false);
      setSelectedTag(null);
      setPage(0);
      setTotalPage(0);
      loadMoreData(0);
    }
  }, [needRefresh]);

  useEffect(() => {
    if (tagHierarchyNodes.length > 0) {
      onSelect([tagHierarchyNodes[0].key]);
    }
  }, [tagHierarchyNodes]);

  return (
    <div>
      <div className={Styles.TagManager}>
        <div className={Styles.header}>{model.name}</div>
        <div className={Styles.content}>
          <div className={Styles.tree}>
            <div className={Styles.title}>
              <span>标签目录</span>
              <PlusOutlined onClick={() => onTagCreationTriggered()} className={Styles.action} />
            </div>

            <div id="scrollableTree" style={{ overflow: 'auto' }}>
              <Spin spinning={loading}>
                <InfiniteScroll
                  dataLength={tagHierarchyNodes.length}
                  next={() => {
                    loadMoreData(page);
                  }}
                  hasMore={page < totalPage}
                  loader={null}
                  scrollableTarget="scrollableTree"
                >
                  <Tree
                    selectedKeys={selectedTag ? [selectedTag.id] : []}
                    showLine={true}
                    showIcon={false}
                    expandAction={false}
                    onSelect={onSelect}
                    selectable={true}
                    treeData={tagHierarchyNodes}
                    style={{ overflow: 'auto' }}
                  />
                </InfiniteScroll>
              </Spin>
            </div>
          </div>
          <div id="scrollableDiv" style={{ width: '100%', overflow: 'scroll' }}>
            {selectedTag ? <SecondaryTagManager model={selectedTag} /> : null}
          </div>
        </div>
      </div>
    </div>
  );
}
