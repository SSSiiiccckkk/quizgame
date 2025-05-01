from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas
from typing import List
from auth import hash_password, check_password
from pydantic import BaseModel
from models import User
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError



models.Base.metadata.create_all(bind=engine)
app = FastAPI()
ph = PasswordHasher()



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    phone_number: str
    password: str


def hashed_password(password: str):
    return ph.hash(password)


def checked_password(hashed_password: str, password: str):
    try:
        return ph.verify(hashed_password, password)
    except VerifyMismatchError:
        return False



@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.phone_number == user.phone_number).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким номером телефона уже существует")

    hashed_password = hash_password(user.password)


    new_user = models.User(username=user.username, phone_number=user.phone_number,
                           hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Пользователь успешно зарегистрирован"}


@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.phone_number == user.phone_number).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Неверный номер телефона")


    if not check_password(db_user.hashed_password, user.password):
        raise HTTPException(status_code=400, detail="Неверный номер телефона или пароль")

    return {"message": "Вход успешно произведен!"}

@app.post("/questions")
def create_question(q: schemas.QuestionCreate, db: Session = Depends(get_db)):
    question = models.Question(**q.dict())
    db.add(question)
    db.commit()
    db.refresh(question)
    return {"message": "Вопрос добавлен", "id": question.id}


# Ответ на вопрос

@app.post("/answer")
def answer_question(answer: schemas.UserAnswerIn, db: Session = Depends(get_db)):
    question = db.query(models.Question).filter(models.Question.id == answer.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Вопрос не найден")

    is_correct = answer.user_answer == question.correct_answer

    user_answer = models.UserAnswer(
        user_id=answer.user_id,
        question_id=answer.question_id,
        user_answer=answer.user_answer,
        correctness=is_correct,
        level=question.level
    )
    db.add(user_answer)
    db.commit()

    rating = db.query(models.Rating).filter(models.Rating.user_id == answer.user_id).first()
    if not rating:
        rating = models.Rating(user_id=answer.user_id, score=0)
        db.add(rating)

    if is_correct:
        rating.score += 1
    db.commit()

    return {"correct": is_correct}




@app.get("/rating/{user_id}", response_model=schemas.RatingOut)
def get_rating(user_id: int, db: Session = Depends(get_db)):
    rating = db.query(models.Rating).filter(models.Rating.user_id == user_id).first()
    if not rating:
        raise HTTPException(status_code=404, detail="Рейтинг не найден")

    return {"score": rating.score, "level": rating.level}
