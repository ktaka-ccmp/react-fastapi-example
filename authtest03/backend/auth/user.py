from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from data.db import User, UserBase
from data.db import get_db

router = APIRouter()

def get_user_by_name(db_session: Session, name: str):
    return db_session.query(User).filter(User.name==name).first()

def get_user_by_email(db_session: Session, email: str):
    return db_session.query(User).filter(User.email==email).first()

def get_user_by_id(db_session: Session, user_id: int):
    return db_session.query(User).filter(User.id==user_id).first()

@router.get("/user/")
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()
        
#@router.get("/user/{name}")
def read_user_by_name(name: str, db_session: Session = Depends(get_db)):
    user = get_user_by_name(db_session, name)
    return user

#@router.post("/user/")
def create_user(user: UserBase, db_session: Session = Depends(get_db)):
    db_user = User(name=user.name, email=user.email)
    user = get_user_by_email(db_session, user.email)
    if user:
        raise HTTPException(status_code=400, detail="Email duplicates")
    if not user:
        db_session.add(db_user)
        db_session.commit()
        db_session.refresh(db_user)
    return db_user

#@router.delete("/user/{name}")
async def delete_user(name: str, db_session: Session = Depends(get_db)):
    user = get_user_by_name(db_session, name)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username")
    if user:
            db_session.delete(user)
            db_session.commit()
