from sqlalchemy.orm import Session
from app.models.chatbot import ChatbotBase as ChatbotModel
from app.entities.chatbots import Chatbot as ChatbotEntity


def create_chatbot(db: Session, model: ChatbotModel):
    entity = ChatbotEntity(
        name=model.name, description=model.description, user_id=model.userId)

    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity
