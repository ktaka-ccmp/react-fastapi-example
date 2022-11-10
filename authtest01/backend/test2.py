from typing import Union, Optional
from fastapi import Depends, FastAPI, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, OAuth2
from pydantic import BaseModel
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
        "session_id": "dufi8o7uoj",
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
        "session_id": "e5drftgyhifi8o7uoj",
    },
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

        print("session_id", session_id)

        return session_id

app = FastAPI()

oauth2_scheme = OAuth2Cookie(tokenUrl="token")

class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None
    session_id: Union[str, None] = None

class UserInDB(User):
    hashed_password: str

def get_user(db, session_id: str):
#    print("session_id", session_id)
    for user in db:
#        print("sid", db[user]["session_id"])
        if db[user]["session_id"] == session_id:
            user_dict = db[user]
            return UserInDB(**user_dict)

def fake_decode_token(token):
    user = get_user(fake_users_db, token)
    print("user", user)
    print("token", token)
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
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
#    hashed_password = fake_hash_password(form_data.password)
#    if not hashed_password == user.hashed_password:
#        raise HTTPException(status_code=400, detail="Incorrect username or password")
    response.set_cookie(key="session_id", value=user.session_id)

    return {"access_token": user.session_id, "token_type": "bearer"}

@app.get("/logout")
async def logout(response: Response):
    response.delete_cookie("session_id")
    return {"cookie": "deleted"}


@app.post("/auth")
async def auth(response: Response, username: str, email: Union[str, None] = None):
    user_dict = fake_users_db.get(username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)

    response.set_cookie(key="fakesession", value="fake-cookie-session-value")

    return {"name": user.username, "email": user.email}


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

