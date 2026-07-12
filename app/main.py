import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from api.routers import papers, qa, analysis, sessions, auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ResearchGPT API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(papers.router)
app.include_router(qa.router)
app.include_router(analysis.router)
app.include_router(sessions.router)

@app.get("/")
def root():
    return {"status": "ok", "message": "ResearchGPT API is running."}