declare namespace Chatbot_API {
  type BaseModel = {
    id: string;
    name: string;
    description: string;
  };

  type PromptConfig = {
    prompt?: string;
    name?: string;
    role?: string;
    style?: string;
    work?: string;
  };

  type Chatbot = {
    id: string;
    name: string;
    description: string;
    knowledge_bases: BaseModel[];
    prompt_config: PromptConfig;
    createdAt: string;
    updatedAt: string;
  };

  type ChatbotCreate = Omit<BaseModel, 'id'>;

  type ChatbotUpdate = {
    name?: string;
    description?: string;
    knowledge_bases?: string[];
    prompt_config?: PromptConfig;
  };
}
