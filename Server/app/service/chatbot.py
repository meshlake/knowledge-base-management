from sqlalchemy.orm import Session
from app.models.userDto import User
from app.models.chatbot import ChatbotBase
import app.crud.chatbot as chatbotCurd


def create_chatbot(db: Session, user: User, model: ChatbotBase):
    chatbot = ChatbotBase(name = model.name, description = model.description, user_id = user.id)
    return chatbotCurd.create_chatbot(db=db, model=chatbot)
