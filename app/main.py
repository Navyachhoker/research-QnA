import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import papers, qa, analysis, sessions, auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ResearchGPT API", version="1.0.0")

# In production this will be your Vercel URL
# In dev it's * so localhost works
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")


# Allow React frontend (any origin in dev — lock this down in prod)
#* means allow requests from any website
#* allows all methods(put, get, post, delete)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register routers
#registers all the endpoints defined in papers.py
app.include_router(auth.router)
app.include_router(papers.router)
app.include_router(qa.router)
app.include_router(analysis.router) 
app.include_router(sessions.router)  

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "ResearchGPT API is running."
        }
