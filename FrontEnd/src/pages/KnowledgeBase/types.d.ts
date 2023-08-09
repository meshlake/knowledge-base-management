import KnowledgeBase from '../../components/ContentLayout/types.d.ts';

interface KnowledgeBaseModel extends KnowledgeBase.BaseModel {
  description: string;
  userId: int;
}

interface KnowledgeBaseTagModel extends KnowledgeBase.BaseModel {
  knowledge_base_id: int;
  parent_id: int;
  user_id?: int;
  description?: string;
}
