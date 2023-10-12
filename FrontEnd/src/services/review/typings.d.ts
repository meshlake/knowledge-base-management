declare namespace REVIEW_API {
  type Uploader = {
    id: number;
    nickname: string;
  };

  type KnowledgeBase = {
    id: number;
    name: string;
  };

  type Tag = {
    id: number;
    name: string;
  };

  type SimilarKnowledge = {
    id: number;
    old_knowledge_id: number;
    new_knowledge_id: number;
    old_knowledge: string;
    new_knowledge: string;
    old_knowledge_user: Uploader;
    new_knowledge_user: Uploader;
    old_knowledge_tag: Tag;
    new_knowledge_tag: Tag;
    old_knowledge_structure: 'QA' | 'NORMAL';
    new_knowledge_structure: 'QA' | 'NORMAL';
    status: 'PENDING' | 'PROCESSED';
    knowledge_base: KnowledgeBase;
  };

  type Review = {
    id: number;
    action: 'NEGLECT' | 'REPLACE' | 'FUSION' | 'ADD';
  };
}
