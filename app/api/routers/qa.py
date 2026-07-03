
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.retriever_service import retrieve
from app.services.generator_service import generate


router = APIRouter(prefix ="/qa", tags= ["Q&A"])

#to validate incoming request
#defines what JSON(API) expects
class AskRequest(BaseModel):
    question: str
    paper: str | None = None #type annotation(str | None)-> paper can be str, or none, and default value would be None
    top_k: int  = 5
    
    
@router.post("/ask")
def ask(req: AskRequest):
#req is an instance of askRequest
    if not req.question.strip():
        raise HTTPException(status_code= 400, details= "question cannot be empty")
    
    chunks = retrieve(req.question, top_k = req.top_k, paper =  req.paper)
    result = generate(req.question, chunks)
    
    return result
