# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from app.api.routers import papers, qa, analysis , sessions, auth  

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ResearchGPT API",
    description="RAG-based research paper Q&A backend",
    version="1.0.0",
)

# Allow React frontend (any origin in dev — lock this down in prod)
#* means allow requests from any website
#* allows all methods(put, get, post, delete)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
