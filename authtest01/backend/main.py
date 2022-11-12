from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
#from db import Customer, CustomerBase, SessionLocal
from db import Customer, CustomerBase
from db import User, UserBase
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer

#from cookieauthdb import *
import cookieauthdb as auth

app = auth.app
get_db = auth.get_db
get_current_active_user = auth.get_current_active_user

# app = FastAPI()

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# @app.get("/items/")
# async def read_items(token: str = Depends(oauth2_scheme)):
#         return {"token": token}

origins = [
    "http://localhost:3000",
    "http://v200.h.ccmp.jp:4000",
    ]

app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def get_customer(db_session: Session, customer_id: int):
    return db_session.query(Customer).filter(Customer.id==customer_id).first()

# def get_db():
#     db_session = SessionLocal()
#     try:
#         yield db_session
#     finally:
#         db_session.close()

@app.get("/customer/")
def read_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_active_user)):
    return db.query(Customer).offset(skip).limit(limit).all()
        
@app.get("/customer/{customer_id}")
def read_customer(customer_id: int, db_session: Session = Depends(get_db)):
    todo = get_customer(db_session, customer_id)
    return todo

@app.post("/customer/")
def create_customer(customer: CustomerBase, db_session: Session = Depends(get_db)):
    db_customer = Customer(name=customer.name, email=customer.email)
    db_session.add(db_customer)
    db_session.commit()
    db_session.refresh(db_customer)
    return db_customer

@app.delete("/customer/{customer_id}")
async def delete_customer(customer_id: int, db_session: Session = Depends(get_db)):
    todo = get_customer(db_session, customer_id)
    db_session.delete(todo)
    db_session.commit()

def get_user_by_name(db_session: Session, name: str):
    return db_session.query(User).filter(User.name==name).first()

def get_user_by_email(db_session: Session, email: str):
    return db_session.query(User).filter(User.email==email).first()

def get_user_by_id(db_session: Session, user_id: int):
    return db_session.query(User).filter(User.id==user_id).first()

@app.get("/user/")
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()
        
@app.get("/user/{name}")
def read_user_by_name(name: str, db_session: Session = Depends(get_db)):
    user = get_user_by_name(db_session, name)
    return user

@app.post("/user/")
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

@app.delete("/user/{name}")
async def delete_user(name: str, db_session: Session = Depends(get_db)):
    user = get_user_by_name(db_session, name)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username")
    if user:
            db_session.delete(user)
            db_session.commit()

