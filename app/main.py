import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routers import analysis, auth, papers, qa, sessions
from app.config import settings
from app.db.database import Base, engine, normalize_existing_user_emails

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("researchgpt")

# NOTE: create_all() is fine for this project's current scope (sqlite,
# single-developer / small deployment) but it can't evolve an existing
# schema. If the models change in a way that needs a real migration
# later, switch to Alembic rather than relying on this.
Base.metadata.create_all(bind=engine)

# Fixes existing rows (if any) written before email-case normalization
# existed, so already-registered accounts aren't locked out by the fix
# below. Safe to run on every startup -- a no-op once data is clean.
normalize_existing_user_emails()

app = FastAPI(title="ResearchGPT API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Never let an unexpected exception leak internals (stack traces,
    # file paths, library errors) back to the client as a raw 500.
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


app.include_router(auth.router)
app.include_router(papers.router)
app.include_router(qa.router)
app.include_router(analysis.router)
app.include_router(sessions.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "ResearchGPT API is running."}


@app.get("/health")
def health():
    return {"status": "healthy"}