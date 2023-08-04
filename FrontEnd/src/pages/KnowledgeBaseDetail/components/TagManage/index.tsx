import React, { useEffect } from 'react';
import Styles from './index.less';
import { Skeleton, Tree } from 'antd';
import type { DataNode } from 'antd/es/tree';
import { KnowledgeBaseModel, KnowledgeBaseTagModel } from '@/pages/KnowledgeBase/types';
import { getKnowledgeBaseTags } from '@/services/knowledgeBaseTags';
import ManagableTagItem from '@/components/ManagableTagItem';
import { PlusOutlined } from '@ant-design/icons';

type TagManagerProps = {
  model: KnowledgeBaseModel;
};

interface HierarchyTagModel extends KnowledgeBaseTagModel {
  children: HierarchyTagModel[];
}

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
          children: [],
        });
      }
    }
  });
  return result;
};

export default function TagManager(props: TagManagerProps) {
  const { model } = props;
  const [loading, setLoading] = React.useState<boolean>(true);
  const [tagHierarchyNodes, setTagHierarchyNodes] = React.useState<DataNode[]>([]);

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
          onDeleted={() => setLoading(true)}
          onBlur={onTagBlur}
        />
      ),
      key: tag.id,
    } as DataNode;
  };
  const onSelect = (selectedKeys: React.Key[], info: any) => {
    console.log('selected', selectedKeys, info);
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
    nodes.push(
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
    if (!loading) {
      return;
    }
    getKnowledgeBaseTags(model.id)
      .then((res) => res.items)
      .then((tags) => transformToTagHierarchy(tags))
      .then((tags) => tags.map((tag) => transformToDataNode(tag)))
      .then((nodes) => setTagHierarchyNodes(nodes))
      .finally(() => setLoading(false));
  }, [model, loading]);

  return (
    <>
      <div className={Styles.LabelManager}>
        <div className={Styles.header}>{model.name}</div>
        <div className={Styles.content}>
          <div className={Styles.tree}>
            <div className={Styles.title}>
              <span>标签目录</span>
              <PlusOutlined onClick={() => onTagCreationTriggered()} className={Styles.action} />
            </div>
            <Skeleton loading={loading} />
            {!loading && (
              <Tree
                showLine={true}
                showIcon={false}
                expandAction={false}
                onSelect={onSelect}
                selectable={true}
                treeData={tagHierarchyNodes}
              />
            )}
          </div>
          <div className={Styles.knowledgeList}></div>
        </div>
      </div>
    </>
  );
}
