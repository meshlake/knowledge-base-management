declare namespace KNOWLEDGE_ITEM_API {
  type KnowledgeItemMetadata = {
    knowledge_item_id: number;
    user_id: number;
    tag: number;
    source: string;
    type: 'FILE' | 'MANUALLY';
  };

  type KnowledgeItem = {
    id: number;
    content: string;
    metadata: KnowledgeItemMetadata;
  };

  type KnowledgeItemCreate = {
    content: string;
    tag?: number;
  };

  type KnowledgeItemUpdate = KnowledgeItemCreate & {
    id: number;
  };
}
