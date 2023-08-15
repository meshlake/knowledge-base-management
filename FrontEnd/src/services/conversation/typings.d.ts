declare namespace Conversation_API {
  type Message = {
    id: string;
    role: string;
    content: string;
    createdAt: number;
    updatedAt: number;
  };

  type Conversation = {
    id: string;
    bot_id: string;
    topic: string;
    description: string;
    messages: Message[];
  };

  type ConversationCteate = {
    bot: string;
    topic: string;
  };

  type MessageCreate = Omit<Message, 'id' | 'createdAt' | 'updatedAt'>;
}
