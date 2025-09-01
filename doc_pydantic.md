Pydantic : Types de données et utilisation
Pydantic est une bibliothèque Python utilisée pour la validation et la sérialisation des données. Dans le contexte d'une application FastAPI, Pydantic est essentiel pour définir des schémas qui valident les données d'entrée et de sortie des API. Ce document explique les types de données Pydantic, leur configuration, et leur utilisation, en s'appuyant sur un exemple inspiré d'une application FastAPI avec un fichier schema.py.
1. Types de données Pydantic
Pydantic utilise les annotations de type Python (introduites dans Python 3.5+) pour définir des modèles de données. Ces types sont validés automatiquement lors de la réception ou de l'envoi de données via une API. Voici les principaux types utilisés dans Pydantic, avec leur correspondance aux types Python standards :
Types de base

str : Chaîne de caractères.
Exemple : name: str
Validation : Vérifie que la valeur est une chaîne (convertit automatiquement si possible, ex. : "123" en str).


int : Entier.
Exemple : id: int
Validation : Rejette les valeurs non entières (ex. : "123.45").


float : Nombre à virgule flottante.
Exemple : price: float


bool : Booléen.
Exemple : is_active: bool
Validation : Accepte True, False, "true", "false", 1, 0, etc.


datetime : Date et heure (du module datetime).
Exemple : created_at: datetime
Validation : Accepte les chaînes ISO 8601 (ex. : "2025-09-01T17:39:00Z") et les objets datetime.


date : Date sans heure.
Exemple : birth_date: date


list : Liste de valeurs.
Exemple : tags: list[str] (liste de chaînes).


dict : Dictionnaire.
Exemple : metadata: dict[str, str] (dictionnaire avec clés et valeurs de type chaîne).



Types optionnels et avancés

Optional[T] ou T | None : Indique qu'une valeur peut être de type T ou None.
Exemple : description: str | None = None
Note : Utilisé pour les champs facultatifs, avec une valeur par défaut de None.


Union[T1, T2] : Permet plusieurs types possibles pour un champ.
Exemple : value: int | str (accepte un entier ou une chaîne).


Literal : Restreint un champ à un ensemble de valeurs littérales.
Exemple : status: Literal["active", "inactive"]


EmailStr : Valide une adresse e-mail.
Exemple : email: EmailStr (nécessite pip install pydantic[email]).


UUID : Valide un identifiant UUID.
Exemple : identifier: UUID



Exemple de modèle Pydantic
Voici un exemple basé sur le fichier schema.py d'une application FastAPI :
from pydantic import BaseModel
from datetime import datetime

class ItemBase(BaseModel):
    name: str
    description: str | None = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


ItemBase : Définit les champs communs (name, description) pour éviter la duplication.
ItemCreate : Hérite de ItemBase pour valider les données d'entrée (POST).
Item : Ajoute id et created_at pour les réponses (GET), avec orm_mode=True pour compatibilité avec SQLAlchemy.

2. Utilisation de Pydantic
Pydantic est utilisé dans FastAPI pour valider les données d'entrée (requêtes HTTP) et de sortie (réponses), ainsi que pour sérialiser les données en JSON. Voici les principales utilisations, avec un focus sur l'intégration avec FastAPI et SQLAlchemy.
a. Définition des schémas
Les modèles Pydantic sont définis en héritant de BaseModel. Les champs sont déclarés avec des annotations de type, et Pydantic valide automatiquement les données.
from pydantic import BaseModel

class ItemBase(BaseModel):
    name: str
    description: str | None = None


Validation : Pydantic vérifie que name est une chaîne et que description est une chaîne ou None.
Valeur par défaut : description=None rend le champ facultatif.

b. Héritage pour réutilisation
Pydantic permet l'héritage pour réutiliser des champs communs, comme dans ItemBase et ItemCreate/Item.
class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    created_at: datetime


