import { KnowledgeBaseTagModel } from '@/pages/KnowledgeBase/types';

interface HierarchyTagModel extends KnowledgeBaseTagModel {
  selectable?: boolean;
  children: HierarchyTagModel[];
}
