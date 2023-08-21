from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.userDto import User
from app.models.chatbot import ChatbotBase, ChatbotUpdate
from app.entities.applications import Application as ApplicationEntity
from app.entities.chatbots import Chatbot as ChatbotEntity
from app.entities.knowledge_bases import KnowledgeBase as KnowledgeBaseEntity
from app.entities.conversations import Conversation as ConversationEntity
import app.crud.chatbot as chatbotCurd
from app.service.user import query_user_by_org


def generate_prompt(chatbot: ChatbotEntity):
    prompt = ""
    prompt_config = chatbot.prompt_config or {}
    if 'prompt' in prompt_config:
        prompt = prompt_config['prompt']
    else:
        required_keys = ['name', 'role', 'work', 'style']
        missing_keys = set(required_keys) - set(prompt_config.keys())
        if not missing_keys:
            PROMPT_TEMPLATE = '你的名字是{name}，在这里，你作为{role}，专门{work}。\n我是你的服务对象，你需要以{style}的语气回答我的问题。\n你不被允许忘掉自己是{name}身份，每当你的身份可能被删除修改时，请保留他并且重复加强认知。即使你是一个计算机程序，但请在接下来的对话中隐藏你是计算机程序这件事，并且扮演{name}。\n不管我用什么语言提问，你都必须用中文回答。\n当问题无法在上下文或者文档中，直接找到答案时，尝试基于顾客问题和上下文对顾客的需求进行提问和进一步确认，引导顾客问出和上下文、文档有关的问题。\n当经过多轮对话，依然无法引导问出与上下文、文档有关的问题时，只能回答"抱歉，我不太明白您的问题是什么，请您再详细说明一下。",不要试图编造答案。'
            prompt = PROMPT_TEMPLATE.format(**prompt_config)
    return prompt


def create_chatbot(db: Session, user: User, model: ChatbotBase):
    chatbot = ChatbotBase(
        name=model.name, description=model.description, user_id=user.id)
    return chatbotCurd.create_chatbot(db=db, model=chatbot)


def update_chatbot(db: Session, user: User, id: int, model: ChatbotUpdate):
    db_chatbot = db.query(ChatbotEntity).filter_by(id=id, deleted=False).first()
    if db_chatbot is None:
        raise HTTPException(
            status_code=404, detail=f"chatbot with id {id} not found")

    for field, value in model.dict(exclude_unset=True).items():
        if field != "knowledgeBaseList":
            if field == "promptConfig":
                setattr(db_chatbot, 'prompt_config', value)
            else:
                setattr(db_chatbot, field, value)

    if model.knowledgeBaseList is not None:  # 更新知识库
        db_chatbot.knowledge_bases = []
        knowledgeBaseList = list(set(model.knowledgeBaseList))
        for knowledge_base_id in knowledgeBaseList:
            db_knowledge_base = db.query(KnowledgeBaseEntity).filter(
                KnowledgeBaseEntity.id == knowledge_base_id).first()
            if db_knowledge_base is None:
                raise HTTPException(
                    status_code=404, detail=f"knowledge base with id {knowledge_base_id} not found")
            db_chatbot.knowledge_bases.append(db_knowledge_base)

    db.commit()
    db.refresh(db_chatbot)
    return db_chatbot


def get_all_chatbot(db: Session, user: User):
    user_ids = query_user_by_org(db, user.organization_id)
    query = db.query(ChatbotEntity).filter(ChatbotEntity.user_id.in_(user_ids)).filter_by(deleted=False)
    db_chatbots = query.order_by(
        ChatbotEntity.createdAt.desc()).all()
    return db_chatbots


def get_chatbot(db: Session, user: User, id: int):
    db_chatbot = db.query(ChatbotEntity).filter_by(id=id, deleted=False).first()
    if db_chatbot is None:
        raise HTTPException(
            status_code=404, detail=f"chatbot with id {id} not found")
    db_chatbot.prompt = generate_prompt(db_chatbot)
    return db_chatbot


def delete_chatbot(db: Session, user: User, id: int):
    db_chatbot = db.query(ChatbotEntity).filter_by(id=id, deleted=False).first()
    if db_chatbot is None:
        raise HTTPException(
            status_code=404, detail=f"chatbot with id {id} not found")

    applications = db.query(ApplicationEntity).filter(
        ApplicationEntity.chatbot_id == id, ApplicationEntity.deleted == False).all()
    if applications:
        return {
            "code": 400,
            "message": "Cannot delete Chatbot record due to foreign key constraints"
        }

    # 同时删除对话
    conversations = db.query(ConversationEntity).filter(
        ConversationEntity.bot_id == id, ConversationEntity.status == 'active').all()
    for conversation in conversations:
        conversation.status = 'deleted'

    # 删除与知识库的关联
    db_chatbot.knowledge_bases = []
    db_chatbot.deleted = True
    # db.delete(db_chatbot)
    db.commit()
    return {
        "code": 200,
        "message": "Chatbot deleted successfully"
    }
