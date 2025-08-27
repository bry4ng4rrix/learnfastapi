from fastapi import FastAPI, Depends
from fast_jwt import FastJWT
from datetime import datetime, timedelta


app = FastAPI()



@app.get('/')
def get():
    return {"kaiza e ": "kaiza e"};