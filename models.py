from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    reg_date = Column(DateTime, default=datetime.utcnow)

    user_answers = relationship('UserAnswer', back_populates='user')
    rating = relationship('Rating', uselist=False, back_populates='user')
    hashed_password = Column(String)

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    main_question = Column(String, nullable=False)
    v1 = Column(String, nullable=False)
    v2 = Column(String, nullable=False)
    v3 = Column(String, nullable=True)
    v4 = Column(String, nullable=True)
    correct_answer = Column(Integer)
    level = Column(String, default='Beginner')
    timer = Column(Integer, default=45)

    answers = relationship("UserAnswer", back_populates="question")


class UserAnswer(Base):
    __tablename__ = 'useranswer'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    question_id = Column(Integer, ForeignKey('questions.id'))
    user_answer = Column(Integer, nullable=False)
    correctness = Column(Boolean, default=False)
    level = Column(String)

    user = relationship("User", back_populates="user_answers")
    question = relationship("Question", back_populates="answers")


class Rating(Base):
    __tablename__ = 'userrating'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    score = Column(Integer, default=0)
    level = Column(String)

    user = relationship('User', back_populates='rating')
