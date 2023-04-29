
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from models.database import Base

class User(Base):
    __tablename__ = 'users'
    numero = Column(Integer, primary_key=True)
    name = Column(String(50))
    correo = Column(String(255))
    password = Column(String(50))
    messages_sent = relationship('Message', backref='sender', lazy='dynamic', foreign_keys='Message.sender_id')
    messages_received = relationship('Message', backref='recipient', lazy='dynamic', foreign_keys='Message.recipient_id')

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    content = Column(String(255))
    sender_id = Column(Integer, ForeignKey('users.numero'))
    recipient_id = Column(Integer, ForeignKey('users.numero'))

class UserList(Base):
    __tablename__ = 'user_list'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.numero'))
    user = relationship('User', backref= backref('lists'))
