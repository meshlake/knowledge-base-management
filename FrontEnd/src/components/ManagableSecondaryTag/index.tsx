import React, { MouseEvent, useEffect, useRef } from 'react';
import { Modal } from 'antd';
import { KnowledgeBaseTagModel } from '@/pages/KnowledgeBase/types';
import styles from './index.less';
import {
  CheckOutlined,
  CloseOutlined,
  DeleteOutlined,
  EditOutlined,
  ExclamationCircleOutlined,
  PlusCircleFilled,
} from '@ant-design/icons';
import { deleteKnowledgeBaseTag, persistKnowledgeBaseTag } from '@/services/knowledgeBaseTags';

type ManageableSecondaryTagProps = {
  model: KnowledgeBaseTagModel;
  mode?: 'create' | 'edit' | 'view';
  onCreated?: (model: KnowledgeBaseTagModel) => void;
  onBlurred?: (model: KnowledgeBaseTagModel) => void;
  onDeleted?: (model: KnowledgeBaseTagModel) => void;
  onChanged?: (model: KnowledgeBaseTagModel) => void;
};

const { confirm } = Modal;
export default function ManageableSecondaryTag(props: ManageableSecondaryTagProps) {
  const {
    model: initModel,
    mode: initialMode = initModel.id ? 'view' : 'create',
    onBlurred: tagBlurredCallback,
    onDeleted: tagDeletedCallback,
    onChanged: tagChangedCallback,
    onCreated: tagCreatedCallback,
  } = props;
  const actionRef = useRef<HTMLSpanElement>(null);
  const [model, setModel] = React.useState(initModel);
  const [mode, setMode] = React.useState<'create' | 'edit' | 'view'>(initialMode);

  const onTagEditing = (e?: MouseEvent<HTMLSpanElement>) => {
    if (e) {
      e.stopPropagation();
      e.preventDefault();
    }
    if (mode === 'edit') {
      console.log(`Edit mode already activated, item => ${model.id}`);
      return;
    }
    console.log(`Edit mode activated, item => ${model.id}`);
    setMode('edit');
  };

  const onTagEdited = (e?: MouseEvent<HTMLSpanElement>) => {
    if (e) {
      e.stopPropagation();
      e.preventDefault();
    }
    const modeFlag = model.id ? 'edit' : 'create';
    const toUpdateName = actionRef.current?.innerText?.trim();
    setMode(model.id || toUpdateName ? 'view' : 'create');
    if (toUpdateName && toUpdateName !== model.name) {
      persistKnowledgeBaseTag(model.knowledge_base_id, model.id, {
        name: toUpdateName,
        parent_id: model.parent_id,
      } as KnowledgeBaseTagModel)
        .then((res: KnowledgeBaseTagModel) => {
          setModel({
            ...model,
            id: res.id,
            name: toUpdateName,
          } as KnowledgeBaseTagModel);
        })
        .then(() => console.log(`Tag ${model.name} (${model.id}) updated to ${toUpdateName}`))
        .then(() =>
          modeFlag === 'create' ? tagCreatedCallback?.(model) : tagChangedCallback?.(model),
        )
        .catch((err) => {
          console.error(err);
          if (actionRef.current) {
            actionRef.current.innerText = model.name;
          }
        })
        .finally(() => tagBlurredCallback?.(model));
      return;
    }
    tagBlurredCallback?.(model);
  };

  const onTagEditCancelled = (e?: MouseEvent<HTMLSpanElement>) => {
    if (e) {
      e.stopPropagation();
      e.preventDefault();
    }
    if (actionRef.current) {
      actionRef.current.innerText = model.name;
    }
    setMode(model.id ? 'view' : 'create');
    console.log(`Tag ${model.name} (${model.id}) update cancelled`);
  };

  const onTagDelete = (e: MouseEvent<HTMLSpanElement>) => {
    console.log(`Delete mode activated, item => ${model.id}`);
    e.stopPropagation();
    e.preventDefault();
    confirm({
      icon: <ExclamationCircleOutlined style={{ color: '#F40909' }} />,
      content: `确定删除标签【${model.name}】吗？删除不可恢复。`,
      okText: '确定删除',
      cancelText: '取消',
      onOk() {
        deleteKnowledgeBaseTag(model.knowledge_base_id, model.id)
          .then(() => tagDeletedCallback?.(model))
          .then(() => console.log(`Tag ${model.name} (${model.id}) deleted`));
      },
    });
  };

  const onTagCreating = (e: MouseEvent<HTMLSpanElement>) => {
    e.stopPropagation();
    e.preventDefault();
    setMode('edit');
  };

  useEffect(() => {
    if (mode === 'edit') {
      actionRef.current?.focus();
      const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === 'Enter') {
          onTagEdited();
        } else if (e.key === 'Escape') {
          onTagEditCancelled();
        }
      };
      document.addEventListener('keydown', handleKeyDown);
      return () => document.removeEventListener('keydown', handleKeyDown);
    }
  }, [mode, actionRef]);

  return (
    <div onDoubleClick={() => onTagEditing()} className={styles.TagItem}>
      {mode !== 'create' && (
        <span
          ref={actionRef}
          contentEditable={mode === 'edit'}
          suppressContentEditableWarning={true}
          onBlur={() => onTagEdited()}
          className={mode === 'edit' ? styles.editable : styles.text}
        >
          {model.name}
        </span>
      )}
      {mode === 'view' && (
        <div className={styles.actions}>
          <EditOutlined onClick={() => onTagEditing()} />
          <DeleteOutlined style={{ color: 'red' }} onClick={(e) => onTagDelete(e)} />
        </div>
      )}
      {mode === 'edit' && (
        <div style={{ display: 'flex' }} className={styles.actions}>
          <CheckOutlined onClick={(e) => onTagEdited(e)} style={{ color: 'green' }} />
          <CloseOutlined onClick={(e) => onTagEditCancelled(e)} />
        </div>
      )}
      {mode === 'create' && (
        <div className={styles.create}>
          <PlusCircleFilled onClick={(e) => onTagCreating(e)} />
        </div>
      )}
    </div>
  );
}
