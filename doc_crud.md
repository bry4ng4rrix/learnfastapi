Documentation CRUD pour main.py avec FastAPI
Ce document décrit l'implémentation d'un système CRUD (Create, Read, Update, Delete) dans le fichier main.py d'une application FastAPI. L'application gère une entité Item avec les champs id, name, description, et created_at, en utilisant FastAPI pour les endpoints API, SQLAlchemy pour l'interaction avec une base de données SQLite, et Pydantic pour la validation des données.
1. Contexte et dépendances
Le fichier main.py définit les endpoints de l'API pour gérer les items. Il repose sur :

FastAPI : Framework pour créer des API RESTful.
SQLAlchemy : ORM pour interagir avec la base de données SQLite (items.db).
Pydantic : Validation des données d'entrée et de sortie, avec conversion des objets SQLAlchemy en JSON via orm_mode=True.

Dépendances importées
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from schema import Item, ItemCreate
from database import Item as DBItem, get_db


FastAPI, Depends, HTTPException : Gestion des routes, injection de dépendances, et gestion des erreurs HTTP.
Session : Gestion des sessions SQLAlchemy pour les opérations sur la base de données.
List : Type Python pour typer les réponses de l'endpoint GET.
Item, ItemCreate : Modèles Pydantic définis dans schema.py pour valider les données.
DBItem, get_db : Modèle SQLAlchemy (Item renommé DBItem) et fonction pour fournir une session de base de données.

2. Opérations CRUD
Le fichier main.py implémente un CRUD complet pour l'entité Item avec les endpoints suivants :

Create : POST /items/
Read : GET /items/
Update : PUT /items/{item_id}
Delete : DELETE /items/{item_id}

a. Create (POST /items/)
Description : Crée un nouvel item dans la base de données.
Code :
@app.post("/items/", response_model=Item)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = DBItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


Entrée : Corps de la requête validé par ItemCreate (Pydantic) avec name (str, requis) et description (str, optionnel).
Traitement :
Crée un objet DBItem (modèle SQLAlchemy) à partir des données validées (item.dict()).
Ajoute l'objet à la session (db.add).
Valide les changements dans la base de données (db.commit).
Rafraîchit l'objet pour inclure les valeurs générées (ex. : id, created_at) (db.refresh).


Sortie : Retourne l'item créé au format Item (Pydantic), incluant id, name, description, et created_at.
Exemple de requête :POST /items/
{
    "name": "Exemple",
    "description": "Un item de test"
}

Réponse :{
    "id": 1,
    "name": "Exemple",
    "description": "Un item de test",
    "created_at": "2025-09-01T17:39:00Z"
}



b. Read (GET /items/)
Description : Récupère une liste paginée d'items depuis la base de données.
Code :
@app.get("/items/", response_model=List[Item])
def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    items = db.query(DBItem).offset(skip).limit(limit).all()
    return items


Entrée : Paramètres de requête skip (int, défaut 0) et limit (int, défaut 10) pour la pagination.
Traitement :
Exécute une requête SQLAlchemy pour récupérer les items (db.query(DBItem)).
Applique la pagination avec offset (décalage) et limit (nombre maximum d'items).
Récupère tous les résultats avec all().


Sortie : Retourne une liste d'items au format List[Item] (Pydantic), chaque item incluant id, name, description, et created_at.
Exemple de requête :GET /items/?skip=0&limit=10

Réponse :[
    {
        "id": 1,
        "name": "Exemple",
        "description": "Un item de test",
        "created_at": "2025-09-01T17:39:00Z"
    }
]



c. Update (PUT /items/{item_id})
Description : Met à jour un item existant dans la base de données.
Code :
@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item: ItemCreate, db: Session = Depends(get_db)):
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item


Entrée :
item_id : Identifiant de l'item à mettre à jour (dans l'URL).
Corps de la requête validé par ItemCreate (Pydantic) avec name (str, requis) et description (str, optionnel).


