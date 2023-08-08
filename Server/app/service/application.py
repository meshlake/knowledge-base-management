from fastapi import HTTPException
from app.entities.chatbots import Chatbot
from app.entities.applications import Application
from app.entities.users import User
from sqlalchemy.orm import Session
from app.models.application import ApplicationCreate, ApplicationUpdate
from app.util import generate_api_key


def get_all_applications(db: Session, user: User):
    return db.query(Application).order_by(
        Application.createdAt.desc()).all()


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
