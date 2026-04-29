from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, webhook, chat, cases

app = FastAPI(title="Plataforma de Petições")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(webhook.router)
app.include_router(chat.router)
app.include_router(cases.router)
