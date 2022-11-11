from typing import Union, Optional
from fastapi import Depends, FastAPI, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, OAuth2
from pydantic import BaseModel
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
import uuid

fake_users_db = {
    "john": {
        "username": "john",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

session_cache = {
}

class OAuth2Cookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: str = None,
        scopes: dict = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        session_id: str = request.cookies.get("session_id")
        return session_id

app = FastAPI()

oauth2_scheme = OAuth2Cookie(tokenUrl="token")

class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None

class UserInDB(User):
    hashed_password: str

class Session(BaseModel):
    session_id: str
    username: str

def create_session(user: str):
    #session_id=str(uuid.uuid4())
    session_id=uuid.UUID(str(uuid.uuid4())).hex
    session_cache[session_id]={
        "username": user 
    }
    return session_id
    
def fake_hash_password(password: str):
    return "fakehashed" + password

async def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token in session_cache:
        return None
    username = session_cache[token]["username"]

    if username in fake_users_db:
        user_dict = fake_users_db[username]
        user=User(**user_dict)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
#    if current_user.disabled:
#        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/token")
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    session_id=create_session(user.username)
    #response.set_cookie(key="session_id", value=session_id)
    response.set_cookie(
                  key="session_id",
                  value=session_id,
                  httponly=True,
                  max_age=1800,
                  expires=1800,
    )
    return {"access_token": session_id, "token_type": "bearer"}

@app.get("/logout")
async def logout(response: Response, request: Request):
    session_id: str = request.cookies.get("session_id")
    response.delete_cookie("session_id")
    try:
        del session_cache[session_id]
    except:
        pass
    return {"cookie": "deleted"}

@app.get("/sessions")
async def list_sessions():
    return session_cache

@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
