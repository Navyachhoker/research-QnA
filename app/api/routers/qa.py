from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession
from database import get_db
from app.services.retriever_service import retrieve
from app.services.generator_service import generate
from app.services.history_service import add_turn, get_turns, get_session
from app.models import User
from app.services.auth_service import get_current_user

router = APIRouter(prefix ="/qa", tags= ["Q&A"])

#to validate incoming request
#defines what JSON(API) expects
class AskRequest(BaseModel):
    question: str
    paper: str | None = None #type annotation(str | None)-> paper can be str, or none, and default value would be None
    top_k: int  = 5
    session_id: int | None = None
    
 
@router.post("/ask")
def ask(
    req:          AskRequest,
    db:           DBSession = Depends(get_db),
    current_user: User      = Depends(get_current_user),
):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    history = []
    if req.session_id:
        session = get_session(db, req.session_id)
        if not session or session.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Session not found.")
        past = get_turns(db, req.session_id)
        history = [{"question": t.question, "answer": t.answer} for t in past[-6:]]

    chunks = retrieve(req.question, top_k=req.top_k, paper=req.paper)
    result = generate(req.question, chunks, history)

    if req.session_id:
        add_turn(db, req.session_id, req.question, result["answer"])

    return result