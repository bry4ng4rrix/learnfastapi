# main.py - Application FastAPI principale
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Imports des modules locaux
from database import init_db
from routers.auth import auth_router

# ==================== APPLICATION ====================
app = FastAPI(
    title="Learn fastapi",
    description="API d'authentification OAuth2 avec FastAPI, SQLite et architecture modulaire",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ==================== MIDDLEWARE ====================
# Configuration CORS pour permettre les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Ajustez selon vos besoins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== INCLUSION DES ROUTERS ====================
# Inclusion du router d'authentification
app.include_router(auth_router)

# ==================== ROUTES PRINCIPALES ====================
@app.get("/")
async def root():
    """Route d'accueil publique"""
    return {
        "message": "Welcome to OAuth2 Authentication API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "auth": "/auth",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Endpoint de vérification de santé de l'API"""
    return {
        "status": "healthy",
        "service": "OAuth2 Authentication API",
        "version": "1.0.0"
    }

# ==================== ÉVÉNEMENTS DE L'APPLICATION ====================
@app.on_event("startup")
async def startup_event():
    # Initialisation de la base de données
    init_db()
   

@app.on_event("shutdown")
async def shutdown_event():
    """Événement exécuté à l'arrêt de l'application"""
    print("🛑 Application arrêtée")

# ==================== LANCEMENT ====================
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Rechargement automatique en développement
        log_level="info"
    )