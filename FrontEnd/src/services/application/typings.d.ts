declare namespace Application_API {
  type BaseModel = {
    id: string;
    name: string;
    description: string;
  };

  type ApplicationProperties = {
    webhook_url?: string;
    puppet_token?: string;
    private_enable?: boolean;
    room_enable?: boolean;
  };

  type ApplicationLoginInfo = {
    id?: string;
    name?: string;
    avatar?: string;
    qrcode?: string;
  };

  type Application = {
    id: string;
    category: 'WX_PUBLIC' | 'WX_CHATBOT';
    name: string;
    description: string;
    chatbot: BaseModel;
    properties?: ApplicationProperties;
    login_info?: ApplicationLoginInfo;
    createdAt: string;
    updatedAt: string;
  };

  type ApplicationCreate = Omit<BaseModel, 'id'>;

  type ApplicationUpdate = {
    name?: string;
    description?: string;
    chatbot_id?: string;
    properties?: ApplicationProperties | null;
  };
}
