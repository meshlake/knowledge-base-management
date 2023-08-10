import { KnowledgeBaseTagModel } from '@/pages/KnowledgeBase/types';

interface HierarchyTagModel extends KnowledgeBaseTagModel {
  children: HierarchyTagModel[];
}
