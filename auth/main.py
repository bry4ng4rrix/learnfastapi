from fastapi import FastAPI
import database
from routers import auth,user,produit 


database.Base.metadata.create_all(database.engine)

app = FastAPI(title = "Learning FastAPI",
              version="1.0.0")

app.include_router(auth.router ,prefix="/auth",tags=["Authentication"])
app.include_router(user.router, prefix="/user",tags=["User"])
app.include_router(produit.router, prefix="/produit",tags=["Produit"])


@app.get("/")
def root():
    return {"message": "Welcome to FastAPI"}