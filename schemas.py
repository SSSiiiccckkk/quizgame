from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class UserCreate(BaseModel):
    username: str
    phone_number: str



class UserLogin(BaseModel):
    username: str
    phone_number: str



class QuestionCreate(BaseModel):
    main_question: str
    v1: str
    v2: str
    v3: Optional[str] = None
    v4: Optional[str] = None
    correct_answer: int
    level: Optional[str] = "Beginner"
    timer: Optional[int] = 45

class QuestionOut(BaseModel):
    id: int
    main_question: str
    v1: str
    v2: str
    v3: Optional[str]
    v4: Optional[str]
    level: str
    timer: int

    class Config:
        from_attributes = True


class UserAnswerIn(BaseModel):
    user_id: int
    question_id: int
    user_answer: int



class RatingOut(BaseModel):
    score: int
    level: str

    class Config:
        orm_mode = True
