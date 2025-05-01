from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas
from typing import List

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Регистрация пользователя

@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.phone_number == user.phone_number).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким номером телефона уже существует")

    new_user = models.User(username=user.username, phone_number=user.phone_number)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Пользователь успешно зарегистрирован"}


# Вход пользователя

@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.phone_number == user.phone_number).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Неверный номер телефона")

    return {"message": "Успешный вход"}


# Получить список вопросов

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

    # Проверка правильности ответа
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

    # Обновление рейтинга пользователя
    rating = db.query(models.Rating).filter(models.Rating.user_id == answer.user_id).first()
    if not rating:
        rating = models.Rating(user_id=answer.user_id, score=0)
        db.add(rating)

    if is_correct:
        rating.score += 1
    db.commit()

    return {"correct": is_correct}


# Получение рейтинга пользователя

@app.get("/rating/{user_id}", response_model=schemas.RatingOut)
def get_rating(user_id: int, db: Session = Depends(get_db)):
    rating = db.query(models.Rating).filter(models.Rating.user_id == user_id).first()
    if not rating:
        raise HTTPException(status_code=404, detail="Рейтинг не найден")

    return {"score": rating.score, "level": rating.level}
