import json
from google.oauth2 import id_token
from google.auth.transport import requests

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from data.db import User

from config import settings

from data.db import get_db
from auth.user import get_user_by_name

async def VerifyToken(body: str):
    buf=json.loads(body)
    print("buf: ", buf)
    if buf == None:
        return None
    token=buf["credential"]

    print("token: ", token)
    print("origin_server: ", settings.origin_server)
    print("google_oauth2_client_id: ", settings.google_oauth2_client_id)

    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.google_oauth2_client_id)
    except ValueError:
        return None

    print("idinfo: ", idinfo)
    return idinfo

async def authenticate(body: str, db_session: Session):
    idinfo = await VerifyToken(body)
    if not idinfo:
        return None

    user = None
    username = idinfo['email']
    print("username: ", username)

    user = get_user_by_name(db_session, username)

    if user:
        return user
    if not user:
        db_user = User(name=username, email=username)
        db_session.add(db_user)
        db_session.commit()
        db_session.refresh(db_user)
        return db_user

router = APIRouter()

@router.get("/env/")
async def env():
    print("settings: ", settings)
    return {
        "origin_server": settings.origin_server,
        "google_oauth2_client_id": settings.google_oauth2_client_id,
    }

