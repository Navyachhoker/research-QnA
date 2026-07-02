#shutil- it provides functions for copying and moving files

import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from services.ingest_service import ingest_pdf, list_papers
from app.config import UPLOAD_DIR


router = APIRouter(prefix="/papers", tags=["Papers"])

#(...) tells the this parameter is required
#Uploadfile- allows to upload file and work with it
@router.post("/upload")
async def upload_paper(file: UploadFile = file(...)):
    
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail= "only pdf files are supposted.")
    
    #removes file extension
    paper_name = os.path.splitext(file.filename)[0]
    #to create the full path where the uploaded file will be saved
    save_path = os.path.join(UPLOAD_DIR, file.filename)
    
    
    #wb- write, binary mode
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
        
    chunk_count = ingest_pdf(save_path, paper_name)
    
    #after getting chunks , no need for saved pdf
    os.remove(save_path)
    
    return{
         "message":     f"'{paper_name}' ingested successfully.",
        "paper_name":  paper_name,
        "chunk_count": chunk_count,
    }
    
@router.get("/list")
def get_papers():
    papers = list_papers()
    return {"papers": papers, "count": len(papers)}