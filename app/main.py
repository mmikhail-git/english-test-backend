from fastapi import FastAPI
from app.routers import auth, words, tests, collections
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

logger.add("info.log")

app = FastAPI(root_path="/api")



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(words.router)
app.include_router(tests.router)
app.include_router(collections.router)
