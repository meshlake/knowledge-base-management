declare namespace KNOWLEDGE_ITEM_API {
  type KnowledgeItemMetadata = {
    knowledge_item_id: int;
    user_id: int;
    tags?: string[];
    source: string;
    type: 'FILE' | 'MANUALLY';
  };

  type KnowledgeItem = {
    id: int;
    content: string;
    metadata: KnowledgeItemMetadata;
  };

  type KnowledgeItemCreate = {
    content: string;
    tags?: string[];
  };

  type KnowledgeItemUpdate = KnowledgeItemCreate & {
    id: int;
  };
}
