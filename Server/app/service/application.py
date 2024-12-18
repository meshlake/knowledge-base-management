from fastapi import HTTPException
from app.service.chatbot import generate_prompt
from app.entities.chatbots import Chatbot
from app.entities.applications import Application
from app.entities.users import User
from sqlalchemy.orm import Session
from app.models.application import ApplicationCreate, ApplicationUpdate
from app.util import generate_api_key
from app.service.user import query_user_by_org

def get_all_applications(db: Session, user: User):
    query = None
    if user.id == 1:
        query = db.query(Application).filter_by(deleted=False)
    else:
        user_ids = query_user_by_org(db, user.organization_id)
        query = db.query(Application).filter(Application.user_id.in_(user_ids)).filter_by(deleted=False)
    return query.order_by(
        Application.createdAt.asc()).all()


def get_application(id: int, db: Session, user: User):
    db_application = db.query(Application).filter_by(
        id=id, deleted=False).first()

    if db_application is None:
        raise HTTPException(
            status_code=404, detail=f"application with id {id} not found")

    return db_application


def create_application(model: ApplicationCreate, db: Session, user: User):
    if model.chatbot_id is not None:
        db_chatbot = db.query(Chatbot).filter_by(
            id=model.chatbot_id, deleted=False).first()
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
    db_application = db.query(Application).filter_by(
        id=id, deleted=False).first()

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
    db_application = db.query(Application).filter_by(
        id=id, deleted=False).first()
    if db_application is None:
        raise HTTPException(
            status_code=404, detail=f"application with id {id} not found")
    db_application.deleted = True
    # db.delete(db_application)
    db.commit()


def get_application_by_api_key(api_key: str, db: Session, user: User):
    db_application = db.query(Application).filter_by(
        api_key=api_key, deleted=False).first()

    if db_application is None:
        raise HTTPException(
            status_code=404, detail=f"application with id {id} not found")

    if db_application.chatbot is not None:
        db_application.chatbot.prompt = generate_prompt(db_application.chatbot)

    return db_application


def get_application_by_bot(db: Session, bot: int | Chatbot) -> Application:
    bot_id = bot.id if isinstance(bot, Chatbot) else bot
    return db.query(Application).filter(Application.chatbot_id == bot_id).first()
