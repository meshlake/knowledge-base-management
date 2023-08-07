import { KnowledgeBaseTagModel } from '@/pages/KnowledgeBase/types';
import {
  CheckOutlined,
  CloseOutlined,
  DeleteOutlined,
  EditOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import styles from './index.less';
import { useEffect, useRef, useState, MouseEvent } from 'react';
import { Modal } from 'antd';
import { deleteKnowledgeBaseTag, persistKnowledgeBaseTag } from '@/services/knowledgeBaseTags';

const { confirm } = Modal;

type ManagableTagItemProps = {
  model: KnowledgeBaseTagModel;
  editMode?: boolean;
  onEdit?: (active: boolean) => void;
  onChanged?: (model: KnowledgeBaseTagModel) => void;
  onDeleted?: (model: KnowledgeBaseTagModel) => void;
  onBlur?: (model: KnowledgeBaseTagModel) => void;
};

export default function ManagableTagItem(props: ManagableTagItemProps) {
  const {
    model,
    editMode: initialEditMode = false,
    onEdit: editModeChangedCallback,
    onChanged: tagChangedCallback,
    onDeleted: tagDeletedCallback,
    onBlur: tagBlurredCallback,
  } = props;
  const [editMode, setEditMode] = useState<boolean>(initialEditMode);
  const actionRef = useRef<HTMLSpanElement>(null);

  const onTagEditActivated = (e: MouseEvent<HTMLSpanElement>) => {
    e.stopPropagation();
    e.preventDefault();
    setEditMode(true);
  };
  const onTagEditCancelled = (e?: MouseEvent<HTMLSpanElement>) => {
    if (e) {
      e.stopPropagation();
      e.preventDefault();
    }
    if (actionRef.current) {
      actionRef.current.innerText = model.name;
    }
    setEditMode(false);
  };
  const onTagEdited = (e?: MouseEvent<HTMLSpanElement>) => {
    if (e) {
      e.stopPropagation();
      e.preventDefault();
    }
    setEditMode(false);
    if (actionRef.current && actionRef.current.innerText !== model.name) {
      const toUpdateName = actionRef.current.innerText;
      persistKnowledgeBaseTag(model.knowledge_base_id, model.id, {
        name: toUpdateName,
      } as KnowledgeBaseTagModel)
        .then((res: KnowledgeBaseTagModel) => {
          model.name = toUpdateName;
          model.id = res.id;
        })
        .then(() => console.log(`Tag ${model.name} (${model.id}) updated to ${toUpdateName}`))
        .then(() => tagChangedCallback?.(model))
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
  const onTagDeleted = (e: MouseEvent<HTMLSpanElement>) => {
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

  useEffect(() => {
    if (editMode) {
      actionRef?.current?.focus();
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
  }, [editMode, actionRef]);

  useEffect(() => {
    editModeChangedCallback?.(editMode);
  }, [model]);
  return (
    <div className={styles.TagItem} style={{ cursor: editMode ? 'text' : 'pointer' }}>
      <span
        ref={actionRef}
        contentEditable={editMode}
        suppressContentEditableWarning={true}
        onBlur={() => onTagEdited()}
        className={styles.TagTitle}
      >
        {model.name}
      </span>
      <div className={styles.actions} style={editMode ? { display: 'none' } : {}}>
        {' '}
        {/* Tag Actions */}
        <EditOutlined className={styles.TagItemAction} onClick={onTagEditActivated} />
        <DeleteOutlined
          className={styles.TagItemAction}
          onClick={onTagDeleted}
          style={{ color: 'red' }}
        />
      </div>
      <div className={styles.actions} style={{ display: editMode ? 'flex' : 'none' }}>
        {' '}
        {/* Tag Edit Mode Actions */}
        <CheckOutlined
          style={{ color: 'green' }}
          onMouseDown={(e) => e.preventDefault()}
          onClick={(e) => onTagEdited(e)}
          className={styles.TagItemAction}
        />
        <CloseOutlined
          onMouseDown={(e) => e.preventDefault()}
          onClick={(e) => onTagEditCancelled(e)}
          className={styles.TagItemAction}
        />
      </div>
    </div>
  );
}
