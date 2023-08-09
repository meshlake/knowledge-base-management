import React, { useEffect } from 'react';
import Styles from './index.less';
import { Skeleton, Tree } from 'antd';
import type { DataNode } from 'antd/es/tree';
import { KnowledgeBaseModel, KnowledgeBaseTagModel } from '@/pages/KnowledgeBase/types';
import { getKnowledgeBaseTags } from '@/services/knowledgeBaseTags';
import ManagableTagItem from '@/components/ManagableTagItem';
import { PlusOutlined } from '@ant-design/icons';
import SecondaryTagManager from '../SecondaryTagManage';

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
        } as HierarchyTagModel);
      }
    }
  });
  return result;
};

export default function TagManager(props: TagManagerProps) {
  const { model } = props;
  const [loading, setLoading] = React.useState<boolean>(true);
  const [tags, setTags] = React.useState<HierarchyTagModel[]>([]);
  const [tagHierarchyNodes, setTagHierarchyNodes] = React.useState<DataNode[]>([]);
  const [selectedTag, setSelectedTag] = React.useState<HierarchyTagModel | null>(null);

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
          onCreated={() => setLoading(true)}
          onDeleted={() => setLoading(true)}
          onBlur={onTagBlur}
        />
      ),
      key: tag.id,
    } as DataNode;
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
    setSelectedTag(null);
    getKnowledgeBaseTags(model.id)
      .then((res) => res.items)
      .then((tags) => transformToTagHierarchy(tags))
      .then((tags) => {
        setTags(tags);
        return tags;
      })
      .then((tags) => tags.map((tag) => transformToDataNode(tag)))
      .then((nodes) => setTagHierarchyNodes(nodes))
      .finally(() => setLoading(false));
  }, [model, loading]);

  useEffect(() => {
    if (tagHierarchyNodes.length > 0) {
      onSelect([tagHierarchyNodes[0].key]);
    }
  }, [tagHierarchyNodes]);

  return (
    <>
      <div className={Styles.TagManager}>
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
                selectedKeys={selectedTag ? [selectedTag.id] : []}
                showLine={true}
                showIcon={false}
                expandAction={false}
                onSelect={onSelect}
                selectable={true}
                treeData={tagHierarchyNodes}
              />
            )}
          </div>
          <div style={{ width: '100%' }}>
            {selectedTag ? <SecondaryTagManager model={selectedTag} /> : null}
          </div>
        </div>
      </div>
    </>
  );
}
