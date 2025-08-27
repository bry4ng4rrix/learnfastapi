from fastapi import FastAPI,Depends 
from fast_jwt import FastJWT 
from datetime import datetime



app = FastAPI()

secret_key = "bgarrixevilg"
fast_jwt = FastJWT(secret_key=secret_key)



@app.get("/")
def test():
    return {"mety"}



@app.post('/login')
def login(LoginRequest: LoginRequest):

    access_token = fast_jwt.creat_access_token(
            user_id=userid, expires_delata=timedelta(minutes=30)
            )

    refresh_token = fast_jwt.create_refresh_token(
            user_id=user_id , expires_delta=timedelta(day=7)
            )
    return {"access_token": access_token , 'refresh_token': refresh_token}




@app.get("/me")
def get_me(user_id: str = Depends(fast_jwt.get_current_user)):
    return {"user_id": user_id}

@app.post("/refresh")
def refresh(new_token: dict = Depends(fast_jwt.refresh_token)):
    return new_token

