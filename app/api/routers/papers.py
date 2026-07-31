import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from services.ingest_service import ingest_pdf, list_papers
from services.auth_service import get_current_user
from models import User
from config import UPLOAD_DIR

router = APIRouter(prefix="/papers", tags=["Papers"])


@router.post("/upload")
async def upload_paper(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="only pdf files are supported.")

    paper_name = os.path.splitext(file.filename)[0]
    save_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    chunk_count = ingest_pdf(save_path, paper_name, user_id=current_user.id)

    os.remove(save_path)

    return {
        "message": f"'{paper_name}' ingested successfully.",
        "paper_name": paper_name,
        "chunk_count": chunk_count,
    }


@router.get("/list")
def get_papers(current_user: User = Depends(get_current_user)):
    papers = list_papers(user_id=current_user.id)
    return {"papers": papers, "count": len(papers)}