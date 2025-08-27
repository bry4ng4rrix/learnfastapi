from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date
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

@router.post("/produits/", response_model=schema.Produit)
def create_produit(produit: schema.ProduitCreate, db: Session = Depends(get_db)):
    db_produit = database.Produit(
        nom=produit.nom,
        description=produit.description,
        date=produit.date
    )
    db.add(db_produit)
    db.commit()
    db.refresh(db_produit)
    return db_produit

@router.get("/produits/", response_model=List[schema.Produit])
def read_produits(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    produits = db.query(database.Produit).offset(skip).limit(limit).all()
    return produits

@router.get("/produits/{produit_id}", response_model=schema.Produit)
def read_produit(produit_id: int, db: Session = Depends(get_db)):
    produit = db.query(database.Produit).filter(database.Produit.id == produit_id).first()
    if produit is None:
        raise HTTPException(status_code=404, detail="Produit not found")
    return produit

@router.get("/produits/search/{nom}", response_model=List[schema.Produit])
def search_produits_by_name(nom: str, db: Session = Depends(get_db)):
    produits = db.query(database.Produit).filter(database.Produit.nom.contains(nom)).all()
    if not produits:
        raise HTTPException(status_code=404, detail="No products found with that name")
    return produits

@router.get("/produits/date/{search_date}", response_model=List[schema.Produit])
def get_produits_by_date(search_date: date, db: Session = Depends(get_db)):
    produits = db.query(database.Produit).filter(database.Produit.date == search_date).all()
    if not produits:
        raise HTTPException(status_code=404, detail="No products found for that date")
    return produits

@router.put("/produits/{produit_id}", response_model=schema.Produit)
def update_produit(produit_id: int, produit: schema.ProduitCreate, db: Session = Depends(get_db)):
    db_produit = db.query(database.Produit).filter(database.Produit.id == produit_id).first()
    if db_produit is None:
        raise HTTPException(status_code=404, detail="Produit not found")
    
    db_produit.nom = produit.nom
    db_produit.description = produit.description
    db_produit.date = produit.date
    db.commit()
    db.refresh(db_produit)
    return db_produit

@router.delete("/produits/{produit_id}")
def delete_produit(produit_id: int, db: Session = Depends(get_db)):
    db_produit = db.query(database.Produit).filter(database.Produit.id == produit_id).first()
    if db_produit is None:
        raise HTTPException(status_code=404, detail="Produit not found")
    
    db.delete(db_produit)
    db.commit()
    return {"message": "Produit deleted successfully", "produit_id": produit_id}