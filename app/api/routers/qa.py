from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession
from database import get_db
from app.services.retriever_service import retrieve
from app.services.generator_service import generate
from app.services.history_service import add_turn, get_turns, get_session

router = APIRouter(prefix ="/qa", tags= ["Q&A"])

#to validate incoming request
#defines what JSON(API) expects
class AskRequest(BaseModel):
    question: str
    paper: str | None = None #type annotation(str | None)-> paper can be str, or none, and default value would be None
    top_k: int  = 5
    session_id: int | None = None
    
    
@router.post("/ask")
def ask(req: AskRequest, db: DBSession = Depends(get_db)):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # Load past turns for this session (if provided)
    history = []
    if req.session_id:
        session = get_session(db, req.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found.")
        past_turns = get_turns(db, req.session_id)
        # Only pass last 6 turns to stay within token limits
        history = [{"question": t.question, "answer": t.answer} for t in past_turns[-6:]]

    # Retrieve + generate
    chunks = retrieve(req.question, top_k=req.top_k, paper=req.paper)
    result = generate(req.question, chunks, history)

    # Persist this turn
    if req.session_id:
        add_turn(db, req.session_id, req.question, result["answer"])

    return result
