import uuid
from sqlalchemy import Column, DateTime, String, Integer, Boolean, Float, Text, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.connection import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String, index=True)
    role = Column(String)
    content = Column(String)