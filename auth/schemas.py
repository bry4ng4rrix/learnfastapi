# schemas.py - Modèles Pydantic pour la validation des données
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Modèle de base pour un utilisateur"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)

class UserCreate(UserBase):
    """Modèle pour la création d'un utilisateur"""
    password: str = Field(..., min_length=6, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        """Validation du mot de passe"""
        if len(v) < 6:
            raise ValueError('Le mot de passe doit contenir au moins 6 caractères')
        if not any(c.isdigit() for c in v):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        """Validation du nom d'utilisateur"""
        if not v.isalnum():
            raise ValueError('Le nom d\'utilisateur ne peut contenir que des lettres et chiffres')
        return v.lower()

class UserUpdate(BaseModel):
    """Modèle pour la mise à jour d'un utilisateur"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    is_active: Optional[bool] = None

class User(UserBase):
    """Modèle public d'un utilisateur (sans mot de passe)"""
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserInDB(User):
    """Modèle complet d'un utilisateur (avec mot de passe hashé)"""
    hashed_password: str

# ==================== SCHÉMAS D'AUTHENTIFICATION ====================

class Token(BaseModel):
    """Modèle pour le token d'accès"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # en secondes

class TokenData(BaseModel):
    """Modèle pour les données contenues dans le token"""
    username: Optional[str] = None
    user_id: Optional[int] = None

class LoginRequest(BaseModel):
    """Modèle pour une demande de connexion"""
    username: str
    password: str

class LoginResponse(BaseModel):
    """Modèle pour la réponse de connexion"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: User

# ==================== SCHÉMAS DE RÉPONSE ====================

class MessageResponse(BaseModel):
    """Modèle pour les réponses simples avec message"""
    message: str
    status: str = "success"

class ErrorResponse(BaseModel):
    """Modèle pour les réponses d'erreur"""
    detail: str
    status: str = "error"
    error_code: Optional[str] = None

class UserListResponse(BaseModel):
    """Modèle pour la liste des utilisateurs"""
    users: list[User]
    total: int
    page: int
    per_page: int

# ==================== SCHÉMAS POUR LA VALIDATION ====================

class PasswordChange(BaseModel):
    """Modèle pour le changement de mot de passe"""
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=100)
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Vérification que les mots de passe correspondent"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Les mots de passe ne correspondent pas')
        return v

class PasswordReset(BaseModel):
    """Modèle pour la réinitialisation de mot de passe"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Modèle pour confirmer la réinitialisation de mot de passe"""
    token: str
    new_password: str = Field(..., min_length=6, max_length=100)
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Les mots de passe ne correspondent pas')
        return v

# ==================== SCHÉMAS POUR LES STATISTIQUES ====================

class UserStats(BaseModel):
    """Modèle pour les statistiques utilisateur"""
    total_users: int
    active_users: int
    inactive_users: int
    users_created_today: int
    users_created_this_week: int
    users_created_this_month: int