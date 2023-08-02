declare namespace Chatbot_API {
  type Chatbot = {
    id: string;
    name: string;
    description?: string;
    createdAt?: string;
    updatedAt?: string;
  };

  type ChatbotCreate = Pick<Chatbot, 'name' | 'description'>;
}
