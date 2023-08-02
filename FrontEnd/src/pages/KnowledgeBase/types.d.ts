import KnowledgeBase from '../../components/ContentLayout/types.d.ts';

interface KnowledgeBaseModel extends KnowledgeBase.BaseModel {
  description: string;
  userId: int;
  createdAt?: int;
  updatedAt?: int;
}
