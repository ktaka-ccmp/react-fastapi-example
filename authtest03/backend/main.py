from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from auth import auth, user, oauth2google
from customer import customer

from config import settings

app = FastAPI()

app.include_router(
    auth.router,
    prefix="/api",
    tags=["auth"],
)

app.include_router(
    customer.router,
    prefix="/api",
    tags=["customer"],
    dependencies=[Depends(auth.get_current_active_user)],
)

app.include_router(
    user.router,
    prefix="/api",
    tags=["user"],
)

app.include_router(
    oauth2google.router,
    prefix="/api",
    tags=["test"],
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

@app.get("/env/")
async def env():
    print("settings: ", settings)
    return {
        "origin_server": settings.origin_server,
        "google_oauth2_client_id": settings.google_oauth2_client_id,
    }

