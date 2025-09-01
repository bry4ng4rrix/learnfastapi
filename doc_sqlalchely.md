SQLAlchemy : Types de données et utilisation
SQLAlchemy est une bibliothèque Python puissante qui fournit un ORM (Object-Relational Mapping) et un toolkit SQL pour interagir avec des bases de données relationnelles. Elle permet de mapper des objets Python à des tables de base de données et d'exécuter des requêtes SQL de manière intuitive. Ce document explique les principaux types de données SQLAlchemy et leurs utilisations, avec des exemples inspirés d'une application FastAPI.
1. Types de données SQLAlchemy
SQLAlchemy propose une variété de types de données pour définir les colonnes des tables dans une base de données. Ces types correspondent aux types SQL standards et permettent de spécifier la structure des données stockées.
Types de données courants
Voici une liste des types de données les plus utilisés dans SQLAlchemy, avec leur description et leur correspondance SQL :

Integer : Représente un entier (ex. : id d'une table).
SQL : INTEGER
Exemple : id = Column(Integer, primary_key=True)


String : Représente une chaîne de caractères de longueur fixe ou variable.
SQL : VARCHAR ou TEXT (selon la longueur spécifiée ou la base de données).
Exemple : name = Column(String(50)) (limite à 50 caractères).
Note : Si aucune longueur n'est spécifiée, cela correspond à TEXT dans certaines bases de données comme SQLite.


Text : Représente une chaîne de caractères de longueur illimitée (ou très grande).
SQL : TEXT
Exemple : description = Column(Text)


DateTime : Représente une date et une heure.
SQL : DATETIME ou TIMESTAMP
Exemple : created_at = Column(DateTime, default=datetime.utcnow)
Note : Peut être utilisé avec des valeurs par défaut comme datetime.utcnow pour définir automatiquement la date/heure actuelle.


Date : Représente une date sans heure.
SQL : DATE
Exemple : birth_date = Column(Date)


Boolean : Représente une valeur booléenne (True/False).
SQL : BOOLEAN
Exemple : is_active = Column(Boolean, default=True)


Float : Représente un nombre à virgule flottante.
SQL : FLOAT ou REAL
Exemple : price = Column(Float)


Numeric : Représente un nombre décimal avec une précision définie.
SQL : NUMERIC ou DECIMAL
Exemple : amount = Column(Numeric(precision=10, scale=2)) (10 chiffres, 2 après la virgule).


ForeignKey : Définit une clé étrangère pour lier une table à une autre.
SQL : FOREIGN KEY
Exemple : user_id = Column(Integer, ForeignKey('users.id'))


Enum : Représente un ensemble de valeurs prédéfinies.
SQL : ENUM (supporté par certaines bases de données comme PostgreSQL).
Exemple : status = Column(Enum('active', 'inactive', name='status_enum'))



Types avancés

JSON : Stocke des données au format JSON (supporté par PostgreSQL, MySQL, SQLite).
Exemple : data = Column(JSON)


Array : Stocke des tableaux (principalement pour PostgreSQL).
Exemple : tags = Column(ARRAY(String))


LargeBinary : Stocke des données binaires (ex. : fichiers).
Exemple : file = Column(LargeBinary)



Options des colonnes
Les colonnes peuvent être configurées avec des options supplémentaires :

primary_key=True : Définit la colonne comme clé primaire.
index=True : Crée un index pour accélérer les requêtes.
nullable=True/False : Indique si la colonne peut contenir des valeurs NULL.
default=valeur : Définit une valeur par défaut (ex. : default=datetime.utcnow).
unique=True : Impose une contrainte d'unicité.

Exemple de modèle avec types
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

2. Utilisation de SQLAlchemy
SQLAlchemy est utilisé dans deux contextes principaux : ORM (mappage d'objets Python à des tables) et Core (requêtes SQL directes). Dans le contexte d'une application FastAPI, l'ORM est souvent privilégié pour sa simplicité et son intégration avec Pydantic. Voici les principales utilisations :
a. Configuration de la connexion à la base de données
SQLAlchemy utilise un moteur (engine) pour se connecter à une base de données.
from sqlalchemy import create_engine

SQLALCHEMY_DATABASE_URL = "sqlite:///./items.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})


create_engine : Crée un moteur pour gérer la connexion.
connect_args : Paramètres spécifiques, comme check_same_thread pour SQLite dans un contexte multi-thread (nécessaire pour FastAPI).

b. Définition des modèles
Les modèles SQLAlchemy sont des classes Python qui héritent de declarative_base(). Ils définissent la structure des tables.
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


Base : Classe de base pour tous les modèles.
__tablename__ : Nom de la table dans la base de données.
Colonnes : Définies avec Column et les types appropriés.

c. Création des tables
Les tables sont créées dans la base de données avec Base.metadata.create_all.
Base.metadata.create_all(bind=engine)


Crée toutes les tables définies par les modèles héritant de Base.
Exécuté une seule fois au démarrage de l'application.

d. Gestion des sessions
SQLAlchemy utilise des sessions pour interagir avec la base de données (ajouter, lire, mettre à jour, supprimer).
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


sessionmaker : Crée une usine pour générer des sessions.
get_db : Fournit une session par requête dans FastAPI, fermée automatiquement après usage.

e. Opérations CRUD
SQLAlchemy permet d'effectuer des opérations CRUD (Create, Read, Update, Delete) via l'ORM.
Création
from sqlalchemy.orm import Session

def create_item(db: Session, name: str, description: str | None):
    db_item = Item(name=name, description=description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


db.add : Ajoute l'objet à la session.
db.commit : Valide les changements dans la base de données.
db.refresh : Met à jour l'objet avec les données de la base (ex. : id généré).

Lecture
def get_items(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Item).offset(skip).limit(limit).all()


db.query : Crée une requête sur le modèle Item.
offset/limit : Implémente la pagination.

Mise à jour
def update_item(db: Session, item_id: int, name: str):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item:
        db_item.name = name
        db.commit()
        db.refresh(db_item)
    return db_item


filter : Filtre les enregistrements.
first : Récupère le premier résultat.

Suppression
def delete_item(db: Session, item_id: int):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item


db.delete : Supprime l'objet de la session.

f. Intégration avec FastAPI
SQLAlchemy s'intègre bien avec FastAPI grâce à Pydantic et au système de dépendances.
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

app = FastAPI()

class ItemCreate(BaseModel):
    name: str
    description: str | None = None

@app.post("/items/")
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


Depends(get_db) : Injecte une session pour chaque requête.
Pydantic : Valide les données d'entrée/sortie et se combine avec orm_mode=True pour convertir les objets SQLAlchemy en JSON.

3. Bonnes pratiques

Utilisez orm_mode=True dans Pydantic pour une conversion fluide entre modèles SQLAlchemy et réponses API.
Gérez les sessions proprement avec get_db pour éviter les fuites de ressources.
Ajoutez des index (index=True) sur les colonnes fréquemment recherchées.
Utilisez des migrations (ex. : Alembic) pour gérer les changements de schéma dans une base de données existante.
Préférez datetime.utcnow pour les champs de date afin d'éviter les problèmes de fuseaux horaires.

4. Conclusion
SQLAlchemy est un outil polyvalent pour interagir avec les bases de données. Ses types de données permettent de définir des schémas précis, et son ORM simplifie les opérations CRUD tout en offrant une flexibilité pour des requêtes complexes. Dans une application FastAPI, SQLAlchemy est particulièrement puissant lorsqu'il est combiné avec Pydantic pour valider les données et gérer les réponses API.
Pour plus de détails, consultez la documentation officielle de SQLAlchemy.