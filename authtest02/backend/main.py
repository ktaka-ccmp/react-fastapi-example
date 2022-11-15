from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from auth import auth, user
from customer import customer

app = FastAPI()
app.include_router(
    auth.router,
    tags=["auth"],
)
app.include_router(
    customer.router,
    tags=["customer"],
    dependencies=[Depends(auth.get_current_active_user)],
)
app.include_router(
    user.router,
    tags=["user"],
)

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

