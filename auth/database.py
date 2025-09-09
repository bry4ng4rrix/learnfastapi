# database.py - Gestion de la base de données SQLite
import sqlite3
from contextlib import contextmanager
from typing import Optional, Dict, Any
from passlib.context import CryptContext

# Configuration
DATABASE_NAME = "auth.db"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db():
    """Initialise la base de données et crée les tables"""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Base de données initialisée")

@contextmanager
def get_db():
    """Context manager pour la connexion à la base de données"""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # Pour accéder aux colonnes par nom
    try:
        yield conn
    finally:
        conn.close()

class UserRepository:
    """Repository pour les opérations CRUD sur les utilisateurs"""
    
    @staticmethod
    def get_by_username(username: str) -> Optional[Dict[str, Any]]:
        """Récupère un utilisateur par username"""
        with get_db() as conn:
            cursor = conn.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            )
            user_data = cursor.fetchone()
            return dict(user_data) if user_data else None
    
    @staticmethod
    def get_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Récupère un utilisateur par email"""
        with get_db() as conn:
            cursor = conn.execute(
                "SELECT * FROM users WHERE email = ?", (email,)
            )
            user_data = cursor.fetchone()
            return dict(user_data) if user_data else None
    
    @staticmethod
    def get_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """Récupère un utilisateur par ID"""
        with get_db() as conn:
            cursor = conn.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            )
            user_data = cursor.fetchone()
            return dict(user_data) if user_data else None
    
    @staticmethod
    def create_user(email: str, username: str, password: str) -> int:
        """Crée un nouvel utilisateur et retourne son ID"""
        hashed_password = pwd_context.hash(password)
        
        with get_db() as conn:
            cursor = conn.execute(
                """INSERT INTO users (email, username, hashed_password) 
                   VALUES (?, ?, ?)""",
                (email, username, hashed_password)
            )
            conn.commit()
            return cursor.lastrowid
    
    @staticmethod
    def update_user_activity(user_id: int, is_active: bool) -> bool:
        """Met à jour le statut d'activité d'un utilisateur"""
        with get_db() as conn:
            cursor = conn.execute(
                "UPDATE users SET is_active = ? WHERE id = ?",
                (is_active, user_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Vérifie si le mot de passe est correct"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def username_exists(username: str) -> bool:
        """Vérifie si un username existe déjà"""
        return UserRepository.get_by_username(username) is not None
    
    @staticmethod
    def email_exists(email: str) -> bool:
        """Vérifie si un email existe déjà"""
        return UserRepository.get_by_email(email) is not None