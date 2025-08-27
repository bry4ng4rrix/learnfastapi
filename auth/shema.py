from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

# Schemas pour User
class UserBase(BaseModel):
    nom: str
    prenom: str
    email: EmailStr

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    
    class Config:
        from_attributes = True

# Schemas pour Produit
class ProduitBase(BaseModel):
    nom: str
    description: str
    date: date

class ProduitCreate(ProduitBase):
    pass

class Produit(ProduitBase):
    id: int
    
    class Config:
        from_attributes = True