ItemCreate : Utilisé pour valider les données envoyées dans une requête POST.
Item : Utilisé pour valider les données renvoyées dans une réponse GET, incluant id et created_at.

c. Configuration avec class Config
La classe Config permet de personnaliser le comportement du modèle.
class Item(ItemBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


orm_mode=True : Permet à Pydantic de lire des objets SQLAlchemy (comme ceux renvoyés par une requête db.query(Item).all()) et de les convertir en modèles Pydantic pour les réponses JSON.
Sans orm_mode, Pydantic ne pourrait pas interpréter les attributs des objets SQLAlchemy.
Note : Dans les versions récentes de Pydantic (v2), cela s'appelle from_attributes=True.



d. Intégration avec FastAPI
Pydantic est utilisé dans FastAPI pour valider les corps des requêtes et les réponses.
Exemple : Endpoint POST
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from schema import Item, ItemCreate
from database import Item as DBItem, get_db

app = FastAPI()

@app.post("/items/", response_model=Item)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = DBItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


item: ItemCreate : Valide le corps de la requête POST (ex. : {"name": "Exemple", "description": null}).
response_model=Item : Garantit que la réponse inclut id et created_at (générés par la base de données).

Exemple : Endpoint GET
from typing import List

@app.get("/items/", response_model=List[Item])
def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    items = db.query(DBItem).offset(skip).limit(limit).all()
    return items


response_model=List[Item] : Valide que la réponse est une liste d'objets conformes au modèle Item.
orm_mode=True : Permet de convertir les objets SQLAlchemy (DBItem) en modèles Pydantic (Item) pour la sérialisation JSON.

e. Validation avancée
Pydantic permet d'ajouter des règles de validation personnalisées avec des décorateurs comme @validator (ou @field_validator dans Pydantic v2).
from pydantic import BaseModel, validator

class ItemBase(BaseModel):
    name: str
    description: str | None = None

    @validator("name")
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v


@validator : Vérifie que name n'est pas une chaîne vide après suppression des espaces.

f. Sérialisation et désérialisation
Pydantic convertit automatiquement les données en JSON (pour les réponses) et valide les données JSON reçues (pour les requêtes).

Entrée : Une requête POST avec {"name": "Exemple", "description": null} est validée par ItemCreate.
Sortie : Un objet SQLAlchemy avec id, name, description, et created_at est converti en JSON conforme au modèle Item.

3. Bonnes pratiques

Utilisez l'héritage pour réutiliser les champs communs (ex. : ItemBase).
Activez orm_mode=True pour intégrer Pydantic avec SQLAlchemy.
Définissez des valeurs par défaut pour les champs optionnels (ex. : description: str | None = None).
Ajoutez des validations personnalisées si nécessaire avec @validator.
Utilisez des types précis (ex. : datetime au lieu de str pour les dates) pour une validation robuste.
Testez les schémas avec l'interface Swagger de FastAPI (/docs) pour vérifier la validation.

4. Exemple complet
Voici un exemple complet basé sur votre application FastAPI :
schema.py
from pydantic import BaseModel
from datetime import datetime

class ItemBase(BaseModel):
    name: str
    description: str | None = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

Utilisation dans FastAPI

POST : Valide les données d'entrée avec ItemCreate et renvoie un Item :POST /items/
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


GET : Retourne une liste de Item :GET /items/
[
    {
        "id": 1,
        "name": "Exemple",
        "description": "Un item de test",
        "created_at": "2025-09-01T17:39:00Z"
    }
]



5. Conclusion
Pydantic est un outil puissant pour valider et sérialiser les données dans une application FastAPI. Ses types de données simples et avancés, combinés à des fonctionnalités comme l'héritage et la validation personnalisée, permettent de créer des API robustes et maintenables. En combinaison avec SQLAlchemy (via orm_mode), Pydantic facilite la conversion entre les modèles de base de données et les réponses JSON.
Pour plus de détails, consultez la documentation officielle de Pydantic.