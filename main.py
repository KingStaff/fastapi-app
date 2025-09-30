from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import User
import uvicorn
import os

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Root endpoint


@app.get("/")
def root():
    return {"message": "I'm alive!"}

# Dependency


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CRUD endpoints


@app.post("/users")
def create_user(name: str, email: str, db: Session = Depends(get_db)):
    user = User(name=name, email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User created successfully", "data": user}


@app.get("/users")
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return {"message": "Users retrieved successfully", "data": users}


@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return {"message": "User retrieved successfully", "data": user}


@app.put("/users/{user_id}")
def update_user(
    user_id: int,
    name: Optional[str] = Body(None),
    email: Optional[str] = Body(None),
    db: Session = Depends(get_db)
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    if name is not None:
        user.name = name
    if email is not None:
        user.email = email

    db.commit()
    db.refresh(user)
    return {"message": "User updated successfully", "data": user}


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
