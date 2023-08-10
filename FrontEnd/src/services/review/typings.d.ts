declare namespace REVIEW_API {
  type Uploader = {
    id: number;
    nickname: string;
  };

  type SimilarKnowledge = {
    id: number;
    old_knowledge_id: number;
    new_knowledge_id: number;
    old_knowledge: string;
    new_knowledge: string;
    old_knowledge_user: Uploader;
    new_knowledge_user: Uploader;
    old_knowledge_tag: number;
    new_knowledge_tag: number;
    status: 'PENDING' | 'PROCESSED';
  };

  type Review = {
    id: number;
    action: 'NEGLECT' | 'REPLACE' | 'FUSION' | 'ADD';
  };
}
