from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import database
import schema

router = APIRouter()

# Dependency pour obtenir la session de base de données
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/users/", response_model=schema.User)
def create_user(user: schema.UserCreate, db: Session = Depends(get_db)):
    # Vérifier si l'email existe déjà
    db_user_check = db.query(database.User).filter(database.User.email == user.email).first()
    if db_user_check:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = database.User(
        nom=user.nom,
        prenom=user.prenom,
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/users/", response_model=List[schema.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(database.User).offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=schema.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(database.User).filter(database.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/users/email/{email}", response_model=schema.User)
def read_user_by_email(email: str, db: Session = Depends(get_db)):
    user = db.query(database.User).filter(database.User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{user_id}", response_model=schema.User)
def update_user(user_id: int, user: schema.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(database.User).filter(database.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Vérifier si le nouvel email existe déjà (sauf si c'est le même utilisateur)
    if user.email != db_user.email:
        email_check = db.query(database.User).filter(database.User.email == user.email).first()
        if email_check:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user.nom = user.nom
    db_user.prenom = user.prenom
    db_user.email = user.email
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(database.User).filter(database.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully", "user_id": user_id}