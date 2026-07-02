
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.retriever_service import retrieve
from services.generator_service import generate


router = APIRouter(prefix ="/qa", tags= ["Q&A"])

class AskRequest(BaseModel):
    question: str
    paper: str | None = None
    top_k: int  = 5
    
    
@router.post("/ask")
def ask(req: AskRequest):
    
    if not req.question.strip():
        raise HTTPException(status_code= 400, details= "question cannot be empty")
    
    chunks = retrieve(req.question, top_k = req.top_k, paper =  req.paper)
    result = generate(req.question, chunks)
    
    return result
