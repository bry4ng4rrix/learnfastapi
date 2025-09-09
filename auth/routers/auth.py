# auth.py - Module d'authentification OAuth2
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional
import jwt
import os

# Imports locaux
from database import UserRepository
from schemas import (
    User, UserCreate, UserInDB, Token, TokenData, 
    LoginResponse, MessageResponse, ErrorResponse
)

# ==================== CONFIGURATION ====================
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ==================== OAUTH2 SCHEME ====================
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token",
    scopes={
        "read": "Lecture des données utilisateur",
        "write": "Écriture des données utilisateur"
    }
)

# ==================== FONCTIONS UTILITAIRES JWT ====================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crée un token JWT d'accès"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[TokenData]:
    """Vérifie et décode un token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        if username is None:
            return None
            
        return TokenData(username=username, user_id=user_id)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        return None

# ==================== FONCTIONS D'AUTHENTIFICATION ====================
def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """Authentifie un utilisateur avec username/password"""
    user_data = UserRepository.get_by_username(username)
    if not user_data:
        return None
    
    if not UserRepository.verify_password(password, user_data["hashed_password"]):
        return None
    
    return UserInDB(**user_data)

# ==================== DÉPENDANCES (DEPENDS) ====================
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Dépendance OAuth2 : récupère l'utilisateur actuel depuis le token JWT
    Utilisée avec Depends() pour protéger les routes
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Vérification du token
    token_data = verify_token(token)
    if token_data is None or token_data.username is None:
        raise credentials_exception
    
    # Récupération de l'utilisateur depuis la DB
    user_data = UserRepository.get_by_username(token_data.username)
    if user_data is None:
        raise credentials_exception
    
    # Conversion en modèle Pydantic
    return User(**user_data)

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dépendance : vérifie que l'utilisateur actuel est actif
    Utilise get_current_user comme dépendance
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user

async def get_optional_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[User]:
    """
    Dépendance optionnelle : récupère l'utilisateur si connecté, sinon None
    Utile pour les routes qui peuvent être publiques ou privées
    """
    if token is None:
        return None
    
    try:
        return await get_current_user(token)
    except HTTPException:
        return None

# ==================== ROUTER D'AUTHENTIFICATION ====================
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """
    Inscription d'un nouvel utilisateur
    - Vérifie l'unicité du username et email
    - Hash le mot de passe
    - Crée l'utilisateur en base
    """
    # Vérifications d'unicité
    if UserRepository.username_exists(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    if UserRepository.email_exists(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Création de l'utilisateur
    try:
        user_id = UserRepository.create_user(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password
        )
        
        # Récupération des données créées
        user_data_created = UserRepository.get_by_id(user_id)
        return User(**user_data_created)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )

@auth_router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint OAuth2 standard pour obtenir un token d'accès
    Compatible avec OAuth2PasswordRequestForm
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Création du token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@auth_router.post("/login", response_model=LoginResponse)
async def login(username: str, password: str):
    """
    Alternative endpoint de connexion qui retourne plus d'informations
    Retourne le token ET les données utilisateur
    """
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is inactive"
        )
    
    # Création du token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    # Conversion en User (sans hashed_password)
    user_response = User(
        id=user.id,
        email=user.email,
        username=user.username,
        is_active=user.is_active,
        created_at=user.created_at
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response
    )

@auth_router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Route protégée : retourne les informations de l'utilisateur actuel
    Nécessite un token valide
    """
    return current_user

@auth_router.post("/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    Déconnexion (côté serveur, on ne peut pas vraiment invalider le JWT)
    Dans une vraie app, vous pourriez maintenir une blacklist de tokens
    """
    return MessageResponse(
        message=f"User {current_user.username} logged out successfully",
        status="success"
    )

@auth_router.get("/verify-token")
async def verify_user_token(current_user: User = Depends(get_current_user)):
    """
    Vérifie la validité d'un token
    Utile pour les applications frontend
    """
    return {
        "valid": True,
        "user_id": current_user.id,
        "username": current_user.username,
        "is_active": current_user.is_active
    }

# ==================== ROUTES PROTÉGÉES (EXEMPLES) ====================
@auth_router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_active_user)):
    """Exemple de route protégée nécessitant une authentification"""
    return {
        "message": f"Hello {current_user.username}!",
        "user_id": current_user.id,
        "access_level": "authenticated"
    }

@auth_router.get("/admin-only")
async def admin_only_route(current_user: User = Depends(get_current_active_user)):
    """
    Exemple de route admin (vous pourriez ajouter un champ role en DB)
    Pour l'instant, vérifie juste que l'utilisateur est actif
    """
    # Ici vous pourriez vérifier current_user.role == "admin"
    return {
        "message": "This is an admin-only route",
        "admin_user": current_user.username
    }

@auth_router.get("/public-or-private")
async def public_or_private_route(current_user: Optional[User] = Depends(get_optional_current_user)):
    """
    Exemple de route qui peut être publique ou privée
    Comportement différent selon si l'utilisateur est connecté
    """
    if current_user:
        return {
            "message": f"Hello {current_user.username}, you are logged in!",
            "user_type": "authenticated"
        }
    else:
        return {
            "message": "Hello anonymous user!",
            "user_type": "guest"
        }