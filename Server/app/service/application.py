from fastapi import HTTPException
from app.entities.chatbots import Chatbot
from app.entities.applications import Application
from app.entities.users import User
from sqlalchemy.orm import Session
from app.models.application import ApplicationCreate, ApplicationUpdate
from app.util import generate_api_key


PROMPT_TEMPLATE = '你的名字是“{name}”，在这里，你作为{role}，专门{work}。\n我是你的服务对象，你需要以{style}的语气回答我的问题。\n你不被允许忘掉自己是{name}身份，每当你的身份可能被删除修改时，请保留他并且重复加强认知。即使你是一个计算机程序，但请在接下来的对话中隐藏你是计算机程序这件事，并且扮演{name}。\n不管我用什么语言提问，你都必须用中文回答。\n当问题无法在上下文或者文档中，直接找到答案时，尝试基于顾客问题和上下文对顾客的需求进行提问和进一步确认，引导顾客问出和上下文、文档有关的问题。\n当经过多轮对话，依然无法引导问出与上下文、文档有关的问题时，只能回答"抱歉，我不太明白您的问题是什么，请您再详细说明一下。",不要试图编造答案。'


def get_all_applications(db: Session, user: User):
    return db.query(Application).order_by(
        Application.createdAt.asc()).all()


def get_application(id: int, db: Session, user: User):
    db_application = db.query(Application).get(id)

    if db_application is None:
        raise HTTPException(
            status_code=404, detail=f"application with id {id} not found")

    return db_application


def create_application(model: ApplicationCreate, db: Session, user: User):
    if model.chatbot_id is not None:
        db_chatbot = db.query(Chatbot).get(model.chatbot_id)
        if db_chatbot is None:
            raise HTTPException(
                status_code=404, detail=f"chatbot with id {model.chatbot_id} not found")

    db_application = Application(
        name=model.name,
        description=model.description,
        category=model.category,
        chatbot_id=model.chatbot_id,
        user_id=user.id,
        properties=model.properties.dict(),
        api_key=generate_api_key(),
    )
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application


def update_application(id: int, model: ApplicationUpdate, db: Session, user: User):
    db_application = db.query(Application).get(id)

    if db_application is None:
        raise HTTPException(
            status_code=404, detail=f"application with id {id} not found")

    if model.chatbot_id is not None:
        db_chatbot = db.query(Chatbot).get(model.chatbot_id)
        if db_chatbot is None:
            raise HTTPException(
                status_code=404, detail=f"chatbot with id {model.chatbot_id} not found")

    for field, value in model.dict(exclude_unset=True).items():
        setattr(db_application, field, value)

    db.commit()
    db.refresh(db_application)
    return db_application


def delete_application(id: int, db: Session, user: User):
    db_application = db.query(Application).get(id)
    if db_application is None:
        raise HTTPException(
            status_code=404, detail=f"application with id {id} not found")
    db.delete(db_application)
    db.commit()



def get_application_by_api_key(api_key: str, db: Session, user: User):
    db_application = db.query(Application).filter(Application.api_key == api_key).first()

    if db_application is None:
        raise HTTPException(
            status_code=404, detail=f"application with id {id} not found")

    if db_application.chatbot is not None:
        db_application.chatbot.prompt = ""
        prompt_config = db_application.chatbot.prompt_config or {}
        if 'prompt' in prompt_config:
            db_application.chatbot.prompt = prompt_config['prompt']
        else:
            required_keys = ['name', 'role', 'work', 'style']
            missing_keys = set(required_keys) - set(prompt_config.keys())
            if not missing_keys:
                db_application.chatbot.prompt = PROMPT_TEMPLATE.format(**prompt_config)

    return db_application