Traitement :
Récupère l'item correspondant à item_id avec db.query(DBItem).filter(...).first().
Vérifie si l'item existe, sinon lève une erreur HTTP 404.
Met à jour les champs de l'item (name, description) avec les nouvelles valeurs via setattr.
Valide les changements (db.commit).
Rafraîchit l'objet pour inclure les valeurs à jour (db.refresh).


Sortie : Retourne l'item mis à jour au format Item (Pydantic).
Exemple de requête :PUT /items/1
{
    "name": "Nouvel Exemple",
    "description": "Description mise à jour"
}

Réponse :{
    "id": 1,
    "name": "Nouvel Exemple",
    "description": "Description mise à jour",
    "created_at": "2025-09-01T17:39:00Z"
}



d. Delete (DELETE /items/{item_id})
Description : Supprime un item de la base de données.
Code :
@app.delete("/items/{item_id}", response_model=Item)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return db_item


Entrée : item_id (int) dans l'URL, identifiant l'item à supprimer.
Traitement :
Récupère l'item correspondant à item_id.
Vérifie si l'item existe, sinon lève une erreur HTTP 404.
Supprime l'item de la session (db.delete).
Valide la suppression (db.commit).


Sortie : Retourne l'item supprimé au format Item (Pydantic) pour confirmer l'opération.
Exemple de requête :DELETE /items/1

Réponse :{
    "id": 1,
    "name": "Nouvel Exemple",
    "description": "Description mise à jour",
    "created_at": "2025-09-01T17:39:00Z"
}



3. Intégration avec SQLAlchemy et Pydantic

SQLAlchemy :
Le modèle DBItem (défini dans database.py) représente la table items avec les colonnes id, name, description, et created_at.
La fonction get_db fournit une session SQLAlchemy pour chaque requête, injectée via Depends(get_db).
Les opérations CRUD utilisent db.query(DBItem) pour interagir avec la table.


Pydantic :
ItemCreate valide les données d'entrée pour les endpoints POST et PUT (name, description).
Item définit le format des réponses (inclut id, created_at), avec orm_mode=True pour convertir les objets SQLAlchemy en JSON.


Gestion des erreurs :
Les endpoints PUT et DELETE lèvent une HTTPException (404) si l'item n'existe pas.
Pydantic valide automatiquement les types et les champs requis, réduisant les erreurs de données.



4. Bonnes pratiques

Validation : Utiliser ItemCreate pour limiter les champs modifiables par le client (ex. : created_at est géré par le serveur).
Pagination : Implémentée dans GET avec skip et limit pour des performances optimales.
Gestion des erreurs : Vérifier l'existence des items avant modification ou suppression.
Sessions : Utiliser get_db pour garantir une gestion propre des sessions SQLAlchemy.
Sérialisation : Utiliser orm_mode=True dans schema.py pour une conversion fluide entre SQLAlchemy et JSON.

5. Instructions pour tester

Dépendances :pip install fastapi uvicorn sqlalchemy pydantic


Lancer l'application :uvicorn main:app --reload


Tester les endpoints :
Utilisez l'interface Swagger à http://localhost:8000/docs pour tester les requêtes POST, GET, PUT, et DELETE.
Exemple de séquence :
POST pour créer un item.
GET pour lister les items.
PUT pour modifier un item.
DELETE pour supprimer un item.





6. Conclusion
Le fichier main.py implémente un CRUD complet pour l'entité Item, avec des endpoints RESTful conformes aux standards. L'intégration de FastAPI, SQLAlchemy, et Pydantic garantit une API robuste, avec validation des données, gestion des erreurs, et compatibilité avec une base de données SQLite. Pour des fonctionnalités avancées, envisagez d'ajouter des filtres (ex. : recherche par nom) ou des migrations avec Alembic pour gérer les changements de schéma.
Pour plus de détails, consultez la documentation de FastAPI.